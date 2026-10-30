# Changelog

## [1.0.0] - 2026-10-30

### Added

- 50 authored skills across 10 phases: `recon` (5), `registry` (5), `confusion` (6),
  `typosquat` (5), `pinning` (6), `scripts` (5), `provenance` (5), `ci` (5),
  `tools` (4), `review` (4).
- `deptrial scan` with ten stable rule ids `DT001`..`DT010`, severity ranking and
  threshold-based exit codes; `--json`, repeatable `--internal-prefix` and
  `--allowlist`, `--max-distance`, `--fail-on`.
- Parsers for `package.json`, `requirements*.txt` and PEP 621 `pyproject.toml`,
  with source (`registry`/`vcs`/`url`/`local`) and binding
  (`exact`/`bounded`/`floating`/`wildcard`) classification.
- `deptrial rules` to list rule ids with meanings and severities.
- Deterministic rendering of 50 `SKILL.md` files plus `pack.json` (50 sha256
  digests) and `results/catalog.md`, all committed and drift-checked.
- Two fixture trees: `examples/vulnerable` (15 findings, 7 high) and
  `examples/hardened` (0 findings).
- 91 tests across the corpus, parsers, classifiers, rules and CLI.

### Fixed

- Parts 1 and 2 both defined the pinning and scripts skills; trimmed to 50 unique.
- `=1.2.3` was classified as a floating range instead of an exact pin.
- A pip vcs requirement without `#egg=` took the whole URL as its package name.
- The report footer printed `dependenc(ies)`/`finding(s)`.

### Notes

- No registry client: `DT004` fires on the local shape of the risk, not on a
  confirmed public registration.
- Only manifests are parsed; transitive dependencies are not scanned.
