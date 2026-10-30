---
name: scripts-inventory-hooks
description: "List preinstall, install, postinstall and prepare hooks across the tree, because these run before anyone opens the code and are the usual execution point for a compromised package. Use when you are reviewing a package.json or an installed dependency tree"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [scripts, hooks, install]
phase: scripts
---

# Inventory every lifecycle hook that runs at install

> List preinstall, install, postinstall and prepare hooks across the tree, because these run before anyone opens the code and are the usual execution point for a compromised package

**Use when:** you are reviewing a package.json or an installed dependency tree

**Avoid when:** the installer runs with scripts disabled in every environment

## Procedure

1. Extract the scripts block from every package.json in the tree, including installed dependencies.
2. Separate hooks that run at install from those that run at test or build.
3. For each install hook, record the command and what it invokes.
4. Sort the list by whether the command reaches the network or a shell.

## Signals

- hooks-extracted
- commands-recorded
- sinks-classified

## Patterns

**1. hooks across the tree**

```
find . -name package.json -not -path '*/node_modules/*' -exec jq -r 'select(.scripts) | .name as $n | .scripts | to_entries[] | select(.key|test("preinstall|install|postinstall|prepare")) | "\($n) \(.key) \(.value)"' {} \;
```

## Pitfalls

- Reading only the top-level package.json and missing hooks in direct dependencies.
- Assuming a hook that runs `node build.js` is local, when build.js downloads a prebuilt binary.

## Done when

- Every install hook in the tree is listed with its command.
- Each command is classified as local, network or unknown.

## References

- [npm scripts](https://docs.npmjs.com/cli/using-npm/scripts)
