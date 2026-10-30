---
name: registry-tarball-source-diff
description: "Download the tarball the registry serves and compare it with the matching git tag, because a published package can contain files the repository never had. Use when the package runs at install time or ships a native build step"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [registry, tarball, diff]
phase: registry
---

# Diff a published tarball against its source tag

> Download the tarball the registry serves and compare it with the matching git tag, because a published package can contain files the repository never had

**Use when:** the package runs at install time or ships a native build step

**Avoid when:** the package is a thin re-export whose published output is reproducible from the tag by inspection

## Procedure

1. Download the exact tarball for the pinned version and record its shasum.
2. Extract it into a scratch directory that is not on any load path.
3. Clone the repository at the tag the version claims and compare the two trees.
4. Report files that exist only in the tarball, and inspect any script those files are wired to.

## Signals

- tarball-hashed
- trees-compared
- extra-files-listed

## Patterns

**1. fetch and hash**

```
curl -sSL https://registry.npmjs.org/PKG/-/PKG-1.2.3.tgz -o pkg.tgz
sha256sum pkg.tgz
tar tzf pkg.tgz | sort > tarball-files.txt
```

## Pitfalls

- Extracting the tarball inside the project so its package.json shadows the real one.
- Diffing against a branch tip rather than the tag, which produces noise instead of evidence.

## Done when

- The tarball hash is recorded next to the registry's published value.
- Every file present only in the tarball is listed and explained.

## References

- [npm pack](https://docs.npmjs.com/cli/commands/npm-pack)
