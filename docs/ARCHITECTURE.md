# Architecture

deptrial has two halves that never mix: a skill corpus with its renderer and validator, and a scanner with its parsers and rules. They share a CLI and nothing else.

```
corpus/part1..part3.py   authored dicts
        |  skill_from_dict (model.py)
      Skill objects  -----> validate.py -----> issues
        |  render_skill (render.py)
   skills/<slug>/SKILL.md, pack.json, results/catalog.md

  project tree  -----> manifests.discover -----> Inventory
                                                    |  rules.scan
                                                 Report (Finding list)
```

## The corpus half

Skills are authored as plain dicts with a fixed key set. `skill_from_dict` is the only place that cares about shape and it fails loudly on a missing key, an empty list entry, or a pattern that is not a `(label, code)` pair. `Skill` is frozen, so the renderer is a pure function and `build_pack` is deterministic.

`validate.py` applies nine per-skill rules and five package rules. The floors are constants, not configuration: a pack whose floors can be lowered per run has no floors. Phase is a closed set of ten, so a skill that fits none of them forces a deliberate change to the list rather than an arbitrary string.

Uniqueness is enforced on slug, case-insensitive title and summary. A copied skill renamed at the slug alone is exactly the failure a "50 unique skills" claim has to survive, and `validate_pack` rejects it.

## The scanner half

`manifests.py` turns a directory into one `Inventory`: dependencies, lifecycle scripts, manifest paths, lockfile paths, and two counts of lockfile entries (total, and with integrity).

Every dependency carries two classifications made at parse time:

- **source** — `registry`, `vcs`, `url` or `local`, decided by the spec prefix. `git+`, `git://`, `github:`, `ssh://` are vcs; `http://`, `https://`, `file:`, `link:` are url; `workspace:` and relative paths are local.
- **binding** — `exact`, `bounded`, `floating` or `wildcard`, decided by the ecosystem's own rules. `1.2.3` and `=1.2.3` are exact; `^`, `~`, `||` and a bare `>=` are floating; `>=1,<2` and `>=1.0.0 <2.0.0` are bounded; empty, `*`, `latest` and `1.x` are wildcards. pip gets its own branch because `==` and PEP 440 bounds do not mean what npm's do.

Because classification happens once, a rule never inspects a raw string, and a new rule cannot disagree with an existing one about what `^1.2.3` is.

`rules.py` holds ten functions with stable ids. Each takes the inventory and the options and returns findings; none raises, because a manifest in the wild is often partly malformed and a scanner that dies on one bad file reports nothing about the rest.

Two rules are opt-in: `DT004` needs `--internal-prefix` and `DT005` needs `--allowlist`. Both depend on organisational facts the tool cannot guess, so omitting them disables the rule instead of guessing. That is also why the negative tests matter: `DT004` must not fire for an exactly pinned name, and `DT005` must not fire for an exact allowlist match.

Ordering is deterministic: findings sort by severity descending, then rule id, then subject, then manifest. Two scans of the same tree produce byte-identical text, which is what makes a before/after comparison meaningful.

## Exit codes

`0` success or below threshold, `1` findings at or above `--fail-on`, `2` usage error. The same convention as the corpus validator, so a pipeline can gate on either half.

## Non-goals

- No registry client: the scanner cannot tell you whether a name is registered publicly.
- No install: nothing here runs `npm install`, so no lifecycle hook is executed by this repository.
- No transitive resolution: only manifests are parsed.
- No vulnerability matching: this is a trust review, not a CVE feed.
