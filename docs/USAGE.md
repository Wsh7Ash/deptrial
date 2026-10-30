# Usage

## Install

```bash
python -m pip install -e .
deptrial --version
```

Or run without installing, from the repository root:

```bash
PYTHONPATH=src python -m deptrial validate
```

## First pass over a repository

Start with the facts you can supply: the internal name prefixes and the trusted names.

```bash
deptrial scan . \
  --internal-prefix 'internal-' --internal-prefix '@acme/' \
  --allowlist react --allowlist lodash --allowlist express \
  --json > deptrial.json
```

Read the report grouped by rule rather than by file:

```bash
jq '.by_rule' deptrial.json
```

A rule that fired forty times is a systemic decision (nobody pins anything), not forty separate bugs. Triage it as one, with one fix.

## Worked example: is this internal package confusable?

1. **Map the names.** `deptrial show recon-private-scope-map` — collect names the organisation treats as internal, with the registry each is meant to come from.
2. **Check the public side.** `deptrial show recon-registry-metadata` and `deptrial show registry-scope-claim-check`. The question is not whether the package exists publicly, it is whether anything prevents someone else from publishing it.
3. **Localise the risk.** Run the scan with the prefix:

   ```bash
   deptrial scan . --internal-prefix '@acme/' --fail-on high
   ```

   `DT004` fires for an internal name declared with a non-exact binding — the shape that lets a public 99.0.0 outrank your private 1.x.

4. **Prove the resolution.** `deptrial show confusion-resolution-order`. Config alone is not evidence; a resolver trace naming the URL that answered is.
5. **Fix and verify.** `deptrial show confusion-scope-pinning`, then `deptrial show confusion-fix-verification`: re-run the same trace and store the before/after pair.

## Worked example: an install hook in a release job

1. **Inventory the hooks.** `deptrial show scripts-inventory-hooks`, or let the scanner do it:

   ```bash
   deptrial scan . --fail-on high | grep DT003
   ```

2. **Separate arrival from execution.** `deptrial show scripts-sandbox-install`: install with `--ignore-scripts`, snapshot, then run hooks only in a container with no credentials.
3. **Check what the job can do.** `deptrial show ci-secret-exposure` and `deptrial show ci-token-least-privilege`. `DT003` is a note in a test job and a serious finding in a job that can publish.
4. **Gate it.** `deptrial show scripts-allowlist-policy`, then `deptrial show scripts-ci-enforcement` so a new hook fails the build.

## Using it as a required check

```yaml
- name: dependency trust
  run: |
    deptrial scan . \
      --internal-prefix '@acme/' \
      --allowlist react --allowlist lodash \
      --fail-on high
```

Exit 1 blocks the merge. Choose the threshold deliberately and write the reason in a comment on the workflow: a gate that fails on every finding gets disabled within a week, and a disabled gate is worse than none because it looks like one.

## Working with the corpus

```bash
deptrial validate     # must be 50/50
deptrial build        # rewrites skills/, pack.json, results/catalog.md
python -m pytest -q   # artifact drift, digests, parsers, rules, CLI
```

Every skill lives in `src/deptrial/corpus/part1..part3.py`. Removing one means removing it from the corpus *and* rebuilding, or `test_committed_skills_match_a_fresh_render` fails on the leftover directory — which is the intended behaviour.

## Using the skills from an agent runtime

Point the runtime at `skills/`. Each file begins with YAML front-matter:

```yaml
---
name: confusion-resolution-order
description: "Show how the client resolves a name when both the private and the public registry can answer ... Use when a name is unregistered publicly"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [confusion, resolution, registries]
phase: confusion
---
```

A runtime that selects by description matches on the summary plus the `use_when` clause.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success, or no finding at or above `--fail-on` |
| 1 | validation failed, or `scan` found a finding at or above the threshold |
| 2 | usage error: unknown command, unknown slug, bad threshold, bad distance, missing path |
