---
name: registry-yank-republish
description: "Look for versions that were unpublished then republished with different content, because a lockfile pin to that version no longer identifies the bytes you reviewed. Use when the lockfile pins exact versions and the project installs from the public registry"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [registry, yank, republish]
phase: registry
---

# Check for a yanked version that came back

> Look for versions that were unpublished then republished with different content, because a lockfile pin to that version no longer identifies the bytes you reviewed

**Use when:** the lockfile pins exact versions and the project installs from the public registry

**Avoid when:** your registry mirror pins by digest and refuses re-published content

## Procedure

1. For each pinned version, record the dist integrity value from the registry document.
2. Compare it with the integrity recorded in the lockfile.
3. Where they differ, record both and the publish time, which is the evidence of a republish.
4. Re-run the install in a clean cache and confirm which bytes arrive.

## Signals

- integrity-compared
- mismatch-recorded
- clean-install-confirmed

## Patterns

**1. compare pin with registry**

```
jq -r '.packages["node_modules/PKG"].integrity' package-lock.json
curl -sS https://registry.npmjs.org/PKG/1.2.3 | jq -r '.dist.integrity'
```

## Pitfalls

- Comparing integrity for the wrong version because the lockfile resolved a different one.
- Reporting a mismatch caused by a private mirror rewriting tarballs.

## Done when

- Every pinned version in scope has both integrity values recorded.
- Mismatches are either explained by the mirror or raised.

## References

- [npm dist.integrity](https://docs.npmjs.com/cli/using-npm/registry)
