"""CLI entry point for deptrial."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .corpus import BY_SLUG, PACK, SKILLS
from .manifests import discover
from .render import build_pack, render_catalog, render_skill, word_count
from .rules import Options, RULES, SEVERITIES, SEVERITY_RANK, scan, to_text
from .validate import (
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_WORDS,
    validate_pack,
)

ROOT = Path(__file__).resolve().parents[2]
VERSION = PACK["version"]

USAGE = """
deptrial - supply-chain dependency skills and a manifest trust scanner

Usage: deptrial <command> [options]

Commands:
  validate [--json]     Check every skill against the corpus rules
  list [--phase P]      List skills, optionally filtered by phase
  show SLUG             Print one rendered SKILL.md
  render                Write skills/<slug>/SKILL.md for every skill
  catalog               Write results/catalog.md
  build                 Write the whole pack (skills, pack.json, catalog)
  scan PATH             Scan a project tree of manifests
       [--json] [--internal-prefix P ...] [--allowlist N ...] [--max-distance N]
       [--fail-on low|medium|high]
  rules                 List the rule ids and what each one means
  --version             Print the version
"""

RULE_SUMMARY = {
    "DT001": ("medium", "npm range floats (^, ~, || or an operator without an upper bound)"),
    "DT002": ("high", "dependency fetched from a vcs, url or local source"),
    "DT003": ("high", "lifecycle hook runs during install"),
    "DT004": ("high", "internal name resolved from the public registry without an exact pin"),
    "DT005": ("high", "declared name is within edit distance of a trusted name"),
    "DT006": ("medium", "an install root whose manifests have no lockfile"),
    "DT007": ("medium", "wildcard constraint (empty, *, latest, x)"),
    "DT008": ("medium", "pip lower bound with no upper bound"),
    "DT009": ("low", "same package declared differently inside one install root"),
    "DT010": ("medium", "lockfile entries without integrity data"),
}


def _multi(args: list[str], name: str) -> list[str]:
    """Collect every value after a repeatable flag, stopping at the next flag."""
    values: list[str] = []
    index = 0
    while index < len(args):
        if args[index] == name and index + 1 < len(args) and not args[index + 1].startswith("--"):
            values.append(args[index + 1])
            index += 2
            continue
        index += 1
    return values


def _flag(args: list[str], name: str, default: str | None = None) -> str | None:
    if name in args:
        index = args.index(name)
        if index + 1 < len(args):
            return args[index + 1]
    return default


def _positional(args: list[str]) -> str | None:
    """The first argument that is not a flag or a flag's value."""
    skip = {"--internal-prefix", "--allowlist", "--max-distance", "--fail-on"}
    index = 0
    while index < len(args):
        token = args[index]
        if token in skip:
            index += 2
            continue
        if token.startswith("--"):
            index += 1
            continue
        return token
    return None


def _cmd_validate(args: list[str]) -> int:
    issues = validate_pack(PACK, SKILLS)
    if "--json" in args:
        payload = {
            "pack": PACK["name"],
            "version": VERSION,
            "expected": PACK["expected_skills"],
            "valid": len(SKILLS) - len({i.split(":")[0] for i in issues}),
            "total": len(SKILLS),
            "passed": not issues,
            "floors": {
                "min_steps": MIN_STEPS,
                "min_signals": MIN_SIGNALS,
                "min_patterns": MIN_PATTERNS,
                "min_pitfalls": MIN_PITFALLS,
                "min_words": MIN_WORDS,
            },
            "issues": issues,
        }
        print(json.dumps(payload, indent=2))
        return 0 if not issues else 1

    if issues:
        for issue in issues:
            print(f"  ISSUE: {issue}")
        print(f"{len(SKILLS) - len({i.split(':')[0] for i in issues})}/{len(SKILLS)} skills valid")
        return 1
    print(f"{len(SKILLS)}/{len(SKILLS)} skills valid")
    return 0


