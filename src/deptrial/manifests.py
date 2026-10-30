"""Manifest discovery and parsing.

Three ecosystems are read: npm (``package.json``), pip requirements
(``requirements*.txt``) and PEP 621 (``pyproject.toml`` via :mod:`tomllib`).

Every dependency is classified by *source* (where the bytes come from) and by
*binding* (how tightly the version is held). Both classifications are made here
so the rules in :mod:`deptrial.rules` never have to look at raw strings.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - 3.10 fallback
    tomllib = None  # type: ignore[assignment]

MANIFEST_NAMES = ("package.json", "requirements.txt", "requirements-dev.txt", "pyproject.toml")
LOCKFILE_NAMES = ("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "uv.lock")

# Directories that never contain a project's own manifests. `.git` matters most:
# a repository of repositories is mostly object files, and walking them turns a
# two-second scan into a four-minute one without finding anything.
PRUNED_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        "build",
        "dist",
        ".next",
        "target",
    }
)

SOURCE_REGISTRY = "registry"
SOURCE_VCS = "vcs"
SOURCE_URL = "url"
SOURCE_LOCAL = "local"

BINDING_EXACT = "exact"
BINDING_BOUNDED = "bounded"
BINDING_FLOATING = "floating"
BINDING_WILDCARD = "wildcard"

VCS_PREFIXES = ("git+", "git://", "git@", "github:", "gitlab:", "bitbucket:", "ssh://")
URL_PREFIXES = ("http://", "https://", "file:", "link:", "portal:")
LOCAL_PREFIXES = ("workspace:", "file:../", "file:./", ".", "../")

FLOATING_RE = re.compile(r"^[\^~]")
WILDCARD_TOKENS = frozenset({"", "*", "latest", "x", "X", "-"})
PEP440_PIN = re.compile(r"^===?\s*([0-9][0-9A-Za-z.*+!-]*)$")
PEP440_BOUNDED = re.compile(r"[<>]=?")
VERSION_TOKEN = re.compile(r"[0-9]+(?:\.[0-9]+)*")


@dataclass(frozen=True)
class Dependency:
    """One declared dependency and everything the rules need to know about it."""

    name: str
    constraint: str
    source: str
    binding: str
    manifest: str

    @property
    def ecosystem(self) -> str:
        return "npm" if self.manifest.endswith("package.json") else "pip"

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "constraint": self.constraint,
            "source": self.source,
            "binding": self.binding,
            "manifest": self.manifest,
            "ecosystem": self.ecosystem,
        }


@dataclass
class Inventory:
    """Everything found in one project tree."""

    dependencies: list[Dependency] = field(default_factory=list)
    scripts: dict[str, str] = field(default_factory=dict)
    manifests: list[str] = field(default_factory=list)
    lockfiles: list[str] = field(default_factory=list)
    integrity_entries: int = 0
    locked_entries: int = 0

    def sorted_dependencies(self) -> list[Dependency]:
        return sorted(self.dependencies, key=lambda d: (d.manifest, d.name, d.constraint))


def classify_source(spec: str) -> str:
    """Where does this dependency's content come from?"""
    lowered = spec.strip().lower()
    if lowered.startswith(LOCAL_PREFIXES):
        return SOURCE_LOCAL
    if lowered.startswith(VCS_PREFIXES):
        return SOURCE_VCS
    if lowered.startswith(URL_PREFIXES):
        return SOURCE_URL
    return SOURCE_REGISTRY


