---
name: recon-ci-install-path
description: "Find the exact command a pipeline runs to install dependencies, because a flag in that command overrides everything the manifest declares. Use when the repository builds in CI and the build has access to secrets or a publish token"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [recon, ci, install]
phase: recon
---

# Read the CI install path before blaming the manifest

> Find the exact command a pipeline runs to install dependencies, because a flag in that command overrides everything the manifest declares

**Use when:** the repository builds in CI and the build has access to secrets or a publish token

**Avoid when:** there is no CI configuration in scope

## Procedure

1. Open every workflow and pipeline definition and locate the install step.
2. Record the flags: --ignore-scripts, --frozen-lockfile, --no-deps, --only=prod and any registry override.
3. Record which secrets the job can read, including the default token.
4. Note whether the job runs on pull requests from forks, which decides who can influence the install.

## Signals

- install-command-recorded
- flags-listed
- secret-scope-recorded

## Patterns

**1. install step**

```
grep -rn -E 'npm (ci|install)|yarn (install|add)|pip install|poetry install' .github/workflows/ || true
```

## Pitfalls

- Assuming --ignore-scripts is set because the README says so, when the workflow omits it.
- Missing a second workflow that installs with different flags for a different job.

## Done when

- The install command and its flags are quoted verbatim in the notes.
- The secret scope of that job is recorded.

## References

- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