def _cmd_list(args: list[str]) -> int:
    phase = _flag(args, "--phase")
    rows = [s for s in SKILLS if phase is None or s.meta_get("phase") == phase]
    for skill in sorted(rows, key=lambda s: s.slug):
        print(f"{skill.slug:34s} {skill.meta_get('phase'):12s} {skill.title}")
    print(f"{len(rows)} skill(s)")
    return 0


def _cmd_show(args: list[str]) -> int:
    slug = _positional(args)
    if slug is None:
        print("usage: deptrial show SLUG", file=sys.stderr)
        return 2
    skill = BY_SLUG.get(slug)
    if skill is None:
        print(f"unknown slug: {slug}", file=sys.stderr)
        return 2
    print(render_skill(PACK, skill), end="")
    return 0


def _cmd_render() -> int:
    files = build_pack(ROOT, PACK, SKILLS)
    rendered = sum(1 for rel in files if rel.startswith("skills/"))
    print(f"Rendered {rendered} skills to {ROOT / 'skills'}")
    return 0


def _cmd_catalog() -> int:
    path = ROOT / "results" / "catalog.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_catalog(PACK, SKILLS), encoding="utf-8")
    print(f"Catalog written to {path}")
    return 0


def _cmd_build() -> int:
    files = build_pack(ROOT, PACK, SKILLS)
    words = sum(word_count(text) for rel, text in files.items() if rel.startswith("skills/"))
    print(f"Built {len(files)} artifacts, {words} rendered skill words")
    return 0


def _cmd_rules() -> int:
    for rule, function in RULES:
        severity, meaning = RULE_SUMMARY.get(rule, ("?", function.__doc__ or ""))
        print(f"{rule} {severity:6s} {meaning}")
    print(f"{len(RULES)} rule(s)")
    return 0


def _cmd_scan(args: list[str]) -> int:
    target = _positional(args)
    if target is None:
        print("usage: deptrial scan PATH [--json] [--fail-on low|medium|high]", file=sys.stderr)
        return 2

    fail_on = _flag(args, "--fail-on", "high")
    if fail_on not in SEVERITY_RANK:
        print(f"error: --fail-on must be one of {', '.join(SEVERITIES)}", file=sys.stderr)
        return 2

    try:
        distance = int(_flag(args, "--max-distance", "2") or "2")
    except ValueError:
        print("error: --max-distance must be an integer", file=sys.stderr)
        return 2

    options = Options(
        internal_prefixes=tuple(_multi(args, "--internal-prefix")),
        allowlist=tuple(_multi(args, "--allowlist")),
        max_distance=distance,
        fail_on=fail_on,
    )

    try:
        inventory = discover(target)
    except FileNotFoundError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    report = scan(inventory, options)

    if "--json" in args:
        payload = {
            "target": str(target),
            "manifests": sorted(inventory.manifests),
            "lockfiles": sorted(inventory.lockfiles),
            "dependencies": len(inventory.dependencies),
            "counts": report.counts(),
            "by_rule": report.by_rule(),
            "findings": [f.to_dict() for f in report.sorted_findings()],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(to_text(report))

    offending = report.at_or_above(fail_on)
    return 1 if offending else 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args or args[0] in {"-h", "--help", "help"}:
        print(USAGE, end="")
        return 0
    if args[0] in {"--version", "-V"}:
        print(f"deptrial {VERSION}")
        return 0

    command, rest = args[0], args[1:]

    if command == "validate":
        return _cmd_validate(rest)
    if command == "list":
        return _cmd_list(rest)
    if command == "show":
        return _cmd_show(rest)
    if command == "render":
        return _cmd_render()
    if command == "catalog":
        return _cmd_catalog()
    if command == "build":
        return _cmd_build()
    if command == "scan":
        return _cmd_scan(rest)
    if command == "rules":
        return _cmd_rules()

    print(f"Unknown command: {command}", file=sys.stderr)
    print(USAGE, end="", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
