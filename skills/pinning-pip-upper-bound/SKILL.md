---
name: pinning-pip-upper-bound
description: "Add a compatible-release or an explicit ceiling to a lower-bound-only requirement, because a bare `>=` accepts every future major version including one that is hostile. Use when a requirements file declares a lower bound with no upper bound"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [pinning, pip, bounds]
phase: pinning
---

# Give a pip requirement an upper bound

> Add a compatible-release or an explicit ceiling to a lower-bound-only requirement, because a bare `>=` accepts every future major version including one that is hostile

**Use when:** a requirements file declares a lower bound with no upper bound

**Avoid when:** the package is pinned by a lockfile with hashes and a policy of never breaking

## Procedure

1. List requirements that declare only a lower bound.
2. Choose the style: a compatible release for a stable package, an explicit ceiling for one with a history of breaking changes.
3. Re-resolve and confirm the installed version is unchanged.
4. Record the version before and after for every changed requirement.

## Signals

- unbounded-listed
- bounds-chosen
- resolution-compared

## Patterns

**1. bounded requirements**

```
requests>=2.28,<3
numpy>=1.26,<2
```

## Pitfalls

- Choosing a ceiling below the version you actually run, which downgrades production.
- Adding a ceiling that no released version satisfies, which fails the build later.

## Done when

- Every requirement in scope has an upper bound.
- The installed versions are unchanged by the edit.

## References

- [PEP 440 version specifiers](https://peps.python.org/pep-0440/#version-specifiers)
