---
name: confusion-fix-verification
description: "Re-run the resolution trace after the fix and confirm the public registry can no longer answer for the name, because a fix that only changes a default registry is undone by the next override. Use when the remediation claims to have pinned a scope or exact-pinned a name"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [confusion, verification, fix]
phase: confusion
---

# Verify the confusion fix after it ships

> Re-run the resolution trace after the fix and confirm the public registry can no longer answer for the name, because a fix that only changes a default registry is undone by the next override

**Use when:** the remediation claims to have pinned a scope or exact-pinned a name

**Avoid when:** the fix is not yet deployed to the environment you can test

## Procedure

1. Re-read the effective config in the fixed environment rather than the repository.
2. Re-run the same resolution trace used before the fix.
3. Confirm the public registry returns nothing for the name, or that it is never consulted.
4. Record the before and after traces side by side.

## Signals

- config-reread
- trace-rerun
- before-after-recorded

## Patterns

**1. post-fix check**

```
npm config get @acme:registry
npm view internal-billing-client version --loglevel=silly 2>&1 | grep 'http fetch' | head -5
```

## Pitfalls

- Verifying on a developer laptop whose global config differs from CI.
- Accepting a fix that removes the name from one manifest while another still declares it unbounded.

## Done when

- The trace after the fix shows only the private registry.
- Every manifest that declared the name is covered by the verification.

## References

- [npm config](https://docs.npmjs.com/cli/using-npm/config)
