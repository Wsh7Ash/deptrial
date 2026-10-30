---
name: registry-scope-claim-check
description: "Look up the scope on the public registry before you trust it, because an unclaimed scope lets anyone publish under your own namespace. Use when the project depends on scoped packages such as @acme/design-tokens"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [registry, scope, namespace]
phase: registry
---

# Check whether a private scope is claimed publicly

> Look up the scope on the public registry before you trust it, because an unclaimed scope lets anyone publish under your own namespace

**Use when:** the project depends on scoped packages such as @acme/design-tokens

**Avoid when:** the scope is an organisation on the public registry with enforced membership

## Procedure

1. Query the public registry for the organisation that owns the scope.
2. If it resolves, record the owning user or org and its member list visibility.
3. If it does not resolve, record that the scope is unclaimed, which is the finding.
4. Attempt nothing further on the public registry; the check is read-only.

## Signals

- scope-query-answered
- owner-recorded
- claim-status-recorded

## Patterns

**1. scope lookup**

```
curl -sS -o /dev/null -w '%{http_code}\n' https://registry.npmjs.org/-/org/acme/user
```

## Pitfalls

- Reporting an unclaimed scope as exploitable without confirming the private package name is used unresolved.
- Publishing anything to prove the claim; that is a change to a third-party system and out of scope.

## Done when

- Each scope in use has a recorded claim status and owner.
- Any unclaimed scope is linked to the packages that depend on it.

## References

- [npm organizations](https://docs.npmjs.com/organizations)
