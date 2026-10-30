---
name: pinning-replace-url-dependency
description: "Move a dependency off a mutable branch or tarball URL onto content identified by a hash, because a git branch and an HTTP URL both point at bytes that can change without any version changing. Use when a manifest declares a git ref, a branch or an http tarball"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [pinning, vcs, url]
phase: pinning
---

# Replace a URL or git dependency with a registry pin

> Move a dependency off a mutable branch or tarball URL onto content identified by a hash, because a git branch and an HTTP URL both point at bytes that can change without any version changing

**Use when:** a manifest declares a git ref, a branch or an http tarball

**Avoid when:** the dependency is genuinely private and its registry publishes signed artifacts

## Procedure

1. Identify the commit or tarball actually in use and record its hash.
2. Locate or publish a registry version containing exactly that content.
3. Switch the manifest to the registry version with an integrity hash.
4. Re-install and diff the resolved tree against the previous one.

## Signals

- commit-hash-recorded
- registry-version-found
- tree-compared

## Patterns

**1. pin a git ref to a commit**

```
# before
express: github:expressjs/express#main
# after, when no registry version matches
express: github:expressjs/express#<40-char-sha>
```

## Pitfalls

- Pinning to a branch that gets rebased, which changes the commit under a stable name.
- Losing the diff review because the resolved tree changed while the constraint looked equivalent.

## Done when

- No dependency points at a moving ref.
- The resolved content is identical before and after, and that is recorded.

## References

- [npm git dependencies](https://docs.npmjs.com/cli/configuring-npm/package-json#git-urls-as-dependencies)
