---
name: scripts-allowlist-policy
description: "Turn install scripts from an open door into an allowlist, so a new hook in any dependency fails the build instead of running unreviewed. Use when the project cannot disable scripts because some dependencies need a native build"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [scripts, policy, allowlist]
phase: scripts
---

# Allow only known install hooks

> Turn install scripts from an open door into an allowlist, so a new hook in any dependency fails the build instead of running unreviewed

**Use when:** the project cannot disable scripts because some dependencies need a native build

**Avoid when:** the package manager version in use cannot restrict hooks per package

## Procedure

1. Record the packages that genuinely need an install hook, with the reason for each.
2. Enable the package manager's script restriction and allow only those packages.
3. Run a clean install and confirm the allowed hooks ran and every other hook was skipped.
4. Commit the allowlist so every addition is a visible diff.

## Signals

- allowlist-recorded
- restriction-enabled
- skip-verified

## Patterns

**1. pnpm allowlist**

```
# pnpm-workspace.yaml or package.json
onlyBuiltDependencies:
  - esbuild
  - sharp
```

## Pitfalls

- Disabling scripts globally, breaking a native dependency, then re-enabling everything.
- Leaving the allowlist out of version control so nobody reviews additions.

## Done when

- Every allowed hook is listed with a justification.
- A clean install proves unlisted hooks are skipped.

## References

- [pnpm onlyBuiltDependencies](https://pnpm.io/settings#onlybuiltdependencies)
