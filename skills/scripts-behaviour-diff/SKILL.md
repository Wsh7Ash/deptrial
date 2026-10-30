---
name: scripts-behaviour-diff
description: "Compare the commands and the files a lifecycle hook touches across versions, because a hook that was benign in one release can become a downloader in the next with no change to its name. Use when a dependency version moved and the package has install hooks"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [scripts, diff, behaviour]
phase: scripts
---

# Diff what a hook does between two versions

> Compare the commands and the files a lifecycle hook touches across versions, because a hook that was benign in one release can become a downloader in the next with no change to its name

**Use when:** a dependency version moved and the package has install hooks

**Avoid when:** the package has no lifecycle hooks in either version

## Procedure

1. Record the hook command strings for both versions from their tarballs.
2. Record the files each hook reads and writes, from a container run of each version.
3. Diff both the commands and the touched-file sets.
4. Report any new network destination or new write outside the package directory.

## Signals

- commands-diffed
- file-sets-diffed
- destinations-listed

## Patterns

**1. compare hook commands**

```
jq -r '.scripts' /tmp/old/package/package.json > old-scripts.json
jq -r '.scripts' /tmp/new/package/package.json > new-scripts.json
diff -u old-scripts.json new-scripts.json || true
```

## Pitfalls

- Comparing only the command text when the invoked script file changed instead.
- Running both versions in the same container, so the second inherits the first's writes.

## Done when

- Both the command diff and the touched-file diff are recorded.
- Every new destination is either explained or raised.

## References

- [npm scripts](https://docs.npmjs.com/cli/using-npm/scripts)
