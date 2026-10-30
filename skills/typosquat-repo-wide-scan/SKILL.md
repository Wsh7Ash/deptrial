---
name: typosquat-repo-wide-scan
description: "Search source files for import statements naming packages absent from every manifest, because an undeclared import still resolves at runtime and nothing in the dependency review sees it. Use when the project has dynamic imports or a history of ad-hoc installs"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [typosquat, imports, undeclared]
phase: typosquat
---

# Scan imports, not just manifests

> Search source files for import statements naming packages absent from every manifest, because an undeclared import still resolves at runtime and nothing in the dependency review sees it

**Use when:** the project has dynamic imports or a history of ad-hoc installs

**Avoid when:** the build fails closed on any unresolved import

## Procedure

1. Extract import specifiers from source files and strip relative paths.
2. Diff that set against declared dependencies and their transitive closure.
3. Record each undeclared name with the file and line that imports it.
4. Check each undeclared name for near-miss distance against the allowlist.

## Signals

- imports-extracted
- diff-produced
- undeclared-listed

## Patterns

**1. import scan**

```
grep -rhoE "(from|require\()\s*['\"][^.'\"][^'\"]*['\"]" src \
  | sed -E "s/.*['\"]([^'\"]+)['\"].*/\1/" | cut -d/ -f1 | sort -u > imports.txt
```

## Pitfalls

- Counting scoped names as their first path segment and losing the scope.
- Ignoring aliases configured in the bundler, which produce false positives for internal paths.

## Done when

- Every undeclared import has a file and line recorded.
- Each one is either added to the manifest or removed from the source.

## References

- [npm package.json dependencies](https://docs.npmjs.com/cli/configuring-npm/package-json#dependencies)
