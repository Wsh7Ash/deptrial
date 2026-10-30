---
name: tools-run-manifest-scan
description: "Produce a per-rule report over a repository with the project's own allowlist, because a scan without an allowlist cannot tell a near miss from a legitimate name. Use when you need a first pass over a repository's dependency trust"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [tools, scan, report]
phase: tools
---

# Run the manifest scan and read the report

> Produce a per-rule report over a repository with the project's own allowlist, because a scan without an allowlist cannot tell a near miss from a legitimate name

**Use when:** you need a first pass over a repository's dependency trust

**Avoid when:** you are reviewing a single already-suspect package

## Procedure

1. Run the scan with the internal prefixes and trusted names the organisation uses.
2. Read the findings grouped by rule, not by file, so a systemic pattern is visible.
3. Record the counts per severity before triaging anything.
4. Store the JSON report with the commit hash it was produced from.

## Signals

- scan-run
- counts-recorded
- report-stored

## Patterns

**1. scan**

```
deptrial scan . --internal-prefix 'internal-' --internal-prefix '@acme/' \
  --allowlist react --allowlist lodash --fail-on high --json > deptrial.json
```

## Pitfalls

- Running without --allowlist and then dismissing every near-miss finding as noise.
- Triaging findings one by one before recording the counts, so a rule that fired forty times looks like forty unrelated problems.

## Done when

- The per-rule counts are recorded for the commit under review.
- The JSON report is stored with that commit hash.

## References

- [deptrial rules](https://github.com/Wsh7Ash/deptrial)
