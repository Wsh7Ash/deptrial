---
name: registry-new-package-triage
description: "Decide in ten minutes whether a package that appeared last week is a legitimate dependency or a name someone registered to be installed. Use when the resolved tree contains a version published after your last review"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [registry, triage, new]
phase: registry
---

# Triage a newly published package in your tree

> Decide in ten minutes whether a package that appeared last week is a legitimate dependency or a name someone registered to be installed

**Use when:** the resolved tree contains a version published after your last review

**Avoid when:** the package predates the project and has a long publish history

## Procedure

1. Record the first publish date, the version count and the maintainer count.
2. Read the package's source for network calls, child processes and environment reads.
3. Check whether the name is one edit from a package already in the tree.
4. Record the verdict with the evidence that decided it, and keep the tarball.

## Signals

- dates-recorded
- source-read
- distance-checked

## Patterns

**1. first publish**

```
curl -sS https://registry.npmjs.org/PKG | jq -r '.time.created, (.versions|length), (.maintainers|length)'
```

## Pitfalls

- Judging by download counts, which a new malicious package can inflate cheaply.
- Opening the package's README for instructions instead of its source for behaviour.

## Done when

- The package has a verdict with three supporting facts.
- The tarball is retained so the verdict can be re-checked.

## References

- [npm registry API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)
