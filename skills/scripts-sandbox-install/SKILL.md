---
name: scripts-sandbox-install
description: "Separate installation from execution so you can inspect what arrived before anything runs, because install-time code has no sandbox unless you build one. Use when you must resolve and inspect a dependency tree that contains hooks"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [scripts, sandbox, install]
phase: scripts
---

# Install with hooks disabled, then run them deliberately

> Separate installation from execution so you can inspect what arrived before anything runs, because install-time code has no sandbox unless you build one

**Use when:** you must resolve and inspect a dependency tree that contains hooks

**Avoid when:** the tree ships no hooks and no native build step

## Procedure

1. Install with scripts disabled and record the resolved tree.
2. Snapshot the filesystem before running any hook.
3. Run each hook in a disposable container with no credentials and no host mounts.
4. Diff the filesystem afterwards and record writes outside the project directory.

## Signals

- tree-resolved
- snapshot-taken
- diff-recorded

## Patterns

**1. two-phase install**

```
npm ci --ignore-scripts
# then, inside a disposable container only:
npm rebuild 2>&1 | tee hooks.log
```

## Pitfalls

- Running hooks on the review workstation because it is faster, with registry tokens in the environment.
- Forgetting that `npm rebuild` re-runs hooks for packages installed without them.

## Done when

- The resolved tree was produced before any hook ran.
- Hook execution happened only in a container with no credentials, and that is recorded.

## References

- [npm ignore-scripts](https://docs.npmjs.com/cli/using-npm/config#ignore-scripts)
