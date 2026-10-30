---
name: review-disclosure-timeline
description: "Set expectations for a supply-chain issue that spans a registry, a vendor and your own build, because an unmaintained package may never patch and the report has to say what happens then. Use when the finding needs a third party, such as a package maintainer or registry, to act"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [review, disclosure, timeline]
phase: review
---

# Agree the disclosure timeline before you report

> Set expectations for a supply-chain issue that spans a registry, a vendor and your own build, because an unmaintained package may never patch and the report has to say what happens then

**Use when:** the finding needs a third party, such as a package maintainer or registry, to act

**Avoid when:** the fix is entirely inside your own repository

## Procedure

1. Identify every party who must act: maintainer, registry, your own team.
2. Record the dates: report, acknowledgement, fix target, public disclosure.
3. State the compensating control that applies in the meantime, such as a pin or a script allowlist.
4. Record what changes if the maintainer never responds.

## Signals

- parties-listed
- dates-recorded
- interim-control-named

## Patterns

**1. timeline**

```
reported: 2026-10-30
ack: 2026-11-06 target
fix target: 2026-11-29
interim: exact pin + lockfile integrity + install scripts disabled
```

## Pitfalls

- Publishing details before the maintainer has had a chance to publish a fixed version.
- Leaving the interim control out, so users have no action to take while they wait.

## Done when

- Every party and date is recorded.
- An interim control is stated and verified to be in place.

## References

- [CERT/CC vulnerability disclosure](https://www.kb.cert.org/vuls/)
- [ISO/IEC 29147](https://www.iso.org/standard/72311.html)
