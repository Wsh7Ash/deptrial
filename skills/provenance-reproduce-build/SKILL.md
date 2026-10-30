---
name: provenance-reproduce-build
description: "Build the tagged source yourself and diff the result against the published tarball, because reproducibility turns an attestation from a claim into a check. Use when the package is pure JavaScript or Python with a deterministic build"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [provenance, reproducible, build]
phase: provenance
---

# Rebuild a package from source and compare

> Build the tagged source yourself and diff the result against the published tarball, because reproducibility turns an attestation from a claim into a check

**Use when:** the package is pure JavaScript or Python with a deterministic build

**Avoid when:** the build needs platform-specific toolchains you cannot reproduce

## Procedure

1. Clone at the exact commit the attestation or tag names.
2. Install with the project's own lockfile and build with the documented command.
3. Diff the build output against the extracted tarball, ignoring timestamps and source maps.
4. Record the files that differ and any file present in only one side.

## Signals

- commit-cloned
- build-completed
- diff-recorded

## Patterns

**1. diff build against tarball**

```
git clone --depth 1 https://github.com/ORG/PKG /tmp/src && cd /tmp/src && git checkout <sha>
npm ci --ignore-scripts && npm run build
diff -r --exclude=node_modules /tmp/src/dist /tmp/scratch/package/dist | head -40
```

## Pitfalls

- Diffing build directories that include source maps with embedded absolute paths, which always differ.
- Building at a branch tip rather than the tagged commit.

## Done when

- The differing files are listed, or the build is proven byte-identical.
- The commit used for the rebuild is recorded.

## References

- [Reproducible builds](https://reproducible-builds.org/)
