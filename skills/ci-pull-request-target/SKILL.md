---
name: ci-pull-request-target
description: "Split workflows so fork code never runs in a job that holds secrets or a write token, because checkout plus install of an attacker's branch is code execution by design. Use when a workflow in scope runs on pull_request_target or on a fork pull request"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [ci, fork, secrets]
phase: ci
---

# Keep untrusted pull request code out of secret-bearing jobs

> Split workflows so fork code never runs in a job that holds secrets or a write token, because checkout plus install of an attacker's branch is code execution by design

**Use when:** a workflow in scope runs on pull_request_target or on a fork pull request

**Avoid when:** every workflow runs only on trusted branches

## Procedure

1. Find workflows triggered by pull_request_target or by a fork's pull request.
2. Record whether that job checks out the pull request head, installs dependencies, or runs project scripts.
3. Move anything that executes contributor code into a workflow without secrets.
4. Record the split with the workflow names and the permissions each retains.

## Signals

- triggers-recorded
- execution-recorded
- split-documented

## Patterns

**1. unsafe pattern**

```
on: pull_request_target
steps:
  - uses: actions/checkout@v4
    with: {ref: ${{ github.event.pull_request.head.sha }}}
  - run: npm ci && npm test   # contributor code with a write token
```

## Pitfalls

- Believing pull_request_target is safe because it does not pass secrets automatically.
- Splitting the workflow but leaving the write token on the job that checks out fork code.

## Done when

- No job both executes contributor code and holds a secret or write token.
- The split workflow names are recorded.

## References

- [GitHub pull_request_target](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request_target)
