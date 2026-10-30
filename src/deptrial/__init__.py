"""deptrial: supply-chain dependency skills and a manifest trust scanner."""

from __future__ import annotations

from .cli import main
from .manifests import Dependency, Inventory, classify_binding, classify_source, discover
from .model import Skill, skill_from_dict
from .render import build_pack, render_catalog, render_skill, sha256_of, word_count
from .rules import RULES, Finding, Options, Report, levenshtein, scan, to_text
from .validate import validate_pack, validate_skill

__all__ = [
    "main",
    "Dependency",
    "Inventory",
    "classify_binding",
    "classify_source",
    "discover",
    "Skill",
    "skill_from_dict",
    "build_pack",
    "render_catalog",
    "render_skill",
    "sha256_of",
    "word_count",
    "RULES",
    "Finding",
    "Options",
    "Report",
    "levenshtein",
    "scan",
    "to_text",
    "validate_pack",
    "validate_skill",
]
