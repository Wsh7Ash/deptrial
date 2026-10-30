---
name: typosquat-homoglyph-check
description: "Compare declared names byte by byte against trusted ones, because a Cyrillic character or a zero-width joiner renders identically in a review and resolves to a different package. Use when a name renders identically to a trusted one but the install resolves elsewhere"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [typosquat, unicode, homoglyph]
phase: typosquat
---

# Check for homoglyph and unicode lookalikes

> Compare declared names byte by byte against trusted ones, because a Cyrillic character or a zero-width joiner renders identically in a review and resolves to a different package

**Use when:** a name renders identically to a trusted one but the install resolves elsewhere

**Avoid when:** the name is plain ASCII and matches the trusted name exactly

## Procedure

1. Dump each declared name as code points, not as rendered text.
2. Flag names containing characters outside the ASCII range, and names containing zero-width or bidirectional control characters.
3. Compare the code-point sequence with the trusted name it resembles.
4. Record the code points in the finding, since the rendered name is the misleading part.

## Signals

- code-points-dumped
- non-ascii-flagged
- comparison-recorded

## Patterns

**1. code points**

```
python -c "import sys;print([hex(ord(c)) for c in sys.argv[1]])" 'lοdash'  # Greek omicron
```

## Pitfalls

- Copying the name from a rendered page into a terminal, which normalises it and hides the difference.
- Reporting a non-ASCII name as malicious when the registry allows it legitimately.

## Done when

- The code points of both names are in the finding.
- Registry resolution for the lookalike is recorded.

## References

- [Unicode confusables](https://www.unicode.org/reports/tr39/)
