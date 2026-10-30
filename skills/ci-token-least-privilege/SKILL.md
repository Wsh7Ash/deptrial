---
name: ci-token-least-privilege
description: "Set the workflow token permission to read-only by default and grant write only where a step needs it, because a dependency that runs at install inherits whatever the job can do. Use when the pipeline installs dependencies and the repository token has default write access"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [ci, permissions, token]
phase: ci
---

# Reduce the pipeline token to what the job needs

> Set the workflow token permission to read-only by default and grant write only where a step needs it, because a dependency that runs at install inherits whatever the job can do

**Use when:** the pipeline installs dependencies and the repository token has default write access

**Avoid when:** the pipeline already declares explicit per-job permissions

## Procedure

1. Record the repository's default workflow token permission setting.
2. Add a top-level permissions block that grants read-only for contents.
3. Grant write per job only where a publish or comment step requires it.
4. Record the effective permissions from a run's log or API, not from the file alone.

## Signals

- default-recorded
- permissions-blocked
- effective-permissions-checked

## Patterns

**1. workflow permissions**

```
permissions:
  contents: read
jobs:
  release:
    permissions:
      contents: read
      id-token: write
```

## Pitfalls

- Leaving the default write token in place because the release job needs it, which also gives every install step write access.
- Granting id-token: write at workflow level, which every job then inherits.

## Done when

- The top-level block grants read-only contents.
- Each write permission is attached to the one job that needs it.

## References

- [GitHub Actions permissions](https://docs.github.com/en/actions/reference/security/authentication-and-permissions)
