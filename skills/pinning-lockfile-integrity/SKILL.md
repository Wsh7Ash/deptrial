---
name: pinning-lockfile-integrity
description: "Confirm every resolved entry carries an integrity hash and that the installer checks it, because a lockfile of version numbers alone still accepts substituted bytes. Use when a lockfile exists and you are relying on it as the control"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [pinning, lockfile, integrity]
phase: pinning
---

# Verify lockfile integrity data is present and enforced

> Confirm every resolved entry carries an integrity hash and that the installer checks it, because a lockfile of version numbers alone still accepts substituted bytes

**Use when:** a lockfile exists and you are relying on it as the control

**Avoid when:** a registry mirror pins by digest independently of the client

## Procedure

1. Count resolved entries and how many carry an integrity or hash field.
2. Record the installer version, since some legacy modes skip verification.
3. Install with the lockfile enforced and confirm a deliberately corrupted entry is rejected.
4. Record both the coverage ratio and the rejection test.

## Signals

- entries-counted
- installer-version-recorded
- rejection-verified

## Patterns

**1. integrity coverage**

```
jq '[.packages | to_entries[] | select(.key != "") | select(.value.integrity == null)] | length' package-lock.json
```

## Pitfalls

- Assuming integrity is enforced because the field exists, when the install path uses a legacy resolver.
- Corrupting a lockfile entry on a shared branch to test rejection.

## Done when

- Integrity coverage is recorded as a ratio.
- A corrupted entry is proven to be rejected in a sandbox.

## References

- [npm package-lock.json](https://docs.npmjs.com/cli/configuring-npm/package-lock-json)
