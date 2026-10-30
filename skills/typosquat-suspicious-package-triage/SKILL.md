---
name: typosquat-suspicious-package-triage
description: "Read a candidate package from its tarball in a scratch directory, because installing it to see what it does is how the investigation becomes the incident. Use when a near-miss or a new dependency needs a verdict"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [typosquat, triage, static]
phase: typosquat
---

# Triage a suspicious package without installing it

> Read a candidate package from its tarball in a scratch directory, because installing it to see what it does is how the investigation becomes the incident

**Use when:** a near-miss or a new dependency needs a verdict

**Avoid when:** the package is already installed in the environment under review

## Procedure

1. Download the tarball only, and record its hash.
2. List its files and read the entry point, install scripts and any file that opens a socket or a child process.
3. Record the network destinations and environment variables it reads.
4. Write the verdict with the file and line for each claim.

## Signals

- tarball-hashed
- files-listed
- sinks-recorded

## Patterns

**1. static look**

```
tar xzf pkg.tgz -C /tmp/scratch
rg -n "child_process|exec\(|https?://|process\.env" /tmp/scratch/package | head -30
```

## Pitfalls

- Running npm install to inspect the package, which executes its install hooks.
- Reading only index.js and missing a file referenced from its scripts block.

## Done when

- Every claim in the verdict cites a file and line in the extracted tarball.
- The tarball hash is retained with the verdict.

## References

- [npm pack](https://docs.npmjs.com/cli/commands/npm-pack)
