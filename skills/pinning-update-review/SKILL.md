---
name: pinning-update-review
description: "Read the diff between the two published versions, because an automated update pull request is the easiest place to slip a new install hook past review. Use when an automated update changes a dependency version"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [pinning, updates, review]
phase: pinning
---

# Review a dependency bump before merging it

> Read the diff between the two published versions, because an automated update pull request is the easiest place to slip a new install hook past review

**Use when:** an automated update changes a dependency version

**Avoid when:** the change is a patch release from a package your own team maintains

## Procedure

1. Fetch both tarballs and diff their file lists and scripts blocks.
2. Read every change to lifecycle scripts before any other code.
3. Compare the maintainer list for the new version with the old one.
4. Record what was reviewed and what was skipped, by file name.

## Signals

- tarballs-diffed
- scripts-reviewed
- maintainers-compared

## Patterns

**1. script diff**

```
tar xzf old.tgz -C /tmp/old && tar xzf new.tgz -C /tmp/new
diff -u /tmp/old/package/package.json /tmp/new/package/package.json
```

## Pitfalls

- Approving the bump because the version looks like a patch release.
- Reviewing the repository diff instead of the published tarball diff, which differ.

## Done when

- The scripts block diff is recorded for the version pair.
- Any new install hook is either justified or the bump is rejected.

## References

- [npm diff](https://docs.npmjs.com/cli/commands/npm-diff)