def classify_binding(constraint: str, ecosystem: str = "npm") -> str:
    """How tightly does this constraint hold the version?"""
    value = constraint.strip()
    lowered = value.lower()
    if lowered in WILDCARD_TOKENS:
        return BINDING_WILDCARD
    if ecosystem == "npm":
        if re.search(r"(^|\.)[xX]($|\.)", value) or "*" in value:
            return BINDING_WILDCARD
        if "||" in value:
            return BINDING_FLOATING
        if FLOATING_RE.match(value):
            return BINDING_FLOATING
        if value.startswith("=") and VERSION_TOKEN.fullmatch(value.lstrip("=")):
            return BINDING_EXACT
        if value.startswith((">=", ">", "<=", "<")):
            return BINDING_BOUNDED if "," in value or " " in value else BINDING_FLOATING
        if VERSION_TOKEN.fullmatch(value):
            return BINDING_EXACT
        return BINDING_FLOATING
    # PEP 440
    pinned = PEP440_PIN.match(value)
    if pinned:
        return BINDING_FLOATING if pinned.group(1).endswith(".*") else BINDING_EXACT
    if PEP440_BOUNDED.search(value) and re.search(r"[<]", value):
        return BINDING_BOUNDED
    if PEP440_BOUNDED.search(value):
        return BINDING_FLOATING
    return BINDING_FLOATING


def _dependency(name: str, constraint: str, manifest: str, ecosystem: str) -> Dependency:
    spec = constraint.strip()
    source = classify_source(spec)
    binding = classify_binding(spec, ecosystem) if source == SOURCE_REGISTRY else BINDING_EXACT
    return Dependency(
        name=name.strip(),
        constraint=spec,
        source=source,
        binding=binding,
        manifest=manifest,
    )


def parse_package_json(path: Path, display: str | None = None) -> tuple[list[Dependency], dict[str, str]]:
    """Return dependencies and lifecycle scripts from a ``package.json``."""
    label = display or str(path)
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    dependencies: list[Dependency] = []
    for key in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        block = data.get(key) or {}
        if not isinstance(block, dict):
            continue
        for name, constraint in block.items():
            dependencies.append(_dependency(name, str(constraint), label, "npm"))
    scripts = {
        str(key): str(value)
        for key, value in (data.get("scripts") or {}).items()
        if key in {"preinstall", "install", "postinstall", "prepare", "prepublish", "prepack"}
    }
    return dependencies, scripts


def parse_requirements(path: Path, display: str | None = None) -> list[Dependency]:
    """Return dependencies from a pip requirements file."""
    label = display or str(path)
    dependencies: list[Dependency] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        if line.startswith(("git+", "http://", "https://")):
            dependencies.append(_dependency(_vcs_name(line), line, label, "pip"))
            continue
        match = re.match(r"^([A-Za-z0-9_.\-\[\]]+)\s*(.*)$", line)
        if not match:
            continue
        name, constraint = match.group(1), match.group(2).strip()
        dependencies.append(_dependency(name, constraint, label, "pip"))
    return dependencies


def _vcs_name(line: str) -> str:
    """Best-effort package name for a vcs or url requirement line.

    pip accepts ``#egg=name`` as the declared identity; without it the name is
    the repository basename, which is what the resolver records too.
    """
    if "#egg=" in line:
        return line.split("#egg=", 1)[1].split("&", 1)[0].strip()
    cleaned = line.split("#", 1)[0].rstrip("/")
    cleaned = cleaned.split("@", 1)[0] if "@" in cleaned.rsplit("/", 1)[-1] else cleaned
    tail = cleaned.rsplit("/", 1)[-1]
    return tail[:-4] if tail.endswith(".git") else tail


def parse_pyproject(path: Path, display: str | None = None) -> list[Dependency]:
    """Return dependencies from a PEP 621 ``pyproject.toml``."""
    label = display or str(path)
    if tomllib is None:  # pragma: no cover - 3.10 fallback
        return []
    data = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    project = data.get("project") or {}
    declarations: list[str] = list(project.get("dependencies") or [])
    for group in (project.get("optional-dependencies") or {}).values():
        declarations.extend(group or [])
    dependencies: list[Dependency] = []
    for declaration in declarations:
        match = re.match(r"^([A-Za-z0-9_.\-]+)(\[[^\]]*\])?\s*(.*)$", str(declaration))
        if not match:
            continue
        name, _, constraint = match.groups()
        dependencies.append(_dependency(name, constraint or "", label, "pip"))
    return dependencies


