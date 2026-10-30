---
name: recon-manifest-inventory
description: "List the files that decide what gets installed before you reason about any single dependency, because the manifest you read first is rarely the one that wins. Use when you are starting a review of a repository you did not write"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [recon, manifests, inventory]
phase: recon
---

# Inventory every manifest and lockfile in the tree

> List the files that decide what gets installed before you reason about any single dependency, because the manifest you read first is rarely the one that wins

**Use when:** you are starting a review of a repository you did not write

**Avoid when:** the review is scoped to one already-identified package

## Procedure

1. Find every package.json, requirements*.txt, pyproject.toml and lockfile, excluding node_modules and virtualenvs.
2. Record the directory of each one, because nested manifests are separate install roots with their own resolution.
3. Match each manifest to its lockfile, and note manifests with none.
4. Write the inventory to a file and hash it, so the review is tied to one commit.

## Signals

- manifests-listed
- lockfile-mapping-recorded
- inventory-hashed

## Patterns

**1. inventory**

```
find . -type f \( -name package.json -o -name 'requirements*.txt' \
  -o -name pyproject.toml -o -name 'package-lock.json' -o -name 'yarn.lock' \
  -o -name 'poetry.lock' -o -name 'uv.lock' \) \
  -not -path '*/node_modules/*' -not -path '*/.venv/*' | sort | tee manifests.txt
```

## Pitfalls

- Reading only the root manifest, while a service directory installs its own dependencies with different pins.
- Counting a lockfile that belongs to a different manifest in a sibling directory.

## Done when

- Every manifest has a recorded path and a lockfile association or an explicit none.
- The inventory is committed to the engagement notes.

## References

- [npm package.json](https://docs.npmjs.com/cli/configuring-npm/package-json)
