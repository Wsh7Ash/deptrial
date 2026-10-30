# deptrial

**50 validated supply-chain skills and a manifest trust scanner with ten stable rule ids.**

Dependency risk is decided by small, checkable facts: whether a constraint can move, whether a name is one edit from a name you trust, whether the bytes come from the registry at all, and whether anything runs at install. `deptrial` reads npm, pip and PEP 621 manifests, resolves those facts, and reports findings under rule ids a review can name.

```
$ deptrial scan examples/vulnerable --internal-prefix @acme/ --allowlist express --fail-on high
high   DT002 express: dependency is fetched from a vcs source, not the registry
       evidence: github:expressjs/express#main
       manifest: package.json
high   DT003 postinstall: `postinstall` runs during install, so its content executes before review
       evidence: node ./scripts/patch-runtime.js
       manifest: package.json
high   DT004 @acme/design-tokens: internal name is resolved from the public registry without an exact pin
       evidence: @acme/design-tokens@>=1.0.0
       manifest: package.json
high   DT005 expres: name is 1 edit(s) from trusted `express`
       evidence: expres ~ express
       manifest: package.json
medium DT001 lodash: version range floats, so a new upstream release is installed without review
       evidence: lodash@^4.17.21
       manifest: package.json
medium DT008 requests: lower bound only, so any future major version is accepted
       evidence: requests>=2.28
       manifest: requirements.txt
14 dependencies, 15 findings [high 7, medium 8, low 0]
$ echo $?
1
```

## The ten rules

| Rule | Severity | What it means |
|---|---|---|
| `DT001` | medium | npm range floats: `^`, `~`, `||`, or a comparison operator with no upper bound |
| `DT002` | high | dependency comes from a vcs, url or local source, not the registry |
| `DT003` | high | a lifecycle hook runs during install (`preinstall`, `install`, `postinstall`, `prepare`, `prepublish`, `prepack`) |
| `DT004` | high | an internal name is resolved from the public registry without an exact pin |
| `DT005` | high | a declared name is within edit distance of a trusted name |
| `DT006` | medium | manifests with no lockfile |
| `DT007` | medium | wildcard constraint: empty, `*`, `latest`, `x` |
| `DT008` | medium | pip lower bound with no upper bound |
| `DT009` | low | the same package declared with different constraints in two manifests |
| `DT010` | medium | lockfile entries without integrity data |

Severity is about what an attacker gains, not about how unusual a pattern is: `high` means a third party can choose the code that runs in your build, `medium` means the dependency set can change under you, `low` is hygiene that makes the other findings harder to reason about.

Exit codes make it a gate: `0` when nothing reaches `--fail-on`, `1` when findings at or above it exist, `2` on a usage error.

## Why this pack exists

Supply-chain review fails in specific ways, and the failures are process failures:

- the manifest is reviewed and the install command in CI, which overrides it, is not;
- a private name is assumed private without checking whether the public registry could answer for it;
- a range is approved because the resolved version looked fine at review time;
- an install hook runs in a job that can publish to the registry, so review happens after execution;
- an attestation is read but the identity it names is never compared with the publisher you expect;
- a near-miss dependency is installed by a typo, and the typo is invisible in a rendered diff;
- the fix pins one manifest and leaves the same name unbounded in a second one.

The 50 skills cover the full engagement: `recon` -> `registry` -> `confusion` -> `typosquat` -> `pinning` -> `scripts` -> `provenance` -> `ci` -> `tools` -> `review`.

## Install

```bash
python -m pip install -e .
deptrial validate
```

No runtime dependencies. Python 3.10+ (`tomllib` needs 3.11 for `pyproject.toml` parsing; on 3.10 that parser returns nothing and the other manifest formats still work).

## Commands

| Command | What it does |
|---|---|
| `deptrial validate [--json]` | Run every corpus rule; exit 1 with the specific issues if any fail |
| `deptrial list [--phase P]` | List skills, optionally filtered by one of the 10 phases |
| `deptrial show SLUG` | Print one fully rendered `SKILL.md` |
| `deptrial render` / `catalog` / `build` | Regenerate skills, `pack.json` and the catalog |
| `deptrial scan PATH` | Scan a project tree for manifest findings |
| `deptrial rules` | List the ten rule ids with severities |

`scan` options: `--json`, repeatable `--internal-prefix` and `--allowlist`, `--max-distance` (default 2), `--fail-on low|medium|high` (default `high`).

## The scanner

```
manifests.py   discover + parse package.json, requirements*.txt, pyproject.toml;
               classify every dependency by source and by binding
rules.py       ten rules over one Inventory, deterministic ordering, severity ranking
cli.py         validate / list / show / render / catalog / build / scan / rules
```

Discovery skips `node_modules` and `.venv`, walks to depth 4, and pairs manifests with their lockfiles. `DT004` and `DT005` are opt-in by design: an internal prefix and an allowlist are organisational facts the tool cannot guess, so passing them is what turns those rules on.

## Use as agent skills

