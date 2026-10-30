---
name: tools-suppression-with-reason
description: "Record why a specific rule does not apply and what compensates for it, because a suppression without evidence becomes permanent the moment the reviewer leaves. Use when a finding is a true positive that the project has decided to accept"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [tools, suppression, risk]
phase: tools
---

# Suppress a finding with a reason, not a comment

> Record why a specific rule does not apply and what compensates for it, because a suppression without evidence becomes permanent the moment the reviewer leaves

**Use when:** a finding is a true positive that the project has decided to accept

**Avoid when:** the finding is actually a false positive, in which case the rule input is wrong and should be fixed

## Procedure

1. Record the rule id, the subject and the manifest the finding came from.
2. Record the compensating control and how it was verified.
3. Record the date and the person who accepted the risk.
4. Re-check the suppression when the package version changes.

## Signals

- finding-identified
- control-verified
- owner-recorded

## Patterns

**1. suppression record**

```
rule: DT001
subject: lodash@^4.17.21
control: package-lock.json committed with integrity, npm ci enforced in CI
verified: 2026-10-30, clean install resolved 4.17.21
owner: <name>
```

## Pitfalls

- Suppressing by package name so the rule stops firing for every future version.
- Recording a control that was never tested, such as a lockfile that CI does not enforce.

## Done when

- Each suppression names a verified control and an owner.
- Suppressions are revisited when the pinned version changes.

## References

- [Risk acceptance](https://csrc.nist.gov/pubs/sp/800/39/r1/final)
