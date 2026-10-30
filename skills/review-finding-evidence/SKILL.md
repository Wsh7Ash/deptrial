---
name: review-finding-evidence
description: "Attach the exact artifact, hash and resolution trace to a finding, because a supply-chain claim without the bytes it refers to cannot be verified after the package changes. Use when you are filing a dependency or pipeline finding"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [review, evidence, report]
phase: review
---

# Write a supply-chain finding that can be rechecked

> Attach the exact artifact, hash and resolution trace to a finding, because a supply-chain claim without the bytes it refers to cannot be verified after the package changes

**Use when:** you are filing a dependency or pipeline finding

**Avoid when:** the observation is a hypothesis you have not yet confirmed

## Procedure

1. State the package, version and tarball hash the finding refers to.
2. Attach the resolution trace or workflow excerpt that demonstrates the behaviour.
3. State the precondition the exploitation depends on, such as the ability to publish under a name.
4. Store the artifact so the finding survives a registry change.

## Signals

- artifact-hashed
- trace-attached
- precondition-stated

## Patterns

**1. finding header**

```
Package: internal-billing-client
Version: 1.2.0 (tarball sha256 ...)
Precondition: ability to publish under a name the private registry does not own
Evidence: install.log lines 41-58
```

## Pitfalls

- Quoting a version without the hash, when a republish makes the version ambiguous.
- Describing a hypothetical instead of the observed resolution.

## Done when

- The finding names an artifact by hash.
- The precondition is stated separately from the observation.

## References

- [CWE-1104 use of unmaintained third-party components](https://cwe.mitre.org/data/definitions/1104.html)
