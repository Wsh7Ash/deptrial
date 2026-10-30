---
name: ci-secret-exposure
description: "Enumerate the environment a dependency install inherits, because an install hook that reads secrets does not need to find them in the repository. Use when install steps run in jobs that also deploy or publish"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [ci, secrets, environment]
phase: ci
---

# Check what an install step can read

> Enumerate the environment a dependency install inherits, because an install hook that reads secrets does not need to find them in the repository

**Use when:** install steps run in jobs that also deploy or publish

**Avoid when:** the install job holds no secrets and no cloud identity

## Procedure

1. List the secrets and environment variables available to the job that installs dependencies.
2. Record whether any step prints the environment, which turns a leak into a log artifact.
3. Move deployment credentials out of the install job.
4. Record the before and after environment for the install step.

## Signals

- secrets-listed
- print-steps-checked
- environment-split

## Patterns

**1. environment audit**

```
grep -rn -E 'secrets\.|env:|printenv|set -x' .github/workflows/ | head -40
```

## Pitfalls

- Auditing the workflow file and not the repository or organisation level secrets it inherits.
- Missing an OIDC identity that grants cloud access without any secret string.

## Done when

- The install job's environment is recorded.
- Deployment credentials are shown to be absent from it.

## References

- [GitHub secrets](https://docs.github.com/en/actions/concepts/security/secrets)