Each rendered skill is a `SKILL.md` with YAML front-matter (`name`, `description`, `pack`, `version`, `category`, `tags`, `phase`) and a body with procedure, signals, a command pattern, pitfalls, done-when criteria and references. Point Claude Code, opencode or any runtime that loads skill directories at `skills/`:

```
skills/confusion-enumerate-internal-names/SKILL.md
skills/pinning-lockfile-integrity/SKILL.md
skills/scripts-sandbox-install/SKILL.md
...
```

## The validator is the point

Nine per-skill rules enforced for all 50: 3 steps, 2 signals, 1 `(label, code)` pattern, 2 pitfalls, a phase from the closed set of 10, an HTTPS-labelled reference, a summary of at least 20 characters, an `avoid_when` of at least 10, and 80 rendered words. Package rules add: exactly 50 skills, all 10 phases present, unique slugs, unique case-insensitive titles, unique summaries.

One test also asserts no skill's steps or pitfalls contain `npm publish` — a pack about unauthorised publication must not instruct the reader to publish.

## Phases and counts

| Phase | Skills | Focus |
|---|---|---|
| `recon` | 5 | manifests, registry metadata, resolved tree, CI install path, private scope map |
| `registry` | 5 | scope claim, maintainer change, yank/republish, tarball vs tag, new-package triage |
| `confusion` | 6 | internal name enumeration, resolution order, scope pinning, version arithmetic, build-log evidence, fix verification |
| `typosquat` | 5 | edit distance, homoglyphs, keyboard adjacency, undeclared imports, static triage |
| `pinning` | 6 | exact npm pins, pip bounds, lockfile generation, integrity coverage, url/git replacement, bump review |
| `scripts` | 5 | hook inventory, two-phase install, behaviour diff, allowlist policy, CI enforcement |
| `provenance` | 5 | attestation check, reproducible rebuild, signature identity, missing-attestation triage, tag match |
| `ci` | 5 | token least privilege, cache keys, fork workflows, secret exposure, dependency gate |
| `tools` | 4 | run the scan, suppression with a reason, SBOM, origin and licence |
| `review` | 4 | evidence, severity basis, fix verification, disclosure timeline |

## Repository layout

```
src/deptrial/
  model.py       immutable Skill shape and dict loader
  validate.py    the 9 per-skill rules and the package rules
  render.py      deterministic SKILL.md, catalog and manifest rendering
  manifests.py   discovery, parsers, source and binding classification
  rules.py       DT001..DT010, ordering, severity ranking, text report
  cli.py         every command, including scan
  corpus/        50 authored skills in part1..part3
examples/
  vulnerable/    npm + pip manifests that trip seven high and eight medium findings
  hardened/      exact pins plus a lockfile with integrity: zero findings
skills/          50 generated SKILL.md files, byte-identical to a fresh render
results/         catalog.md and demo_transcript.txt
pack.json        manifest of 50 slugs with sha256 digests
tests/           91 tests: corpus rules, artifact drift, parsers, classifiers, rules, CLI
```

## Guarantees the tests actually check

- `validate_pack(PACK, SKILLS) == []`, 50/50, all 10 phases, at least 3 skills per phase.
- Every committed skill equals a fresh render byte for byte; every `pack.json` digest matches its file.
- `build_pack` is deterministic and produces 52 artifacts.
- `^1.2.3` floats, `1.2.3` and `=1.2.3` do not, `>=1.0.0 <2.0.0` is bounded, `1.x` and `*` are wildcards.
- `git+`, `github:` and `ssh://` classify as vcs; `http(s)://` as url; `workspace:` and `file:` as local.
- A pip line with `#egg=` takes its name from the egg fragment, otherwise from the repository basename.
- `DT004` fires only when an internal prefix is supplied and the name is not exact-pinned.
- `DT005` fires only with an allowlist, never for an exact match, and reports the distance.
- The hardened example produces zero findings; the vulnerable one produces seven high.
- Discovery ignores `node_modules`; a missing target raises rather than returning an empty report.
- `scan` exits 1 above the threshold, 0 below it, and 2 for a bad threshold, bad distance or missing path.

## Limits

- **No registry access.** The scanner reads local files only. It cannot tell whether a name is registered publicly; `recon-enumerate-internal-names` says to check that, and `DT004` fires on the local shape of the risk.
- **Transitive dependencies are not scanned.** Only manifests are parsed, so a risky transitive package appears only if a lockfile count reveals it (`DT010`). This is stated rather than hidden.
- **`pyproject.toml` needs Python 3.11+** for `tomllib`; on 3.10 that parser returns nothing and the other formats still work.
- **Lockfile integrity counting is per format and approximate** for `yarn.lock` and `pnpm-lock.yaml`, where it counts markers rather than parsed entries.
- **`DT005` is only as good as the allowlist.** An empty allowlist disables the rule, and a stale allowlist misses renames.
- **No skill here publishes anything.** Every check is read-only against registries in the sense that it fetches metadata or tarballs; no skill tells you to claim a public name.
- **The examples are fixtures, not live scans.** `example.invalid` is a reserved domain; the git URLs are not fetched by anything in this repository.

## License

MIT.
