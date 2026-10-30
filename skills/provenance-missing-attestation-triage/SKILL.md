---
name: provenance-missing-attestation-triage
description: "Turn an absent provenance statement into a proportionate decision instead of a blanket finding, because most of the ecosystem has none and a report that says so about every package is noise. Use when a load-bearing dependency has no attestation"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [provenance, triage, risk]
phase: provenance
---

# Decide what to do about a missing attestation

> Turn an absent provenance statement into a proportionate decision instead of a blanket finding, because most of the ecosystem has none and a report that says so about every package is noise

**Use when:** a load-bearing dependency has no attestation

**Avoid when:** the dependency has an attestation that already verifies

## Procedure

1. Record what the package can do: install hooks, network access at runtime, filesystem writes.
2. Record compensating controls: lockfile integrity, script allowlist, sandboxed build.
3. Decide by capability rather than by popularity: a package that runs code at install with no integrity pin is the priority.
4. Write the decision with the two facts it is based on.

## Signals

- capabilities-recorded
- controls-recorded
- decision-written

## Patterns

**1. capability summary**

```
jq '{scripts: (.scripts // {}), deps: (.dependencies // {} | keys)}' /tmp/scratch/package/package.json
```

## Pitfalls

- Ranking by download count instead of by what the package is allowed to do.
- Recording a missing attestation without naming the control that compensates for it.

## Done when

- The decision names the capability and the compensating control.
- Prioritisation across packages is consistent with the same two facts.

## References

- [SLSA provenance](https://slsa.dev/provenance)
