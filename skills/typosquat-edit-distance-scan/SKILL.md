---
name: typosquat-edit-distance-scan
description: "Compute edit distance between every declared name and the names you actually trust, because a substitution or a missing hyphen is the cheapest way to be installed by accident. Use when the project declares many dependencies and nobody has reviewed the names recently"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [typosquat, distance, scan]
phase: typosquat
---

# Scan a manifest for names one edit away from trusted ones

> Compute edit distance between every declared name and the names you actually trust, because a substitution or a missing hyphen is the cheapest way to be installed by accident

**Use when:** the project declares many dependencies and nobody has reviewed the names recently

**Avoid when:** the dependency set is small enough to read line by line

## Procedure

1. Collect the trusted names from the organisation's own allowlist, not from the manifest under test.
2. Normalise case, underscores and dots before comparing, since registries treat them as equivalent variants.
3. Compute edit distance for each declared name against the allowlist and keep distances of one and two.
4. Record each near miss with both names and the distance.

## Signals

- allowlist-collected
- distances-computed
- near-misses-listed

## Patterns

**1. deptrial**

```
deptrial scan . --allowlist react --allowlist lodash --allowlist express --fail-on high
```

## Pitfalls

- Using the manifest itself as the allowlist, which makes every name trivially trusted.
- Flagging a legitimate short name that happens to be close to another short name without checking its history.

## Done when

- Every declared name has a recorded minimum distance to the allowlist.
- Near misses are listed with distance and publish date.

## References

- [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
