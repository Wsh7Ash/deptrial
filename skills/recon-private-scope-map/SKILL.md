---
name: recon-private-scope-map
description: "Build the list of package names your organisation treats as internal, because every name on that list is a dependency-confusion candidate the moment it is unbounded. Use when the organisation publishes private packages alongside public ones"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [recon, scope, internal]
phase: recon
---

# Map which names are supposed to be private

> Build the list of package names your organisation treats as internal, because every name on that list is a dependency-confusion candidate the moment it is unbounded

**Use when:** the organisation publishes private packages alongside public ones

**Avoid when:** every dependency is verified public and none is internal

## Procedure

1. Collect internal names from manifests, import statements and the private registry's own index.
2. Record the intended registry for each name, whether a scope or a prefix.
3. Mark names that carry no scope and no registry pin, which are the ambiguous ones.
4. Store the list as the input to the scanner's internal-prefix option rather than retyping it later.

## Signals

- internal-names-listed
- intended-registry-recorded
- unscoped-names-marked

## Patterns

**1. unscoped internal names**

```
grep -rhoE '"(internal-[a-z0-9-]+|@acme/[a-z0-9-]+)"' --include=package.json . | sort -u
```

## Pitfalls

- Treating a scoped name as safe without checking that the scope is actually claimed on the public registry.
- Missing internal names that are imported but never declared, which still resolve at runtime.

## Done when

- Every internal name is listed with its intended registry.
- The list is saved where the scanner can read it.

## References

- [npm scopes](https://docs.npmjs.com/cli/using-npm/scope)
