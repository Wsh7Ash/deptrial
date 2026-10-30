# Results

Reproducible evidence for the claims in `README.md`.

## Environment

- OS: Windows (MSYS2 shell), Python 3.14
- Runtime: Python 3.10+ standard library only; `pytest` as a dev dependency
- Network: not required at any point

## Gate 1 — corpus validation

```
$ PYTHONPATH=src python -m deptrial validate
50/50 skills valid
```

Phase distribution, measured:

```
recon 5, registry 5, confusion 6, typosquat 5, pinning 6,
scripts 5, provenance 5, ci 5, tools 4, review 4   (total 50)
```

## Gate 2 — test suite

```
$ PYTHONPATH=src python -m pytest -q
........................................................................ [ 79%]
...................                                                      [100%]
```

104 tests: 30 in `tests/test_corpus.py`, 74 in `tests/test_rules.py`, all passing.

`test_corpus.py` covers 50/50 shape, unique slugs, unique case-insensitive titles, unique summaries, all 10 phases with at least 3 skills each, the per-skill floors, HTTPS-labelled references, kebab-case slugs, no duplicate steps, committed skills equal to a fresh render byte for byte, `pack.json` digests matching their files, build determinism and the 52-artifact count, the catalog listing every slug, plus the CLI surface and its exit codes. It also asserts that no skill's steps or pitfalls contain `npm publish`.

`test_rules.py` also covers install-root boundaries: the nearest marker wins, a nested lockfile creates its own root, two repositories are never compared, a single manifest can conflict with itself, and `DT006` fires once per unlocked root. It covers the npm and pip binding classifiers (16 cases), the source classifier (8 cases), Levenshtein distance including a transposition, all three manifest parsers including a PEP 621 optional-dependency group, discovery (lockfile pairing, `node_modules` exclusion, missing target), and every rule with both a firing and a non-firing case where one exists: exact pins produce no `DT001`, an exact allowlist match produces no `DT005`, the hardened tree produces no findings at all, and `DT004` needs an internal prefix before it can fire.

## Gate 3 — build output

```
$ PYTHONPATH=src python -m deptrial build
Built 52 artifacts, 10371 rendered skill words
```

10371 words across 50 skills is a mean of 207 rendered words per skill, against a floor of 80. 52 artifacts = 50 skills + `pack.json` + `results/catalog.md`.

## Gate 4 — the scanner on the fixture trees

Vulnerable fixture (npm + pip, 14 declared dependencies):

```
$ PYTHONPATH=src python -m deptrial scan examples/vulnerable \
    --internal-prefix @acme/ --allowlist express --allowlist lodash --allowlist react --fail-on high
14 dependencies, 15 findings [high 7, medium 8, low 0]
(exit 1)
```

The seven high findings are three `DT002` (a `github:` ref, a `git+https` requirement and an https tarball), two `DT003` (preinstall and postinstall hooks), one `DT004` (`@acme/design-tokens` at `>=1.0.0`) and one `DT005` (`expres`, one edit from the allowlisted `express`). The eight medium findings are four `DT001` (floating npm ranges), one `DT006` (no lockfile), two `DT007` (empty and `*` constraints) and one `DT008` (`requests>=2.28`).

Hardened fixture (exact pins plus a lockfile with integrity on every entry):

```
$ PYTHONPATH=src python -m deptrial scan examples/hardened --fail-on high
3 dependencies, 0 findings [high 0, medium 0, low 0]
(exit 0)
```

That second result is the important one: the same rules that fire on the vulnerable tree are silent on a tree that pins exactly, ships a lockfile and carries no hooks. A scanner that only ever finds something is not measuring anything.

## Gate 5 — command surface

```
$ PYTHONPATH=src python -m deptrial rules | tail -1
10 rule(s)
```

`results/demo_transcript.txt` holds the verbatim output of `validate`, `list --phase confusion`, both scans with their exit codes, and the rule list.

## Defects found and fixed while building this pack

1. **Duplicate skill bodies.** Parts 1 and 2 both defined the pinning and scripts
   skills, so the pack loaded 61 skills with 11 duplicate slugs. Fixed by trimming
   part 1 to its own 21 skills; `validate_pack` caught it, which is what the
   duplicate-slug rule is for.
2. **`=1.2.3` classified as floating.** An npm equality constraint was treated as
   a range, which made `DT001` fire on an exact pin. Fixed to classify as exact.
3. **A pip vcs requirement took its name from the whole URL.** `git+https://...`
   without an `#egg=` fragment produced a "package name" that was the URL, so the
   finding's subject was unreadable. Fixed to use the egg fragment when present
   and the repository basename otherwise.
4. **Parenthetical plurals in the report footer** (`14 dependenc(ies), 15
   finding(s)`), which is noise in output a reviewer pastes into a ticket. Fixed
   to proper singular/plural.
5. **Three of my own tests asserted the wrong contract**: `lodash`/`loadsh` is two
   edits not one, `DT004` correctly skips an exactly pinned name, and the
   vulnerable fixture initially contained no near-miss name at all. The fixture
   gained `expres`, and the tests were corrected to the real behaviour rather than
   the implementation being bent to match them.
6. **A hardcoded finding count in a test** that depended on which options were
   passed. Replaced with an assertion computed from the report itself.

## Gate 6 — install roots on this workspace

The scanner was run against a 146-manifest workspace before and after the install-root
change, from the same commit of the tree:

| Rule | Before | After | Meaning |
|---|---|---|---|
| `DT009` | 11 | **0** | all 11 groups spanned unrelated repositories |
| `DT006` | 0 | **132** | one lockfile anywhere had silenced the rule for every project |
| `DT001` | 15 | 15 | unchanged |
| `DT008` | 117 | 117 | unchanged |
| `DT007` | 1 | 1 | unchanged |

Elapsed time for the scan stayed under one second after the walk was pruned.

## What was not run

- **No registry was contacted.** The scanner has no registry client; `DT004` fires on
  the local shape of the risk, not on a confirmed public registration.
- **No dependency was installed**, so no lifecycle hook was executed. The hooks in
  the fixture are strings the scanner reports, not commands this repository runs.
- **Transitive dependencies were not scanned.** Only manifests are parsed.
- **`pyproject.toml` parsing was exercised on Python 3.14** (`tomllib` present). The
  3.10 fallback returns no dependencies and is not covered by a passing test.
- **`yarn.lock` and `pnpm-lock.yaml` integrity counting** is marker-based and was
  exercised only on the npm `package-lock.json` fixture.
