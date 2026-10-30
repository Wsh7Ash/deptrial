---
name: provenance-source-tag-match
description: "Check that the version string corresponds to a commit in the repository it claims, because a version published from a working tree has no reviewable history behind it. Use when the package names a repository and you need to tie the artifact to a reviewable commit"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [provenance, tags, commit]
phase: provenance
---

# Confirm the published version matches a real tag

> Check that the version string corresponds to a commit in the repository it claims, because a version published from a working tree has no reviewable history behind it

**Use when:** the package names a repository and you need to tie the artifact to a reviewable commit

**Avoid when:** the package is registry-only with no repository field

## Procedure

1. Read the repository field and the version from the tarball's manifest.
2. Fetch the tags from that repository and record whether the version has one.
3. Compare the tag's tree with the tarball's file list.
4. Record a version with no tag as an unverifiable publication.

## Signals

- repository-read
- tag-existence-recorded
- tree-compared

## Patterns

**1. tag check**

```
git ls-remote --tags https://github.com/ORG/PKG | grep -E 'refs/tags/v?1\.2\.3$' || echo 'no matching tag'
```

## Pitfalls

- Matching a tag by substring, so v1.2.30 satisfies a search for v1.2.3.
- Assuming a tag is immutable, when it can be moved or recreated.

## Done when

- The tag for the pinned version is recorded as present or absent.
- A present tag is compared with the tarball contents, not just its name.

## References

- [git ls-remote](https://git-scm.com/docs/git-ls-remote)
