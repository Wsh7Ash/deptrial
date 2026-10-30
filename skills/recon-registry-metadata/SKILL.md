---
name: recon-registry-metadata
description: "Pull the registry document for each dependency and read maintainers, publish times and dist integrity, because the version string tells you nothing about who published it. Use when a dependency is load-bearing enough that its compromise would matter"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [recon, registry, metadata]
phase: recon
---

# Read registry metadata for the packages that matter

> Pull the registry document for each dependency and read maintainers, publish times and dist integrity, because the version string tells you nothing about who published it

**Use when:** a dependency is load-bearing enough that its compromise would matter

**Avoid when:** the package is a local workspace entry with no registry presence

## Procedure

1. Fetch the registry document for the package and store it unmodified.
2. Record the maintainers, the latest publish time and the number of published versions.
3. Compare the maintainer list with what the repository or documentation claims.
4. Record the dist integrity value so a later tarball can be compared with it.

## Signals

- registry-document-stored
- maintainers-recorded
- integrity-recorded

## Patterns

**1. npm registry document**

```
curl -sS https://registry.npmjs.org/lodash | jq '{maintainers, time: .time.modified, versions: (.versions|length)}'
```

## Pitfalls

- Trusting the version number, when a maintainer account change is the signal that matters.
- Fetching through a proxy that rewrites the document and then treating the result as authoritative.

## Done when

- The registry document is stored for every load-bearing dependency.
- Maintainer and publish-time values are in the notes, not in memory.

## References

- [npm registry API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)
