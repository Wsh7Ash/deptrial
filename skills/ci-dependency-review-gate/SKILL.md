---
name: ci-dependency-review-gate
description: "Run the manifest scanner as a required check so a risky dependency cannot be merged without a decision, because review of a lockfile diff is where supply-chain risk is actually accepted. Use when the repository accepts dependency changes through pull requests"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [ci, gate, scan]
phase: ci
---

# Fail the build on a new high-severity dependency finding

> Run the manifest scanner as a required check so a risky dependency cannot be merged without a decision, because review of a lockfile diff is where supply-chain risk is actually accepted

**Use when:** the repository accepts dependency changes through pull requests

**Avoid when:** dependencies are vendored and updated out of band

## Procedure

1. Add a job that runs the scanner with the project's allowlist and internal prefixes.
2. Choose the fail-on severity deliberately and write the reason in the workflow comment.
3. Make the job a required check on the default branch.
4. Record a pull request that was blocked by it and how it was resolved.

## Signals

- job-added
- severity-chosen
- block-demonstrated

## Patterns

**1. gate step**

```
- name: dependency trust
  run: deptrial scan . --allowlist react --allowlist lodash --internal-prefix 'internal-' --fail-on high
```

## Pitfalls

- Failing on every finding, so the check is disabled within a week.
- Running the gate without the internal prefix list, which hides the confusion rules.

## Done when

- The check is required and its severity threshold is justified in the file.
- A real pull request was blocked and resolved.

## References

- [Required status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
