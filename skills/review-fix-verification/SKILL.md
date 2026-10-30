---
name: review-fix-verification
description: "Re-run the scan and the resolution trace after the fix and compare with the pre-fix record, because a pin that was added in one manifest and forgotten in another closes nothing. Use when remediation has been merged"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [review, verification, fix]
phase: review
---

# Verify the dependency fix with the same evidence

> Re-run the scan and the resolution trace after the fix and compare with the pre-fix record, because a pin that was added in one manifest and forgotten in another closes nothing

**Use when:** remediation has been merged

**Avoid when:** the fix has not reached an environment you can test

## Procedure

1. Re-run the same scan command with the same options against the fixed commit.
2. Compare the finding counts per rule with the pre-fix record.
3. Re-run the resolution trace for the specific package and confirm the new source.
4. Record any finding that remains, with the reason it was not fixed.

## Signals

- scan-rerun
- counts-compared
- trace-confirmed

## Patterns

**1. before and after**

```
deptrial scan . --fail-on high --json > after.json
jq -S '.by_rule' before.json after.json
```

## Pitfalls

- Re-running with a different allowlist, which changes the findings for reasons unrelated to the fix.
- Accepting a reduced count as proof when the specific package still resolves publicly.

## Done when

- The per-rule counts before and after are both recorded.
- The specific package's resolution is shown to have changed.

## References

- [NIST SP 800-40 patch management](https://csrc.nist.gov/pubs/sp/800/40/r4/final)
