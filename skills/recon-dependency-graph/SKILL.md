---
name: recon-dependency-graph
description: "Distinguish what the manifest declares from what the lockfile actually installs, since the transitive set is where most compromise lands and it is invisible in the manifest. Use when you need to know whether a risky package is actually installed or merely declared"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [recon, transitive, graph]
phase: recon
---

# Split direct dependencies from the resolved tree

> Distinguish what the manifest declares from what the lockfile actually installs, since the transitive set is where most compromise lands and it is invisible in the manifest

**Use when:** you need to know whether a risky package is actually installed or merely declared

**Avoid when:** the project vendors no lockfile and has no installed tree to read

## Procedure

1. Produce the resolved tree from the lockfile rather than from the manifest.
2. Mark each entry direct or transitive, and record which direct dependency pulled it in.
3. Count transitive entries that come from a vcs or url source, since those bypass registry integrity.
4. Record the deepest chain length, which bounds how far a single compromised package can reach.

## Signals

- tree-produced
- direct-marked
- transitive-counted

## Patterns

**1. resolved tree**

```
npm ls --all --json > tree.json 2>/dev/null; jq '[.. | objects | select(.version?) | .version] | length' tree.json
```

## Pitfalls

- Treating a declared dependency as installed when the lockfile excludes it.
- Reporting a transitive package as reachable without naming the direct dependency that pulls it in.

## Done when

- Every risky package is labelled direct or transitive with its parent named.
- The transitive count is recorded as a number, not an impression.

## References

- [npm ls](https://docs.npmjs.com/cli/commands/npm-ls)
