---
name: pinning-exact-npm
description: "Replace caret and tilde ranges with exact versions where a lockfile is not the only control, because a range is a promise to accept code you have not reviewed. Use when a package is installed without a lockfile, such as a global tool or a standalone script"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [pinning, npm, exact]
phase: pinning
---

# Pin npm dependencies exactly

> Replace caret and tilde ranges with exact versions where a lockfile is not the only control, because a range is a promise to accept code you have not reviewed

**Use when:** a package is installed without a lockfile, such as a global tool or a standalone script

**Avoid when:** a committed lockfile with integrity hashes already governs the install

## Procedure

1. List every dependency whose constraint is not an exact version.
2. Replace each range with the exact version currently resolved, which is the version running in production today.
3. Re-install and confirm the resolved tree is unchanged apart from the constraint strings.
4. Record the resolved tree before and after as the change evidence.

## Signals

- ranges-listed
- pins-applied
- tree-compared

## Patterns

**1. exact version**

```
npm pkg set dependencies.lodash=4.17.21
npm install --package-lock-only
```

## Pitfalls

- Pinning everything in one commit, which makes a regression impossible to bisect.
- Pinning to a version that was never in the lockfile, which silently upgrades the tree.

## Done when

- No dependency in scope has a floating range.
- The resolved tree is identical apart from the manifest constraints.

## References

- [npm semantic versioning](https://docs.npmjs.com/about-semantic-versioning)
