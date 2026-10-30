---
name: typosquat-keyboard-adjacent
description: "Catch the mistyped-but-plausible names that edit distance misses, because swapping two adjacent keys produces a different string at the same length and often a real registered package. Use when the team installs dependencies by typing them rather than copying from documentation"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [typosquat, keyboard, typo]
phase: typosquat
---

# Check keyboard-adjacent misspellings

> Catch the mistyped-but-plausible names that edit distance misses, because swapping two adjacent keys produces a different string at the same length and often a real registered package

**Use when:** the team installs dependencies by typing them rather than copying from documentation

**Avoid when:** dependencies are added only through a reviewed lockfile change

## Procedure

1. Build the keyboard-adjacency pairs for the layout the team uses.
2. For each trusted name, generate the single-key substitution and transposition variants.
3. Check which variants are registered and, for those, whether they are recent.
4. Record registered variants with publish date and maintainer count.

## Signals

- variants-generated
- registration-checked
- dates-recorded

## Patterns

**1. adjacent pair check**

```
for v in lodahs lodasj lodashh; do printf '%s %s\n' "$(curl -sS -o /dev/null -w '%{http_code}' https://registry.npmjs.org/$v)" "$v"; done
```

## Pitfalls

- Generating thousands of variants against the public registry and getting rate limited mid-scan.
- Treating every registered variant as malicious when most are abandoned placeholders.

## Done when

- Registered variants are listed with dates and maintainers.
- Rate-limit behaviour during the scan is recorded.

## References

- [npm registry API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)
