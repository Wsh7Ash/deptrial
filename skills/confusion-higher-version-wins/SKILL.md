---
name: confusion-higher-version-wins
description: "Demonstrate the version arithmetic that makes confusion work, so the finding explains why a newer public release is chosen over the private package you actually wanted. Use when a range rather than an exact pin is declared for an internal name"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [confusion, version, semver]
phase: confusion
---

# Show that a higher public version outranks the private one

> Demonstrate the version arithmetic that makes confusion work, so the finding explains why a newer public release is chosen over the private package you actually wanted

**Use when:** a range rather than an exact pin is declared for an internal name

**Avoid when:** the name is exact-pinned in every manifest and lockfile

## Procedure

1. Record the constraint as declared and the private version that satisfies it.
2. Record what a semver resolution does when a much higher version exists in the other registry.
3. Show the arithmetic in the report: declared range, private max, hypothetical public max.
4. State the precondition plainly: the attacker must be able to publish under that name.

## Signals

- constraint-quoted
- private-version-recorded
- arithmetic-shown

## Patterns

**1. range vs pin**

```
jq -r '.dependencies["internal-billing-client"]' package.json   # >=1.0.0
# a public 99.0.0 satisfies the range and outranks any private 1.x
```

## Pitfalls

- Claiming the attack without the publish precondition, which makes the report unfalsifiable.
- Forgetting that an exact pin plus a lockfile removes the choice entirely.

## Done when

- The report shows the declared range and both candidate maximums.
- The precondition is stated as a precondition, not as an accomplished fact.

## References

- [semver ranges](https://github.com/npm/node-semver#ranges)
