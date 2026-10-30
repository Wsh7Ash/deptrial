---
name: provenance-attestation-check
description: "Look for a signed provenance statement that ties the tarball to a source repository and commit, because an attestation is the only claim a registry makes about where the bytes came from. Use when the dependency runs at install time or ships compiled code"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [provenance, attestation, registry]
phase: provenance
---

# Check whether a package publishes a build attestation

> Look for a signed provenance statement that ties the tarball to a source repository and commit, because an attestation is the only claim a registry makes about where the bytes came from

**Use when:** the dependency runs at install time or ships compiled code

**Avoid when:** the registry in use has no provenance support

## Procedure

1. Fetch the version document for the pinned version and record whether a provenance or attestation field exists.
2. Record the source repository, commit and build workflow the attestation names.
3. Compare that commit with the tag the version claims to be.
4. Record a missing attestation as a fact, not as a finding on its own.

## Signals

- attestation-presence-recorded
- commit-captured
- tag-compared

## Patterns

**1. attestation lookup**

```
curl -sS https://registry.npmjs.org/PKG/1.2.3 | jq '{dist: .dist.attestations, repo: .repository}'
```

## Pitfalls

- Treating the absence of an attestation as evidence of compromise, when most packages have none.
- Reading the attestation from the latest version instead of the pinned one.

## Done when

- The pinned version's attestation status and named commit are recorded.
- Any mismatch between the named commit and the tag is raised.

## References

- [npm attestations](https://docs.npmjs.com/generating-provenance-statements)
