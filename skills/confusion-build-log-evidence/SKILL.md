---
name: confusion-build-log-evidence
description: "Run the install in a sandbox with logging and keep the log, because a resolver trace from the project's own build is the evidence a maintainer cannot dismiss. Use when you need evidence rather than a configuration argument"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [confusion, evidence, logs]
phase: confusion
---

# Capture resolver evidence from a real build

> Run the install in a sandbox with logging and keep the log, because a resolver trace from the project's own build is the evidence a maintainer cannot dismiss

**Use when:** you need evidence rather than a configuration argument

**Avoid when:** running the install would execute untrusted scripts on a machine with credentials

## Procedure

1. Create a disposable environment with no credentials and no access to production networks.
2. Install with lifecycle scripts disabled and full logging to a file.
3. Extract the lines that show which URL served the package and which version was chosen.
4. Keep the log and the exact commands beside the finding.

## Signals

- sandbox-created
- log-captured
- urls-extracted

## Patterns

**1. sandboxed install**

```
npm ci --ignore-scripts --loglevel=silly > install.log 2>&1 || true
grep -E 'http fetch GET .* (internal-|@acme/)' install.log | head -20
```

## Pitfalls

- Running the install on a workstation that holds registry tokens, which turns evidence collection into an incident.
- Trimming the log until the URL that served the package is gone.

## Done when

- The log names the URL and version for the package in question.
- The sandbox had no credentials, and that is recorded.

## References

- [npm ci](https://docs.npmjs.com/cli/commands/npm-ci)
