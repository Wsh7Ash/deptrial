---
name: scripts-ci-enforcement
description: "Install with hooks restricted and fail the build on lockfile or allowlist drift, because a policy that lives only in a document is not a control. Use when the policy exists and you want it to hold for every build"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [scripts, ci, enforcement]
phase: scripts
---

# Enforce the script policy in CI

> Install with hooks restricted and fail the build on lockfile or allowlist drift, because a policy that lives only in a document is not a control

**Use when:** the policy exists and you want it to hold for every build

**Avoid when:** CI cannot install dependencies at all

## Procedure

1. Set the install step to the restricted form and commit the allowlist.
2. Add a step that fails when the lockfile changes during install.
3. Add a step that reports which hooks were skipped, so a new hook is visible in the log.
4. Record a run where an added hook produced a red build.

## Signals

- restricted-install
- drift-step-added
- skip-report-present

## Patterns

**1. workflow steps**

```
- name: install
  run: npm ci --ignore-scripts
- name: lockfile drift
  run: git diff --exit-code -- package-lock.json
```

## Pitfalls

- Placing the drift check before the install, when nothing has changed yet.
- Making the skip report an annotation nobody reads instead of a step that fails on an unknown hook.

## Done when

- A build with an unlisted hook is proven to fail.
- The skip report appears in the job log on every run.

## References

- [npm ci](https://docs.npmjs.com/cli/commands/npm-ci)
