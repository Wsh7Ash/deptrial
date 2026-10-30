---
name: tools-origin-and-licence-check
description: "Record the origin and licence of every direct dependency, because a package that mirrors another's source can be swapped later and a licence change is often the first visible sign. Use when you are assembling the trust record for a service"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [tools, origin, licence]
phase: tools
---

# Check where each dependency actually comes from

> Record the origin and licence of every direct dependency, because a package that mirrors another's source can be swapped later and a licence change is often the first visible sign

**Use when:** you are assembling the trust record for a service

**Avoid when:** the dependency set is a handful of first-party workspaces

## Procedure

1. For each direct dependency, record the repository URL from the registry document and from the tarball manifest.
2. Record a mismatch between the two, which is how a fork is detected.
3. Record the licence string from the tarball and compare it with the repository.
4. Flag packages whose repository is a fork or a mirror rather than the canonical source.

## Signals

- origins-recorded
- mismatches-listed
- licences-compared

## Patterns

**1. origin comparison**

```
jq -r '.repository.url' /tmp/scratch/package/package.json
curl -sS https://registry.npmjs.org/PKG | jq -r '.repository.url'
```

## Pitfalls

- Trusting the registry's repository field, which the publisher controls.
- Treating a licence mismatch as a legal question and not recording it at all.

## Done when

- Every direct dependency has both origin values recorded.
- Mismatches are listed with the file that shows them.

## References

- [SPDX licence list](https://spdx.org/licenses/)
