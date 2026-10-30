"""Validation gates for the deptrial corpus."""

from __future__ import annotations

from typing import Any

from .model import Skill

MIN_STEPS = 3
MIN_SIGNALS = 2
MIN_PATTERNS = 1
MIN_PITFALLS = 2
MIN_WORDS = 80

PHASES = frozenset(
    {
        "recon",
        "registry",
        "confusion",
        "typosquat",
        "pinning",
        "scripts",
        "provenance",
        "ci",
        "tools",
        "review",
    }
)


def validate_skill(skill: Skill) -> list[str]:
    """Return a list of validation errors for a single skill; empty means valid."""
    errors: list[str] = []

    if len(skill.steps) < MIN_STEPS:
        errors.append(f"steps: need >= {MIN_STEPS}, got {len(skill.steps)}")
    if len(skill.signals) < MIN_SIGNALS:
        errors.append(f"signals: need >= {MIN_SIGNALS}, got {len(skill.signals)}")
    if len(skill.patterns) < MIN_PATTERNS:
        errors.append(f"patterns: need >= {MIN_PATTERNS}, got {len(skill.patterns)}")
    if len(skill.pitfalls) < MIN_PITFALLS:
        errors.append(f"pitfalls: need >= {MIN_PITFALLS}, got {len(skill.pitfalls)}")
    if skill.meta_get("phase", "") not in PHASES:
        errors.append(f"unknown phase: {skill.meta_get('phase')}")
    if not skill.refs:
        errors.append("refs: at least one reference required")
    else:
        for ref in skill.refs:
            if not (ref.startswith("[") and "](https://" in ref):
                errors.append(f"ref not HTTPS-labelled: {ref}")
                break
    if len(skill.summary.strip()) < 20:
        errors.append("summary: too short to be useful")
    if len(skill.avoid_when.strip()) < 10:
        errors.append("avoid_when: too short to be useful")

    return errors


def validate_pack(pack: dict[str, Any], skills: list[Any]) -> list[str]:
    """Return every validation error across the whole pack."""
    errors: list[str] = []

    for key in ("name", "version", "category", "description", "expected_skills"):
        if key not in pack:
            errors.append(f"pack missing key: {key}")

    expected = int(pack.get("expected_skills", 0))
    if len(skills) != expected:
        errors.append(f"skill count: expected {expected}, got {len(skills)}")

    for skill in skills:
        for error in validate_skill(skill):
            errors.append(f"{skill.slug}: {error}")

    phases = {skill.meta_get("phase") for skill in skills}
    missing = PHASES - phases
    if missing:
        errors.append(f"missing phases: {sorted(missing)}")

    slugs = [skill.slug for skill in skills]
    if len(slugs) != len(set(slugs)):
        dupes = sorted({s for s in slugs if slugs.count(s) > 1})
        errors.append(f"duplicate slugs in pack: {dupes}")

    titles = [skill.title.lower() for skill in skills]
    if len(titles) != len(set(titles)):
        dupes = sorted({t for t in titles if titles.count(t) > 1})
        errors.append(f"duplicate titles in pack: {dupes}")

    summaries = [skill.summary for skill in skills]
    if len(summaries) != len(set(summaries)):
        errors.append("duplicate summaries in pack")

    return errors


__all__ = [
    "MIN_STEPS",
    "MIN_SIGNALS",
    "MIN_PATTERNS",
    "MIN_PITFALLS",
    "MIN_WORDS",
    "PHASES",
    "validate_skill",
    "validate_pack",
]