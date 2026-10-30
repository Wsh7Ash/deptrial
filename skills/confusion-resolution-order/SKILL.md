---
name: confusion-resolution-order
description: "Show how the client resolves a name when both the private and the public registry can answer, because the answer decides whether the finding is real. Use when a name is unregistered publicly and the client is configured with two registries"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [confusion, resolution, registries]
phase: confusion
---

# Prove which registry wins for one name

> Show how the client resolves a name when both the private and the public registry can answer, because the answer decides whether the finding is real

**Use when:** a name is unregistered publicly and the client is configured with two registries

**Avoid when:** the client is pinned to a single registry with no fallback

## Procedure

1. Read the effective npm config for the project, including .npmrc and any environment override.
2. Record the registry for the exact scope or prefix, not just the default registry.
3. Resolve one dependency with verbose logging and capture which URL answered.
4. Record the resolver output as the evidence, with the version it chose.

## Signals

- effective-config-recorded
- url-captured
- version-recorded

## Patterns

**1. resolution trace**

```
npm config get registry
npm view internal-billing-client version --loglevel=silly 2>&1 | grep -E 'http fetch|registry' | head -20
```

## Pitfalls

- Reading the global .npmrc and missing the project one, which usually wins.
- Concluding the finding from config alone instead of a resolution trace.

## Done when

- The registry that answered for the name is quoted from the log.
- The chosen version is recorded with its source URL.

## References

- [npm config](https://docs.npmjs.com/cli/using-npm/config)
