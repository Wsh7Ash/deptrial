# Security policy

## Scope

deptrial is a skill pack and a **static manifest scanner**. It has no registry client,
sends no network request, installs nothing, and never executes a dependency's lifecycle
hooks. `scan` reads files from disk and prints findings.

The realistic vulnerabilities here are in the tooling:

- a manifest that makes the scanner hang or exhaust memory (deeply nested JSON, a huge
  lockfile);
- a classifier bug that reports a pinned dependency as floating, or the reverse, which
  would make a gate either useless or unpassable;
- a rule that produces a finding whose evidence cannot be rechecked;
- a skill that instructs a reader to take a destructive or unauthorised action, such as
  publishing to a public registry or running an untrusted install on a machine holding
  credentials.

## Reporting

Open a private security advisory on this repository, or email the maintainer in
`pyproject.toml`. Include the file, a minimal input that reproduces the problem, and
what you expected.

Do not include live credentials, customer manifests or registry tokens in a report.

## Handling

- Acknowledgement within 7 days.
- A fix or a documented decision within 30 days, in a patch release.
- Credit in `CHANGELOG.md` unless you ask otherwise.

## Reviewing untrusted manifests

`scan` is meant to run against manifests you did not write. It reads them as text with
`errors="replace"`, parses JSON and TOML, and evaluates nothing. It does not run install
hooks, so pointing it at a hostile repository does not execute that repository's code.
