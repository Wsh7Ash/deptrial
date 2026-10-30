"""The rule engine.

Ten rules, each with a stable id (`DT001`..`DT010`) so a suppression in a
review can name exactly what it suppresses. A rule returns findings; it never
raises, because a manifest in the wild is often partly malformed and a scanner
that dies on one bad file reports nothing about the rest.

Severity is about *what an attacker gains*, not about how unusual the pattern is:

* `high` — the declared dependency set lets a third party choose the code that
  runs in your build or on your machine;
* `medium` — the set can change under you, but reaching code execution needs a
  second step;
* `low` — a hygiene problem that makes the other findings harder to reason about.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

from .manifests import (
    BINDING_BOUNDED,
    BINDING_EXACT,
    BINDING_FLOATING,
    BINDING_WILDCARD,
    SOURCE_LOCAL,
    SOURCE_REGISTRY,
    SOURCE_URL,
    SOURCE_VCS,
    Dependency,
    Inventory,
)

SEVERITIES = ("low", "medium", "high")
SEVERITY_RANK = {name: index for index, name in enumerate(SEVERITIES, start=1)}

LIFECYCLE_HOOKS = ("preinstall", "install", "postinstall", "prepare", "prepublish", "prepack")


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    subject: str
    manifest: str
    message: str
    evidence: str = ""

    @property
    def rank(self) -> int:
        return SEVERITY_RANK[self.severity]

    def to_dict(self) -> dict[str, str]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "subject": self.subject,
            "manifest": self.manifest,
            "message": self.message,
            "evidence": self.evidence,
        }


@dataclass
class Options:
    """Everything a rule may consult that is not in the manifests themselves."""

    internal_prefixes: tuple[str, ...] = ()
    allowlist: tuple[str, ...] = ()
    max_distance: int = 2
    fail_on: str = "high"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    inventory: Inventory | None = None

    def sorted_findings(self) -> list[Finding]:
        return sorted(
            self.findings,
            key=lambda f: (-f.rank, f.rule, f.subject, f.manifest),
        )

    def counts(self) -> dict[str, int]:
        counts = {name: 0 for name in SEVERITIES}
        for finding in self.findings:
            counts[finding.severity] += 1
        return counts

    def by_rule(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.rule] = counts.get(finding.rule, 0) + 1
        return dict(sorted(counts.items()))

    def at_or_above(self, severity: str) -> list[Finding]:
        floor = SEVERITY_RANK[severity]
        return [f for f in self.findings if f.rank >= floor]


# --------------------------------------------------------------------- helpers


def levenshtein(left: str, right: str) -> int:
    """Edit distance, iterative and two rows wide."""
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            cost = 0 if left_char == right_char else 1
            current.append(
                min(
                    previous[j] + 1,  # deletion
                    current[j - 1] + 1,  # insertion
                    previous[j - 1] + cost,  # substitution
                )
            )
        previous = current
    return previous[-1]


def _normalise(name: str) -> str:
    """Package names compare case-insensitively and treat `_` and `.` as `-`."""
    return name.strip().lower().replace("_", "-").replace(".", "-")


def _is_internal(name: str, prefixes: Sequence[str]) -> bool:
    lowered = name.strip().lower()
    return any(lowered.startswith(prefix.lower()) for prefix in prefixes)


# ----------------------------------------------------------------------- rules


def rule_floating_range(inventory: Inventory, options: Options) -> list[Finding]:
    """DT001 — an npm range that lets a new upstream release change your build.

    pip's unbounded `>=` is the same risk but has its own rule (DT008), because
    pip has no default upper bound and the remediation differs: npm wants an
    exact pin or a lockfile, pip wants a compatible-release or an upper bound.
    """
    findings: list[Finding] = []
    for dependency in inventory.sorted_dependencies():
        if dependency.source != SOURCE_REGISTRY or dependency.ecosystem != "npm":
            continue
        if dependency.binding != BINDING_FLOATING:
            continue
        findings.append(
            Finding(
                rule="DT001",
                severity="medium",
                subject=dependency.name,
                manifest=dependency.manifest,
                message="version range floats, so a new upstream release is installed without review",
                evidence=f"{dependency.name}@{dependency.constraint}",
            )
        )
    return findings


def rule_non_registry_source(inventory: Inventory, options: Options) -> list[Finding]:
    """DT002 — the bytes come from somewhere without registry integrity data."""
    findings: list[Finding] = []
    for dependency in inventory.sorted_dependencies():
        if dependency.source in {SOURCE_VCS, SOURCE_URL}:
            findings.append(
                Finding(
                    rule="DT002",
                    severity="high",
                    subject=dependency.name,
                    manifest=dependency.manifest,
                    message=f"dependency is fetched from a {dependency.source} source, not the registry",
                    evidence=dependency.constraint,
                )
            )
        elif dependency.source == SOURCE_LOCAL and dependency.constraint.startswith("workspace:"):
            findings.append(
                Finding(
                    rule="DT002",
                    severity="low",
                    subject=dependency.name,
                    manifest=dependency.manifest,
                    message="dependency resolves to a workspace path; it is not published anywhere",
                    evidence=dependency.constraint,
                )
            )
    return findings


def rule_install_script(inventory: Inventory, options: Options) -> list[Finding]:
    """DT003 — a lifecycle hook runs during install, before anyone reads the code."""
    findings: list[Finding] = []
    for key, command in sorted(inventory.scripts.items()):
        manifest, _, hook = key.rpartition(":")
        if hook not in LIFECYCLE_HOOKS:
            continue
        findings.append(
            Finding(
                rule="DT003",
                severity="high",
                subject=hook,
                manifest=manifest or key,
                message=f"`{hook}` runs during install, so its content executes before review",
                evidence=command.strip()[:160],
            )
        )
    return findings


def rule_internal_name_unscoped(inventory: Inventory, options: Options) -> list[Finding]:
    """DT004 — a private name that a public registry could satisfy first."""
    if not options.internal_prefixes:
        return []
    findings: list[Finding] = []
    for dependency in inventory.sorted_dependencies():
        if not _is_internal(dependency.name, options.internal_prefixes):
            continue
        if dependency.source != SOURCE_REGISTRY:
            continue
        if dependency.binding == BINDING_EXACT:
            continue
        findings.append(
            Finding(
                rule="DT004",
                severity="high",
                subject=dependency.name,
                manifest=dependency.manifest,
                message="internal name is resolved from the public registry without an exact pin",
                evidence=f"{dependency.name}@{dependency.constraint}",
            )
        )
    return findings


def rule_typosquat_near_miss(inventory: Inventory, options: Options) -> list[Finding]:
    """DT005 — a name one or two edits away from a dependency you trust."""
    if not options.allowlist:
        return []
    trusted = {_normalise(name) for name in options.allowlist}
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for dependency in inventory.sorted_dependencies():
        candidate = _normalise(dependency.name)
        if candidate in trusted:
            continue
        for name in sorted(trusted):
            distance = levenshtein(candidate, name)
            if distance == 0 or distance > options.max_distance:
                continue
            key = (candidate, name)
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                Finding(
                    rule="DT005",
                    severity="high",
                    subject=dependency.name,
                    manifest=dependency.manifest,
                    message=f"name is {distance} edit(s) from trusted `{name}`",
                    evidence=f"{dependency.name} ~ {name}",
                )
            )
    return findings


def rule_no_lockfile(inventory: Inventory, options: Options) -> list[Finding]:
    """DT006 — an install root whose manifests have no lockfile.

    Per root, not per scan: a lockfile in one project does not make another
    project's installs reproducible. Scanning a workspace previously produced
    zero findings here because any single lockfile anywhere silenced the rule.
    """
    findings: list[Finding] = []
    for root, manifests in inventory.unlocked_roots():
        declared = len(inventory.dependencies_in(root))
        shown = ", ".join(manifests[:4])
        if len(manifests) > 4:
            shown += f" and {len(manifests) - 4} more"
        findings.append(
            Finding(
                rule="DT006",
                severity="medium",
                subject="lockfile",
                manifest=root,
                message=(
                    f"no lockfile in this install root ({len(manifests)} manifest(s): {shown}), "
                    "so two installs are two dependency trees"
                ),
                evidence=f"{declared} declared dependencies",
            )
        )
    return findings


def rule_wildcard_binding(inventory: Inventory, options: Options) -> list[Finding]:
    """DT007 — `*` or `latest` or an empty constraint on a registry package."""
    findings: list[Finding] = []
    for dependency in inventory.sorted_dependencies():
        if dependency.source != SOURCE_REGISTRY:
            continue
        if dependency.binding != BINDING_WILDCARD:
            continue
        findings.append(
            Finding(
                rule="DT007",
                severity="medium",
                subject=dependency.name,
                manifest=dependency.manifest,
                message="constraint is a wildcard, so any published version satisfies it",
                evidence=f"{dependency.name}@{dependency.constraint or '<empty>'}",
            )
        )
    return findings


def rule_unbounded_lower_bound(inventory: Inventory, options: Options) -> list[Finding]:
    """DT008 — `>=1.4` with no upper bound (pip's most common declaration)."""
    findings: list[Finding] = []
    for dependency in inventory.sorted_dependencies():
        if dependency.source != SOURCE_REGISTRY or dependency.ecosystem != "pip":
            continue
        if dependency.binding not in {BINDING_FLOATING}:
            continue
        if "==" in dependency.constraint and "<" not in dependency.constraint:
            continue
        if ">=" not in dependency.constraint and ">" not in dependency.constraint:
            continue
        findings.append(
            Finding(
                rule="DT008",
                severity="medium",
                subject=dependency.name,
                manifest=dependency.manifest,
                message="lower bound only, so any future major version is accepted",
                evidence=f"{dependency.name}{dependency.constraint}",
            )
        )
    return findings


def rule_cross_manifest_conflict(inventory: Inventory, options: Options) -> list[Finding]:
    """DT009 — one package, two constraints, inside the *same* install root.

    Scope matters here: `pytest>=8` in one repository and `pytest>=8.0,<9` in
    another are two independent decisions, not a conflict. Only manifests that
    resolve together can disagree about a version.
    """
    by_key: dict[tuple[str, str], list[Dependency]] = {}
    for dependency in inventory.dependencies:
        by_key.setdefault((dependency.root, _normalise(dependency.name)), []).append(dependency)

    findings: list[Finding] = []
    for (root, name), group in sorted(by_key.items()):
        constraints = {d.constraint for d in group}
        manifests = {d.manifest for d in group}
        if len(constraints) < 2:
            continue
        ordered = sorted(f"{d.manifest}:{d.constraint}" for d in group)
        findings.append(
            Finding(
                rule="DT009",
                severity="low",
                subject=name,
                manifest=root or ", ".join(sorted(manifests)),
                message=(
                    "declared with different constraints inside one install root"
                    if len(manifests) > 1
                    else "declared twice with different constraints in one manifest"
                ),
                evidence="; ".join(ordered),
            )
        )
    return findings


def rule_lockfile_without_integrity(inventory: Inventory, options: Options) -> list[Finding]:
    """DT010 — a lockfile whose entries cannot be verified."""
    if not inventory.lockfiles or inventory.locked_entries == 0:
        return []
    missing = inventory.locked_entries - inventory.integrity_entries
    if missing <= 0:
        return []
    return [
        Finding(
            rule="DT010",
            severity="medium",
            subject="lockfile",
            manifest=", ".join(sorted(inventory.lockfiles)),
            message="lockfile entries without integrity data cannot be verified at install time",
            evidence=f"{missing} of {inventory.locked_entries} resolved entries lack integrity",
        )
    ]


RULES: tuple[tuple[str, Callable[[Inventory, Options], list[Finding]]], ...] = (
    ("DT001", rule_floating_range),
    ("DT002", rule_non_registry_source),
    ("DT003", rule_install_script),
    ("DT004", rule_internal_name_unscoped),
    ("DT005", rule_typosquat_near_miss),
    ("DT006", rule_no_lockfile),
    ("DT007", rule_wildcard_binding),
    ("DT008", rule_unbounded_lower_bound),
    ("DT009", rule_cross_manifest_conflict),
    ("DT010", rule_lockfile_without_integrity),
)


def scan(inventory: Inventory, options: Options | None = None) -> Report:
    """Run every rule and collect the findings."""
    active = options or Options()
    report = Report(inventory=inventory)
    for _, rule in RULES:
        report.findings.extend(rule(inventory, active))
    return report


def to_text(report: Report) -> str:
    lines: list[str] = []
    for finding in report.sorted_findings():
        lines.append(f"{finding.severity:6s} {finding.rule} {finding.subject}: {finding.message}")
        if finding.evidence:
            lines.append(f"       evidence: {finding.evidence}")
        lines.append(f"       manifest: {finding.manifest}")
    counts = report.counts()
    inventory = report.inventory
    declared = len(inventory.dependencies) if inventory else 0
    findings = len(report.findings)
    lines.append(
        f"{declared} {'dependency' if declared == 1 else 'dependencies'}, "
        f"{findings} {'finding' if findings == 1 else 'findings'} "
        f"[high {counts['high']}, medium {counts['medium']}, low {counts['low']}]"
    )
    return "\n".join(lines)


__all__ = [
    "Finding",
    "Options",
    "RULES",
    "Report",
    "SEVERITIES",
    "SEVERITY_RANK",
    "levenshtein",
    "scan",
    "to_text",
]
