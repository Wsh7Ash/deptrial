"""Deterministic SKILL.md rendering and pack building for deptrial."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .model import Skill

FENCE = "```"


def render_description(skill: Skill) -> str:
    """Front-matter description: the summary plus an explicit use-when clause."""
    summary = skill.summary.rstrip(".")
    return f"{summary}. Use when {skill.use_when}"


def render_frontmatter(pack: dict[str, Any], skill: Skill) -> str:
    lines = [
        "---",
        f"name: {skill.slug}",
        "description: " + json.dumps(render_description(skill), ensure_ascii=True),
        f"pack: {pack['name']}",
        f"version: {pack['version']}",
        f"category: {pack['category']}",
        "tags: [" + ", ".join(skill.tags) + "]",
        f"phase: {skill.meta_get('phase', 'plan')}",
        "---",
    ]
    return "\n".join(lines)


def render_skill(pack: dict[str, Any], skill: Skill) -> str:
    """Render one SKILL.md. Pure function: identical input, byte-identical output."""
    body: list[str] = [f"# {skill.title}", "", f"> {skill.summary}", ""]
    body.append(f"**Use when:** {skill.use_when}")
    body.append("")
    body.append(f"**Avoid when:** {skill.avoid_when}")
    body.append("")
    body.append("## Procedure")
    body.append("")
    body.extend(f"{i}. {step}" for i, step in enumerate(skill.steps, start=1))
    body.append("")
    body.append("## Signals")
    body.append("")
    body.extend(f"- {signal}" for signal in skill.signals)
    body.append("")
    body.append("## Patterns")
    body.append("")
    for index, (label, code) in enumerate(skill.patterns, start=1):
        body.append(f"**{index}. {label}**")
        body.append("")
        body.append(FENCE)
        body.append(code)
        body.append(FENCE)
        body.append("")
    body.append("## Pitfalls")
    body.append("")
    body.extend(f"- {pitfall}" for pitfall in skill.pitfalls)
    body.append("")
    body.append("## Done when")
    body.append("")
    body.extend(f"- {item}" for item in skill.done_when)
    body.append("")
    body.append("## References")
    body.append("")
    body.extend(f"- {ref}" for ref in skill.refs)

    return render_frontmatter(pack, skill) + "\n\n" + "\n".join(body) + "\n"


def strip_frontmatter(text: str) -> str:
    """Return the markdown body without the YAML front-matter block."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + len("\n---\n") :]


def word_count(text: str) -> int:
    return len(strip_frontmatter(text).split())


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_catalog(pack: dict[str, Any], skills: list[Skill]) -> str:
    lines = [
        f"{pack['name']} Skill Catalog",
        "",
        f"{len(skills)} skills across {len({s.meta_get('phase') for s in skills})} phases.",
        "",
        "| `slug` | title | phase |",
        "|---|---|---|",
    ]
    for skill in sorted(skills, key=lambda s: s.slug):
        phase = skill.meta_get("phase", "?")
        lines.append(f"| `{skill.slug}` | {skill.title} | {phase} |")
    lines.append("")
    return "\n".join(lines)


def render_manifest(pack: dict[str, Any], skills: list[Skill]) -> str:
    entries = []
    for skill in sorted(skills, key=lambda s: s.slug):
        text = render_skill(pack, skill)
        entries.append({"slug": skill.slug, "sha256": sha256_of(text)})
    manifest = {
        "name": pack["name"],
        "version": pack["version"],
        "category": pack["category"],
        "skill_count": len(skills),
        "skills": entries,
    }
    return json.dumps(manifest, indent=2, ensure_ascii=True) + "\n"


def build_pack(
    root: str | Path | None,
    pack: dict[str, Any],
    skills: list[Skill],
) -> dict[str, str]:
    """Return every generated artifact as a relative path -> text mapping.

    When ``root`` is given the files are also written to disk. The mapping is
    ordered and deterministic so callers can compare two builds for drift.
    """
    files: dict[str, str] = {}
    for skill in sorted(skills, key=lambda s: s.slug):
        files[f"skills/{skill.slug}/SKILL.md"] = render_skill(pack, skill)
    files["pack.json"] = render_manifest(pack, skills)
    files["results/catalog.md"] = render_catalog(pack, skills)

    if root is not None:
        base = Path(root)
        for rel, text in files.items():
            out = base / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")

    return files


__all__ = [
    "FENCE",
    "render_description",
    "render_frontmatter",
    "render_skill",
    "strip_frontmatter",
    "word_count",
    "sha256_of",
    "render_catalog",
    "render_manifest",
    "build_pack",
]