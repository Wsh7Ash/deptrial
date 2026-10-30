# Contributing

## Before opening a pull request

```bash
PYTHONPATH=src python -m deptrial validate   # 50/50 skills valid
PYTHONPATH=src python -m deptrial build      # regenerate skills/, pack.json, catalog
PYTHONPATH=src python -m pytest -q           # green
```

The generated artifacts are committed, so a corpus change without a rebuild fails
`test_committed_skills_match_a_fresh_render`. That failure is the point: drift between
the corpus and what a user installs is a bug.

## Adding a skill

1. Edit `src/deptrial/corpus/part1.py` … `part3.py`; skills are plain dicts with the keys
   in `REQUIRED_KEYS` (`model.py`).
2. Meet every floor honestly: 3 steps, 2 signals, 1 `(label, code)` pattern, 2 pitfalls,
   an HTTPS-labelled reference, 80 rendered words.
3. Declare a phase from the closed set in `validate.py`. If a skill fits none, open an
   issue about the phase list rather than inventing a string.
4. Keep the slug kebab-case and the title and summary unique. Uniqueness is enforced on
   all three, because a copy renamed at the slug is still a copy.
5. Never instruct the reader to publish to a public registry, claim a namespace, or
   install an untrusted package to see what it does. `test_corpus.py` enforces the first
   of those mechanically.

Replacing a skill rather than adding one keeps the count at 50; the pack is fixed-size.

## Changing a rule

Rules are identified by a stable id. If a rule changes meaning, add a new id rather than
changing the old one, because suppressions in other projects name ids.

Every rule needs three tests: a positive case, a negative case that must not fire, and
a case that pins the severity. If a rule depends on an option, add a test proving it is
inert without that option.

## Reporting a security issue in this repository

See `SECURITY.md`. Do not open a public issue for a vulnerability in the tooling.
