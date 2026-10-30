# Project spec

```text
Name             deptrial
Category         supply-chain security
Target user      appsec engineers, release engineers and bug-bounty hunters who
                 must decide whether a dependency tree can be trusted
Problem          Dependency risk is decided by small facts that reviewers get
                 wrong: a floating range, a name one edit from a trusted one, a
                 git ref that moves, an install hook in a privileged job. Those
                 facts are spread across manifests, lockfiles and workflows, and
                 the tools that exist report vulnerabilities rather than trust.
Solution         A 50-skill pack covering the whole supply-chain engagement, plus
                 a scanner that parses npm, pip and PEP 621 manifests and reports
                 ten rule ids with severities, so a pipeline can gate on a
                 decision instead of a vibe.
Core workflow    recon -> registry -> confusion -> typosquat -> pinning ->
                 scripts -> provenance -> ci -> tools -> review
Must-have        50 unique validated skills; 10 phases; nine per-skill rules and
                 five package-level rules; deterministic rendering; committed
                 skills/, pack.json and catalog with drift tests; ten rules with
                 stable ids; threshold-based exit codes.
Nice-to-have     transitive dependency scanning; a live registry check for name
                 registration; SARIF output for code scanning.
Stack            Python 3.10+ standard library only (tomllib on 3.11+); pytest.
Test strategy    91 tests in two files. test_corpus.py: shape, uniqueness, floors,
                 phases, artifact drift byte for byte, manifest digests, build
                 determinism, absence of publish instructions, CLI exit codes.
                 test_rules.py: every classifier case, every parser, discovery
                 behaviour, each of the ten rules including the opt-in ones, the
                 negative cases (exact pins produce no finding, exact allowlist
                 match produces no near miss, the hardened example is clean), and
                 the scan CLI including all three exit codes.
Demo/result      examples/vulnerable -> 14 dependencies, 15 findings, exit 1 with
                 --fail-on high; examples/hardened -> 0 findings, exit 0. Verbatim
                 output in results/demo_transcript.txt.
Safety           Read-only over local files. No registry client, no publish, no
                 install. The one test that forbids "npm publish" in a skill is
                 deliberate: the pack must never instruct a reader to claim a
                 public name as proof.
Definition of    validate 50/50; build reproduces committed artifacts with no diff;
done             pytest green; both examples produce their documented counts and
                 exit codes; README and RESULTS cite measured output only.
```
