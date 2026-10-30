"""deptrial corpus: pack metadata plus 50 authored supply-chain skills.

Skills are authored as plain dicts in ``part1``..``part3`` and loaded once
into the validated :class:`~deptrial.model.Skill` shape.
"""

from __future__ import annotations

from typing import Any

from ..model import skill_from_dict
from .part1 import SKILLS as PART1
from .part2 import SKILLS as PART2
from .part3 import SKILLS as PART3

PACK: dict[str, Any] = {
    "name": "deptrial",
    "version": "1.0.0",
    "category": "supply-chain",
    "license": "MIT",
    "runtime": "Claude Code, opencode, or any agent runtime that loads SKILL.md files",
    "description": (
        "50 validated skills for reviewing dependency trust: manifest recon, "
        "registry metadata, dependency confusion, typosquatting, pinning and "
        "lockfiles, install scripts, provenance, CI execution and reporting, "
        "with a CLI that scans manifests using stable rule ids."
    ),
    "expected_skills": 50,
}

SKILLS: list[Any] = [skill_from_dict(raw) for raw in (*PART1, *PART2, *PART3)]
BY_SLUG: dict[str, Any] = {skill.slug: skill for skill in SKILLS}

__all__ = ["PACK", "SKILLS", "BY_SLUG"]
