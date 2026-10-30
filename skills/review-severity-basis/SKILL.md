---
name: review-severity-basis
description: "Rate a finding by what the compromised package or job could do in this specific pipeline, because the same missing pin is a critical finding in a release job and a note in a test job. Use when you are assigning severity to a supply-chain finding"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [review, severity, impact]
phase: review
---

# Justify severity from capability, not from rule name

> Rate a finding by what the compromised package or job could do in this specific pipeline, because the same missing pin is a critical finding in a release job and a note in a test job

**Use when:** you are assigning severity to a supply-chain finding

**Avoid when:** the finding has no execution path in the affected environment

## Procedure

1. Record what the affected job or runtime can reach: secrets, registry tokens, production network, signing keys.
2. Record whether the dependency executes code at install or only at runtime.
3. State the impact in one sentence with the reachable asset named.
4. Show the same rule in a lower-privilege job to demonstrate the difference.

## Signals

- capability-recorded
- execution-point-recorded
- asset-named

## Patterns

**1. severity note**

```
Rule: DT003 (install hook)
Job: release (contents: write, NPM_TOKEN)
Impact: install-time code can publish to the registry under the org scope
```

## Pitfalls

- Copying severity from a scanner's default rating, which knows nothing about the job.
- Rating by the number of downloads rather than the reachable asset.

## Done when

- The severity cites a reachable asset and an execution point.
- A contrasting lower-privilege case is recorded.

## References

- [CVSS v4](https://www.first.org/cvss/v4-0/specification-document)
