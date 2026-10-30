---
name: registry-maintainer-change
description: "Compare the maintainer list across the versions you depend on, because a package that gained a maintainer six weeks ago is a different trust proposition than the one in your review notes. Use when the dependency was pinned long ago and nobody has re-reviewed it"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [registry, maintainers, ownership]
phase: registry
---

# Detect a maintainer or ownership change

> Compare the maintainer list across the versions you depend on, because a package that gained a maintainer six weeks ago is a different trust proposition than the one in your review notes

**Use when:** the dependency was pinned long ago and nobody has re-reviewed it

**Avoid when:** the package has a single maintainer and always has

## Procedure

1. Fetch the registry document and record the maintainer list with the current version.
2. Fetch the same fields for the version you have pinned.
3. Diff the two lists and record additions and removals with publish dates.
4. For an addition, record the new maintainer's other packages, which is how a takeover is recognised.

## Signals

- maintainer-diff-recorded
- dates-captured
- other-packages-listed

## Patterns

**1. maintainer diff**

```
curl -sS https://registry.npmjs.org/PKG | jq -r '.versions[.\"dist-tags\".latest].maintainers[]?.name' | sort > now.txt
diff pinned.txt now.txt || true
```

## Pitfalls

- Treating an added maintainer as malicious without evidence; it is a reason to look, not a finding.
- Comparing only the latest version, so a change that happened before your pin is missed.

## Done when

- The maintainer list for both versions is recorded with dates.
- Any addition is either explained or escalated.

## References

- [npm provenance](https://docs.npmjs.com/generating-provenance-statements)