def _walk_manifests(base: Path, max_depth: int) -> list[Path]:
    """Find manifest and lockfile paths, pruning directories we never want.

    ``os.walk`` is used rather than ``rglob`` because pruning has to happen
    before descent: an unpruned walk of this repository reads 13k files inside
    nested ``.git`` directories to find zero manifests.
    """
    found: list[Path] = []
    base_depth = len(base.parts)
    for directory, dirnames, filenames in os.walk(base):
        current = Path(directory)
        depth = len(current.parts) - base_depth
        # Mutating dirnames in place is what prunes the descent.
        dirnames[:] = sorted(name for name in dirnames if name not in PRUNED_DIRS)
        if depth >= max_depth:
            dirnames[:] = []
        for filename in sorted(filenames):
            if filename in (*MANIFEST_NAMES, *LOCKFILE_NAMES):
                found.append(current / filename)
    return found


def discover(root: str | Path, max_depth: int = 4) -> Inventory:
    """Walk a tree and build one inventory of every manifest found."""
    base = Path(root)
    if not base.exists():
        raise FileNotFoundError(f"no such target: {root}")

    inventory = Inventory()
    candidates: Iterable[Path]
    if base.is_file():
        candidates = [base]
    else:
        candidates = _walk_manifests(base, max_depth)

    for path in candidates:
        display = str(path.relative_to(base)) if base.is_dir() else path.name
        if path.name in LOCKFILE_NAMES:
            inventory.lockfiles.append(display)
            _count_lockfile(path, inventory)
            continue
        if path.name == "package.json":
            dependencies, scripts = parse_package_json(path, display)
            inventory.dependencies.extend(dependencies)
            for key, command in scripts.items():
                inventory.scripts[f"{display}:{key}"] = command
        elif path.name in {"requirements.txt", "requirements-dev.txt"}:
            inventory.dependencies.extend(parse_requirements(path, display))
        elif path.name == "pyproject.toml":
            inventory.dependencies.extend(parse_pyproject(path, display))
        inventory.manifests.append(display)

    return inventory


def _count_lockfile(path: Path, inventory: Inventory) -> None:
    """Count resolved packages and how many carry integrity data."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.name in {"package-lock.json", "npm-shrinkwrap.json"}:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return
        packages = data.get("packages") or {}
        for name, entry in packages.items():
            if not name:
                continue
            inventory.locked_entries += 1
            if isinstance(entry, dict) and entry.get("integrity"):
                inventory.integrity_entries += 1
        return
    if path.name == "yarn.lock":
        inventory.locked_entries += text.count("\nresolution:")
        inventory.integrity_entries += text.count("\nintegrity ")
        return
    if path.name == "pnpm-lock.yaml":
        inventory.locked_entries += text.count("\n  /") + text.count("\n  '")
        inventory.integrity_entries += text.count("integrity:")
        return
    if path.name in {"poetry.lock", "uv.lock"}:
        inventory.locked_entries += text.count("[[package]]")
        inventory.integrity_entries += text.count("hash = ")


def iter_names(inventory: Inventory) -> Iterator[str]:
    for dependency in inventory.dependencies:
        yield dependency.name


__all__ = [
    "BINDING_BOUNDED",
    "BINDING_EXACT",
    "BINDING_FLOATING",
    "BINDING_WILDCARD",
    "Dependency",
    "Inventory",
    "LOCKFILE_NAMES",
    "MANIFEST_NAMES",
    "SOURCE_LOCAL",
    "SOURCE_REGISTRY",
    "SOURCE_URL",
    "SOURCE_VCS",
    "classify_binding",
    "classify_source",
    "discover",
    "parse_package_json",
    "parse_pyproject",
    "parse_requirements",
]
