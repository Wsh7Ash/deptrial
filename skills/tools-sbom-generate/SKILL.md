---
name: tools-sbom-generate
description: "Generate a component inventory from what is installed rather than declared, because an SBOM built from manifests describes intent and not the machine. Use when you need to answer which versions are deployed when an advisory lands"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [tools, sbom, inventory]
phase: tools
---

# Produce an SBOM from the resolved tree

> Generate a component inventory from what is installed rather than declared, because an SBOM built from manifests describes intent and not the machine

**Use when:** you need to answer which versions are deployed when an advisory lands

**Avoid when:** the runtime has no resolvable dependency tree to read

## Procedure

1. Generate the SBOM from the lockfile or the installed environment.
2. Record the generator and its version alongside the document.
3. Confirm the component count matches the resolved tree count.
4. Store the SBOM keyed by commit and build identifier.

## Signals

- sbom-generated
- generator-recorded
- count-matched

## Patterns

**1. npm SBOM**

```
npm sbom --sbom-format cyclonedx > sbom.cdx.json
jq '.components | length' sbom.cdx.json
```

## Pitfalls

- Generating from the manifest, which omits transitive components entirely.
- Storing one SBOM for many releases, so an advisory cannot be matched to a version.

## Done when

- The component count matches the resolved tree.
- The SBOM is stored per build with its generator recorded.

## References

- [CycloneDX](https://cyclonedx.org/specification/overview/)
