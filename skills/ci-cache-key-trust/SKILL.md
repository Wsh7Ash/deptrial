---
name: ci-cache-key-trust
description: "Scope caches so a pull request cannot write content the default branch later restores, because a poisoned cache is code execution that never touches the repository. Use when the pipeline caches dependencies, build output or toolchains"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [ci, cache, poisoning]
phase: ci
---

# Make cache keys unforgeable

> Scope caches so a pull request cannot write content the default branch later restores, because a poisoned cache is code execution that never touches the repository

**Use when:** the pipeline caches dependencies, build output or toolchains

**Avoid when:** the pipeline has no cache step

## Procedure

1. List every cache key and the workflow events that can write to it.
2. Confirm that caches written on a fork pull request cannot be restored by a default-branch job.
3. Include the lockfile hash in the key so a restore cannot cross a dependency change.
4. Record a test where a modified cache entry is not restored.

## Signals

- keys-listed
- write-events-recorded
- restore-tested

## Patterns

**1. hashed cache key**

```
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
```

## Pitfalls

- Using a key without the lockfile hash, so a dependency change silently restores the old tree.
- Assuming fork pull requests cannot write caches in every CI system.

## Done when

- Every cache key includes a content hash.
- A restore attempt with a modified entry is proven to miss.

## References

- [actions/cache](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
