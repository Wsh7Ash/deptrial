---
name: pinning-lockfile-generate
description: "Produce a lockfile that records every resolved version with its integrity hash, because without one two installs of the same commit are two different dependency trees. Use when manifests exist and no lockfile does"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [pinning, lockfile, reproducible]
phase: pinning
---

# Generate and commit a lockfile

> Produce a lockfile that records every resolved version with its integrity hash, because without one two installs of the same commit are two different dependency trees

**Use when:** manifests exist and no lockfile does

**Avoid when:** the deployable is a library that deliberately leaves resolution to its consumers

## Procedure

1. Generate the lockfile with the package manager the project actually uses, not a different one.
2. Commit it and enable the CI flag that fails the build when it is out of date.
3. Re-install from a clean cache and confirm the resolved versions match.
4. Record the lockfile hash in the review notes.

## Signals

- lockfile-generated
- ci-flag-enabled
- clean-install-matches

## Patterns

**1. generate and enforce**

```
npm install --package-lock-only
git add package-lock.json
npm ci --ignore-scripts
```

## Pitfalls

- Committing a lockfile generated on another platform, whose optional dependencies differ.
- Leaving the lockfile out of the container build context so the image resolves fresh.

## Done when

- The lockfile is committed and CI refuses to install without it.
- A clean install resolves exactly the locked versions.

## References

- [npm ci](https://docs.npmjs.com/cli/commands/npm-ci)
