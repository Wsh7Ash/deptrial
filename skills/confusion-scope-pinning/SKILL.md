---
name: confusion-scope-pinning
description: "Configure the client so a scope can only ever come from the private registry, which removes the fallback that makes confusion possible. Use when the organisation publishes under a scope and wants the gap closed rather than monitored"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [confusion, scope, fix]
phase: confusion
---

# Pin a private scope to one registry

> Configure the client so a scope can only ever come from the private registry, which removes the fallback that makes confusion possible

**Use when:** the organisation publishes under a scope and wants the gap closed rather than monitored

**Avoid when:** the packages are unscoped and cannot be renamed to a scope

## Procedure

1. Add a scoped registry line for the organisation's scope, with no default fallback for it.
2. Set the token for that scope only, never globally.
3. Verify by resolving a package in the scope and confirming the private URL answered.
4. Record the before and after resolution traces as the fix evidence.

## Signals

- scope-configured
- token-scoped
- resolution-verified

## Patterns

**1. .npmrc**

```
@acme:registry=https://npm.acme.internal/
//npm.acme.internal/:_authToken=${NPM_TOKEN}
always-auth=true
```

## Pitfalls

- Leaving a corporate proxy as the default registry that mirrors public packages, which restores the fallback.
- Committing a token to .npmrc instead of reading it from the environment.

## Done when

- Resolution for the scope is proven to hit only the private URL.
- The token is environment-provided and absent from the repository.

## References

- [npm scope registry config](https://docs.npmjs.com/cli/using-npm/scope)
