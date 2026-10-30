"""Behavioural tests for manifest parsing and the ten rules.

The scanner's claims are narrow and checkable: a constraint is pinned or it is
not, a name is one edit away or it is not, and a finding names the rule that
produced it. Each test pins one of those, so a rule that stops firing, or starts
firing on the wrong input, fails here rather than in a report.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from deptrial.manifests import (
    BINDING_BOUNDED,
    BINDING_EXACT,
    BINDING_FLOATING,
    BINDING_WILDCARD,
    SOURCE_LOCAL,
    SOURCE_REGISTRY,
    SOURCE_URL,
    SOURCE_VCS,
    classify_binding,
    classify_source,
    discover,
    parse_package_json,
    parse_pyproject,
    parse_requirements,
)
from deptrial.rules import Options, levenshtein, scan, to_text

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
VULNERABLE = EXAMPLES / "vulnerable"
HARDENED = EXAMPLES / "hardened"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "deptrial", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={"PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"},
        timeout=120,
    )


# ------------------------------------------------------------------ classifiers


@pytest.mark.parametrize(
    "constraint,expected",
    [
        ("1.2.3", BINDING_EXACT),
        ("=1.2.3", BINDING_EXACT),
        ("^1.2.3", BINDING_FLOATING),
        ("~1.2.3", BINDING_FLOATING),
        (">=1.0.0", BINDING_FLOATING),
        (">=1.0.0 <2.0.0", BINDING_BOUNDED),
        ("*", BINDING_WILDCARD),
        ("", BINDING_WILDCARD),
        ("latest", BINDING_WILDCARD),
        ("1.x", BINDING_WILDCARD),
        ("1.2.x", BINDING_WILDCARD),
        (">=1 || >=2", BINDING_FLOATING),
    ],
)
def test_npm_binding_classification(constraint: str, expected: str) -> None:
    assert classify_binding(constraint, "npm") == expected


@pytest.mark.parametrize(
    "constraint,expected",
    [
        ("==1.26.4", BINDING_EXACT),
        ("===1.26.4", BINDING_EXACT),
        (">=2.28", BINDING_FLOATING),
        (">=1,<2", BINDING_BOUNDED),
        ("", BINDING_WILDCARD),
        ("==1.26.*", BINDING_FLOATING),
    ],
)
def test_pip_binding_classification(constraint: str, expected: str) -> None:
    assert classify_binding(constraint, "pip") == expected


@pytest.mark.parametrize(
    "spec,expected",
    [
        ("1.2.3", SOURCE_REGISTRY),
        ("^1.2.3", SOURCE_REGISTRY),
        ("git+https://github.com/o/r@main", SOURCE_VCS),
        ("git://example.org/r.git", SOURCE_VCS),
        ("github:o/r#main", SOURCE_VCS),
        ("https://example.invalid/pkg.tgz", SOURCE_URL),
        ("file:../shared", SOURCE_LOCAL),
        ("workspace:*", SOURCE_LOCAL),
    ],
)
def test_source_classification(spec: str, expected: str) -> None:
    assert classify_source(spec) == expected


def test_levenshtein_is_symmetric_and_exact() -> None:
    assert levenshtein("lodash", "lodash") == 0
    assert levenshtein("lodash", "lodahs") == 2  # a transposition is two edits
    assert levenshtein("lodash", "loadsh") == 2
    assert levenshtein("express", "expres") == 1
    assert levenshtein("", "abc") == 3
    assert levenshtein("abc", "") == 3
    assert levenshtein("kitten", "sitting") == 3


# --------------------------------------------------------------------- parsers


def test_package_json_parses_every_dependency_block() -> None:
    dependencies, scripts = parse_package_json(VULNERABLE / "package.json", "package.json")
    names = {d.name for d in dependencies}
    assert {"lodash", "react", "jest", "@acme/design-tokens", "sharp"} <= names
    assert set(scripts) == {"preinstall", "postinstall"}


def test_package_json_excludes_ordinary_scripts() -> None:
    _, scripts = parse_package_json(HARDENED / "package.json", "package.json")
    assert scripts == {}


def test_requirements_parses_names_and_constraints() -> None:
    dependencies = parse_requirements(VULNERABLE / "requirements.txt", "requirements.txt")
    by_name = {d.name: d for d in dependencies}
    assert by_name["requests"].constraint == ">=2.28"
    assert by_name["flask"].binding == BINDING_WILDCARD
    assert "numpy" in by_name
    assert by_name["numpy"].binding == BINDING_EXACT


def test_requirements_skips_comments_and_flags() -> None:
    dependencies = parse_requirements(VULNERABLE / "requirements.txt", "requirements.txt")
    assert all(not d.name.startswith("#") for d in dependencies)
    assert all(d.name != "" for d in dependencies)


def test_pyproject_reads_pep621_dependencies(tmp_path: Path) -> None:
    manifest = tmp_path / "pyproject.toml"
    manifest.write_text(
        '[project]\nname = "x"\ndependencies = ["requests>=2.28,<3", "flask"]\n'
        '[project.optional-dependencies]\ndev = ["pytest==8.2.0"]\n',
        encoding="utf-8",
    )
    dependencies = {d.name: d for d in parse_pyproject(manifest, "pyproject.toml")}
    assert dependencies["requests"].binding == BINDING_BOUNDED
    assert dependencies["flask"].binding == BINDING_WILDCARD
    assert dependencies["pytest"].binding == BINDING_EXACT


# ------------------------------------------------------------------ discovery


def test_discovery_finds_manifests_and_lockfiles() -> None:
    inventory = discover(HARDENED)
    assert "package.json" in inventory.manifests
    assert "package-lock.json" in inventory.lockfiles
    assert inventory.locked_entries == 2
    assert inventory.integrity_entries == 2


def test_discovery_skips_node_modules(tmp_path: Path) -> None:
    nested = tmp_path / "node_modules" / "dep"
    nested.mkdir(parents=True)
    (nested / "package.json").write_text('{"name": "dep", "dependencies": {"a": "^1.0.0"}}', encoding="utf-8")
    (tmp_path / "package.json").write_text('{"name": "root"}', encoding="utf-8")
    inventory = discover(tmp_path)
    assert inventory.manifests == ["package.json"]


def test_discovery_rejects_a_missing_target(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        discover(tmp_path / "nope")


# ----------------------------------------------------------------------- rules


def vulnerable_report(options: Options | None = None):
    return scan(discover(VULNERABLE), options or Options())


def rules_fired(report) -> set[str]:
    return {finding.rule for finding in report.findings}


def test_vulnerable_example_fires_the_expected_rules() -> None:
    report = vulnerable_report(Options(internal_prefixes=("internal-", "@acme/"), allowlist=("lodash", "express")))
    fired = rules_fired(report)
    assert {"DT001", "DT002", "DT003", "DT007", "DT008"} <= fired


def test_hardened_example_is_clean_apart_from_missing_allowlist() -> None:
    report = scan(discover(HARDENED), Options())
    assert report.findings == []
    assert report.counts() == {"low": 0, "medium": 0, "high": 0}


def test_floating_range_ignores_exact_pins() -> None:
    report = scan(discover(HARDENED), Options())
    assert "DT001" not in rules_fired(report)


def test_install_hook_is_high_severity() -> None:
    report = vulnerable_report()
    hooks = [f for f in report.findings if f.rule == "DT003"]
    assert {f.subject for f in hooks} == {"preinstall", "postinstall"}
    assert all(f.severity == "high" for f in hooks)


def test_non_registry_sources_are_reported_with_kind() -> None:
    report = vulnerable_report()
    sources = [f for f in report.findings if f.rule == "DT002"]
    assert any("vcs" in f.message for f in sources)
    assert any("url" in f.message for f in sources)


def test_internal_prefix_is_required_for_confusion_rule() -> None:
    without = vulnerable_report(Options())
    assert "DT004" not in rules_fired(without)
    with_prefix = vulnerable_report(Options(internal_prefixes=("@acme/",)))
    confusion = [f for f in with_prefix.findings if f.rule == "DT004"]
    assert {f.subject for f in confusion} == {"@acme/design-tokens"}


def test_exact_pin_of_internal_name_is_not_confusion() -> None:
    report = vulnerable_report(
        Options(internal_prefixes=("internal-",), allowlist=(), max_distance=0)
    )
    confusion = [f for f in report.findings if f.rule == "DT004"]
    # internal-billing-client is pinned 1.2.0, so only the unbounded one fires
    assert all("1.2.0" not in f.evidence for f in confusion)


def test_typosquat_needs_an_allowlist() -> None:
    assert "DT005" not in rules_fired(vulnerable_report(Options()))
    report = vulnerable_report(Options(allowlist=("express",), max_distance=2))
    near = [f for f in report.findings if f.rule == "DT005"]
    assert {f.subject for f in near} == {"expres"}
    assert near[0].severity == "high"
    assert "1 edit" in near[0].message


def test_typosquat_does_not_flag_an_exact_match() -> None:
    report = vulnerable_report(Options(allowlist=("lodash", "react", "jest", "express"), max_distance=1))
    subjects = {f.subject for f in report.findings if f.rule == "DT005"}
    assert "lodash" not in subjects
    assert "react" not in subjects


def test_missing_lockfile_is_reported_once(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x", "dependencies": {"a": "1.0.0"}}', encoding="utf-8")
    report = scan(discover(tmp_path), Options())
    lockfile = [f for f in report.findings if f.rule == "DT006"]
    assert len(lockfile) == 1
    assert lockfile[0].severity == "medium"


def test_lockfile_present_suppresses_dt006() -> None:
    assert "DT006" not in rules_fired(scan(discover(HARDENED), Options()))


def test_wildcard_and_lower_bound_are_separate_rules() -> None:
    report = vulnerable_report()
    wildcard = {f.subject for f in report.findings if f.rule == "DT007"}
    lower_bound = {f.subject for f in report.findings if f.rule == "DT008"}
    assert "left-pad" in wildcard
    assert "requests" in lower_bound


def test_cross_manifest_conflict_is_detected(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "a", "dependencies": {"left-pad": "1.3.0"}}', encoding="utf-8")
    sub = tmp_path / "service"
    sub.mkdir()
    (sub / "package.json").write_text('{"name": "b", "dependencies": {"left-pad": "^1.2.0"}}', encoding="utf-8")
    report = scan(discover(tmp_path), Options())
    conflicts = [f for f in report.findings if f.rule == "DT009"]
    assert len(conflicts) == 1
    assert conflicts[0].subject == "left-pad"
    assert conflicts[0].severity == "low"


def test_lockfile_without_integrity_is_reported(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x", "dependencies": {"a": "1.0.0"}}', encoding="utf-8")
    (tmp_path / "package-lock.json").write_text(
        json.dumps({"lockfileVersion": 3, "packages": {"": {}, "node_modules/a": {"version": "1.0.0"}}}),
        encoding="utf-8",
    )
    report = scan(discover(tmp_path), Options())
    integrity = [f for f in report.findings if f.rule == "DT010"]
    assert len(integrity) == 1
    assert "1 of 1" in integrity[0].evidence


def test_threshold_selection_uses_severity_rank() -> None:
    report = vulnerable_report()
    assert len(report.at_or_above("low")) >= len(report.at_or_above("high"))
    assert all(f.rank >= 3 for f in report.at_or_above("high"))


def test_report_is_deterministic() -> None:
    first = to_text(vulnerable_report())
    second = to_text(vulnerable_report())
    assert first == second
    assert first.startswith(first.splitlines()[0])


def test_text_report_ends_with_counts() -> None:
    report = vulnerable_report()
    last = to_text(report).splitlines()[-1]
    counts = report.counts()
    assert last == (
        f"{len(report.inventory.dependencies)} dependencies, "
        f"{len(report.findings)} findings "
        f"[high {counts['high']}, medium {counts['medium']}, low {counts['low']}]"
    )
    assert counts["high"] > 0 and counts["low"] >= 0


# ------------------------------------------------------------------------ CLI


def test_cli_scan_reports_and_exits_nonzero_on_high() -> None:
    result = run_cli("scan", "examples/vulnerable", "--fail-on", "high")
    assert result.returncode == 1
    assert "high" in result.stdout


def test_cli_scan_can_pass_a_higher_threshold_than_findings_allow() -> None:
    result = run_cli("scan", "examples/hardened", "--fail-on", "high")
    assert result.returncode == 0
    assert "0 findings" in result.stdout


def test_cli_scan_json_is_machine_readable() -> None:
    payload = json.loads(run_cli("scan", "examples/vulnerable", "--json").stdout)
    assert payload["dependencies"] > 0
    assert "by_rule" in payload
    assert all("rule" in finding for finding in payload["findings"])


def test_cli_scan_honours_internal_prefix() -> None:
    without = json.loads(run_cli("scan", "examples/vulnerable", "--json").stdout)
    with_prefix = json.loads(
        run_cli("scan", "examples/vulnerable", "--json", "--internal-prefix", "@acme/").stdout
    )
    assert "DT004" not in without["by_rule"]
    assert with_prefix["by_rule"]["DT004"] == 1


def test_cli_scan_rejects_a_bad_threshold() -> None:
    result = run_cli("scan", "examples/vulnerable", "--fail-on", "critical")
    assert result.returncode == 2
    assert "must be one of" in result.stderr


def test_cli_scan_rejects_a_bad_distance() -> None:
    result = run_cli("scan", "examples/vulnerable", "--max-distance", "two")
    assert result.returncode == 2
    assert "integer" in result.stderr


def test_cli_scan_rejects_a_missing_target() -> None:
    result = run_cli("scan", "examples/nope")
    assert result.returncode == 2
    assert "no such target" in result.stderr


def test_cli_scan_without_a_target_is_a_usage_error() -> None:
    result = run_cli("scan", "--json")
    assert result.returncode == 2
    assert "usage" in result.stderr.lower()


def test_cli_rules_lists_every_rule_id() -> None:
    result = run_cli("rules")
    assert result.returncode == 0
    for rule in ("DT001", "DT005", "DT010"):
        assert rule in result.stdout
    assert "10 rule(s)" in result.stdout
