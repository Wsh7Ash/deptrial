---
name: confusion-enumerate-internal-names
description: "Produce the exact list of internal package names that have no public registration, because that list is the attack surface for dependency confusion. Use when the organisation runs a private registry next to a public one"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [confusion, enumeration, internal]
phase: confusion
---

# Enumerate the internal names that are resolvable publicly

> Produce the exact list of internal package names that have no public registration, because that list is the attack surface for dependency confusion

**Use when:** the organisation runs a private registry next to a public one

**Avoid when:** the build resolves every dependency through one locked registry

## Procedure

1. Collect internal names from manifests, lockfiles and import statements.
2. Query the public registry for each name and record the status code.
3. Record names that return 404 as unregistered, which is the candidate set.
4. Record names that resolve but whose maintainer is not your organisation, which is the stronger case.

## Signals

- names-collected
- status-codes-recorded
- unregistered-listed

## Patterns

**1. public registration check**

```
while read -r n; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' --get --data-urlencode "x=1" "https://registry.npmjs.org/$n")
  printf '%s %s\n' "$code" "$n"
done < internal-names.txt
```

## Pitfalls

- Querying names for packages that are already scoped to a private registry, which cannot be confused.
- Publishing a placeholder to prove the gap; that is an unauthorised change to a public registry.

## Done when

- Every internal name has a recorded public status.
- Unregistered names are listed and tied to the manifests that declare them.

## References

- [Dependency confusion](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610)
