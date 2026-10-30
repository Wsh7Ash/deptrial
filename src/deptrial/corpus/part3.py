"""Part 3 of the deptrial corpus: provenance, ci, tools, review."""

from __future__ import annotations

from typing import Any

SKILLS: list[dict[str, Any]] = [
    {
        "slug": "provenance-attestation-check",
        "title": "Check whether a package publishes a build attestation",
        "summary": "Look for a signed provenance statement that ties the tarball to a source repository and commit, because an attestation is the only claim a registry makes about where the bytes came from",
        "use_when": "the dependency runs at install time or ships compiled code",
        "avoid_when": "the registry in use has no provenance support",
        "tags": ["provenance", "attestation", "registry"],
        "steps": [
            "Fetch the version document for the pinned version and record whether a provenance or attestation field exists.",
            "Record the source repository, commit and build workflow the attestation names.",
            "Compare that commit with the tag the version claims to be.",
            "Record a missing attestation as a fact, not as a finding on its own.",
        ],
        "signals": ["attestation-presence-recorded", "commit-captured", "tag-compared"],
        "patterns": [
            (
                "attestation lookup",
                "curl -sS https://registry.npmjs.org/PKG/1.2.3 | jq '{dist: .dist.attestations, repo: .repository}'",
            )
        ],
        "pitfalls": [
            "Treating the absence of an attestation as evidence of compromise, when most packages have none.",
            "Reading the attestation from the latest version instead of the pinned one.",
        ],
        "done_when": [
            "The pinned version's attestation status and named commit are recorded.",
            "Any mismatch between the named commit and the tag is raised.",
        ],
        "refs": ["[npm attestations](https://docs.npmjs.com/generating-provenance-statements)"],
        "meta": {"phase": "provenance"},
    },
    {
        "slug": "provenance-reproduce-build",
        "title": "Rebuild a package from source and compare",
        "summary": "Build the tagged source yourself and diff the result against the published tarball, because reproducibility turns an attestation from a claim into a check",
        "use_when": "the package is pure JavaScript or Python with a deterministic build",
        "avoid_when": "the build needs platform-specific toolchains you cannot reproduce",
        "tags": ["provenance", "reproducible", "build"],
        "steps": [
            "Clone at the exact commit the attestation or tag names.",
            "Install with the project's own lockfile and build with the documented command.",
            "Diff the build output against the extracted tarball, ignoring timestamps and source maps.",
            "Record the files that differ and any file present in only one side.",
        ],
        "signals": ["commit-cloned", "build-completed", "diff-recorded"],
        "patterns": [
            (
                "diff build against tarball",
                "git clone --depth 1 https://github.com/ORG/PKG /tmp/src && cd /tmp/src && git checkout <sha>\nnpm ci --ignore-scripts && npm run build\ndiff -r --exclude=node_modules /tmp/src/dist /tmp/scratch/package/dist | head -40",
            )
        ],
        "pitfalls": [
            "Diffing build directories that include source maps with embedded absolute paths, which always differ.",
            "Building at a branch tip rather than the tagged commit.",
        ],
        "done_when": [
            "The differing files are listed, or the build is proven byte-identical.",
            "The commit used for the rebuild is recorded.",
        ],
        "refs": ["[Reproducible builds](https://reproducible-builds.org/)"],
        "meta": {"phase": "provenance"},
    },
    {
        "slug": "provenance-verify-signature",
        "title": "Verify a signature instead of reading it",
        "summary": "Check the artifact signature against the publisher identity you expect, because a signature that verifies against the wrong identity proves only that someone signed it",
        "use_when": "the package ships a signature bundle or a registry attestation",
        "avoid_when": "no signature exists and none is claimed",
        "tags": ["provenance", "signature", "identity"],
        "steps": [
            "Record the identity the signature claims, including the issuer and the workflow ref.",
            "Verify with the tool the ecosystem documents, offline against the stored bundle.",
            "Compare the verified identity with the expected repository and workflow.",
            "Record the verification output verbatim, including the certificate subject.",
        ],
        "signals": ["identity-recorded", "verification-run", "subject-compared"],
        "patterns": [
            (
                "sigstore verify",
                "cosign verify-blob --bundle pkg.sigstore --certificate-identity-regexp 'https://github.com/ORG/.+' pkg.tgz",
            )
        ],
        "pitfalls": [
            "Accepting a valid signature without checking which identity it belongs to.",
            "Verifying online against a transparency log from a network you do not control, then trusting the response.",
        ],
        "done_when": [
            "The verified identity matches the expected publisher, or the mismatch is recorded.",
            "The verification command and output are stored with the finding.",
        ],
        "refs": ["[sigstore cosign](https://docs.sigstore.dev/cosign/overview/)"],
        "meta": {"phase": "provenance"},
    },
    {
        "slug": "provenance-missing-attestation-triage",
        "title": "Decide what to do about a missing attestation",
        "summary": "Turn an absent provenance statement into a proportionate decision instead of a blanket finding, because most of the ecosystem has none and a report that says so about every package is noise",
        "use_when": "a load-bearing dependency has no attestation",
        "avoid_when": "the dependency has an attestation that already verifies",
        "tags": ["provenance", "triage", "risk"],
        "steps": [
            "Record what the package can do: install hooks, network access at runtime, filesystem writes.",
            "Record compensating controls: lockfile integrity, script allowlist, sandboxed build.",
            "Decide by capability rather than by popularity: a package that runs code at install with no integrity pin is the priority.",
            "Write the decision with the two facts it is based on.",
        ],
        "signals": ["capabilities-recorded", "controls-recorded", "decision-written"],
        "patterns": [
            (
                "capability summary",
                "jq '{scripts: (.scripts // {}), deps: (.dependencies // {} | keys)}' /tmp/scratch/package/package.json",
            )
        ],
        "pitfalls": [
            "Ranking by download count instead of by what the package is allowed to do.",
            "Recording a missing attestation without naming the control that compensates for it.",
        ],
        "done_when": [
            "The decision names the capability and the compensating control.",
            "Prioritisation across packages is consistent with the same two facts.",
        ],
        "refs": ["[SLSA provenance](https://slsa.dev/provenance)"],
        "meta": {"phase": "provenance"},
    },
    {
        "slug": "provenance-source-tag-match",
        "title": "Confirm the published version matches a real tag",
        "summary": "Check that the version string corresponds to a commit in the repository it claims, because a version published from a working tree has no reviewable history behind it",
        "use_when": "the package names a repository and you need to tie the artifact to a reviewable commit",
        "avoid_when": "the package is registry-only with no repository field",
        "tags": ["provenance", "tags", "commit"],
        "steps": [
            "Read the repository field and the version from the tarball's manifest.",
            "Fetch the tags from that repository and record whether the version has one.",
            "Compare the tag's tree with the tarball's file list.",
            "Record a version with no tag as an unverifiable publication.",
        ],
        "signals": ["repository-read", "tag-existence-recorded", "tree-compared"],
        "patterns": [
            (
                "tag check",
                "git ls-remote --tags https://github.com/ORG/PKG | grep -E 'refs/tags/v?1\\.2\\.3$' || echo 'no matching tag'",
            )
        ],
        "pitfalls": [
            "Matching a tag by substring, so v1.2.30 satisfies a search for v1.2.3.",
            "Assuming a tag is immutable, when it can be moved or recreated.",
        ],
        "done_when": [
            "The tag for the pinned version is recorded as present or absent.",
            "A present tag is compared with the tarball contents, not just its name.",
        ],
        "refs": ["[git ls-remote](https://git-scm.com/docs/git-ls-remote)"],
        "meta": {"phase": "provenance"},
    },
    {
        "slug": "ci-token-least-privilege",
        "title": "Reduce the pipeline token to what the job needs",
        "summary": "Set the workflow token permission to read-only by default and grant write only where a step needs it, because a dependency that runs at install inherits whatever the job can do",
        "use_when": "the pipeline installs dependencies and the repository token has default write access",
        "avoid_when": "the pipeline already declares explicit per-job permissions",
        "tags": ["ci", "permissions", "token"],
        "steps": [
            "Record the repository's default workflow token permission setting.",
            "Add a top-level permissions block that grants read-only for contents.",
            "Grant write per job only where a publish or comment step requires it.",
            "Record the effective permissions from a run's log or API, not from the file alone.",
        ],
        "signals": ["default-recorded", "permissions-blocked", "effective-permissions-checked"],
        "patterns": [
            (
                "workflow permissions",
                "permissions:\n  contents: read\njobs:\n  release:\n    permissions:\n      contents: read\n      id-token: write",
            )
        ],
        "pitfalls": [
            "Leaving the default write token in place because the release job needs it, which also gives every install step write access.",
            "Granting id-token: write at workflow level, which every job then inherits.",
        ],
        "done_when": [
            "The top-level block grants read-only contents.",
            "Each write permission is attached to the one job that needs it.",
        ],
        "refs": ["[GitHub Actions permissions](https://docs.github.com/en/actions/reference/security/authentication-and-permissions)"],
        "meta": {"phase": "ci"},
    },
    {
        "slug": "ci-cache-key-trust",
        "title": "Make cache keys unforgeable",
        "summary": "Scope caches so a pull request cannot write content the default branch later restores, because a poisoned cache is code execution that never touches the repository",
        "use_when": "the pipeline caches dependencies, build output or toolchains",
        "avoid_when": "the pipeline has no cache step",
        "tags": ["ci", "cache", "poisoning"],
        "steps": [
            "List every cache key and the workflow events that can write to it.",
            "Confirm that caches written on a fork pull request cannot be restored by a default-branch job.",
            "Include the lockfile hash in the key so a restore cannot cross a dependency change.",
            "Record a test where a modified cache entry is not restored.",
        ],
        "signals": ["keys-listed", "write-events-recorded", "restore-tested"],
        "patterns": [
            (
                "hashed cache key",
                "- uses: actions/cache@v4\n  with:\n    path: ~/.npm\n    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}",
            )
        ],
        "pitfalls": [
            "Using a key without the lockfile hash, so a dependency change silently restores the old tree.",
            "Assuming fork pull requests cannot write caches in every CI system.",
        ],
        "done_when": [
            "Every cache key includes a content hash.",
            "A restore attempt with a modified entry is proven to miss.",
        ],
        "refs": ["[actions/cache](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)"],
        "meta": {"phase": "ci"},
    },
    {
        "slug": "ci-pull-request-target",
        "title": "Keep untrusted pull request code out of secret-bearing jobs",
        "summary": "Split workflows so fork code never runs in a job that holds secrets or a write token, because checkout plus install of an attacker's branch is code execution by design",
        "use_when": "a workflow in scope runs on pull_request_target or on a fork pull request",
        "avoid_when": "every workflow runs only on trusted branches",
        "tags": ["ci", "fork", "secrets"],
        "steps": [
            "Find workflows triggered by pull_request_target or by a fork's pull request.",
            "Record whether that job checks out the pull request head, installs dependencies, or runs project scripts.",
            "Move anything that executes contributor code into a workflow without secrets.",
            "Record the split with the workflow names and the permissions each retains.",
        ],
        "signals": ["triggers-recorded", "execution-recorded", "split-documented"],
        "patterns": [
            (
                "unsafe pattern",
                "on: pull_request_target\nsteps:\n  - uses: actions/checkout@v4\n    with: {ref: ${{ github.event.pull_request.head.sha }}}\n  - run: npm ci && npm test   # contributor code with a write token",
            )
        ],
        "pitfalls": [
            "Believing pull_request_target is safe because it does not pass secrets automatically.",
            "Splitting the workflow but leaving the write token on the job that checks out fork code.",
        ],
        "done_when": [
            "No job both executes contributor code and holds a secret or write token.",
            "The split workflow names are recorded.",
        ],
        "refs": ["[GitHub pull_request_target](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request_target)"],
        "meta": {"phase": "ci"},
    },
    {
        "slug": "ci-secret-exposure",
        "title": "Check what an install step can read",
        "summary": "Enumerate the environment a dependency install inherits, because an install hook that reads secrets does not need to find them in the repository",
        "use_when": "install steps run in jobs that also deploy or publish",
        "avoid_when": "the install job holds no secrets and no cloud identity",
        "tags": ["ci", "secrets", "environment"],
        "steps": [
            "List the secrets and environment variables available to the job that installs dependencies.",
            "Record whether any step prints the environment, which turns a leak into a log artifact.",
            "Move deployment credentials out of the install job.",
            "Record the before and after environment for the install step.",
        ],
        "signals": ["secrets-listed", "print-steps-checked", "environment-split"],
        "patterns": [
            (
                "environment audit",
                "grep -rn -E 'secrets\\.|env:|printenv|set -x' .github/workflows/ | head -40",
            )
        ],
        "pitfalls": [
            "Auditing the workflow file and not the repository or organisation level secrets it inherits.",
            "Missing an OIDC identity that grants cloud access without any secret string.",
        ],
        "done_when": [
            "The install job's environment is recorded.",
            "Deployment credentials are shown to be absent from it.",
        ],
        "refs": ["[GitHub secrets](https://docs.github.com/en/actions/concepts/security/secrets)"],
        "meta": {"phase": "ci"},
    },
    {
        "slug": "ci-dependency-review-gate",
        "title": "Fail the build on a new high-severity dependency finding",
        "summary": "Run the manifest scanner as a required check so a risky dependency cannot be merged without a decision, because review of a lockfile diff is where supply-chain risk is actually accepted",
        "use_when": "the repository accepts dependency changes through pull requests",
        "avoid_when": "dependencies are vendored and updated out of band",
        "tags": ["ci", "gate", "scan"],
        "steps": [
            "Add a job that runs the scanner with the project's allowlist and internal prefixes.",
            "Choose the fail-on severity deliberately and write the reason in the workflow comment.",
            "Make the job a required check on the default branch.",
            "Record a pull request that was blocked by it and how it was resolved.",
        ],
        "signals": ["job-added", "severity-chosen", "block-demonstrated"],
        "patterns": [
            (
                "gate step",
                "- name: dependency trust\n  run: deptrial scan . --allowlist react --allowlist lodash --internal-prefix 'internal-' --fail-on high",
            )
        ],
        "pitfalls": [
            "Failing on every finding, so the check is disabled within a week.",
            "Running the gate without the internal prefix list, which hides the confusion rules.",
        ],
        "done_when": [
            "The check is required and its severity threshold is justified in the file.",
            "A real pull request was blocked and resolved.",
        ],
        "refs": ["[Required status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)"],
        "meta": {"phase": "ci"},
    },
    {
        "slug": "tools-run-manifest-scan",
        "title": "Run the manifest scan and read the report",
        "summary": "Produce a per-rule report over a repository with the project's own allowlist, because a scan without an allowlist cannot tell a near miss from a legitimate name",
        "use_when": "you need a first pass over a repository's dependency trust",
        "avoid_when": "you are reviewing a single already-suspect package",
        "tags": ["tools", "scan", "report"],
        "steps": [
            "Run the scan with the internal prefixes and trusted names the organisation uses.",
            "Read the findings grouped by rule, not by file, so a systemic pattern is visible.",
            "Record the counts per severity before triaging anything.",
            "Store the JSON report with the commit hash it was produced from.",
        ],
        "signals": ["scan-run", "counts-recorded", "report-stored"],
        "patterns": [
            (
                "scan",
                "deptrial scan . --internal-prefix 'internal-' --internal-prefix '@acme/' \\\n  --allowlist react --allowlist lodash --fail-on high --json > deptrial.json",
            )
        ],
        "pitfalls": [
            "Running without --allowlist and then dismissing every near-miss finding as noise.",
            "Triaging findings one by one before recording the counts, so a rule that fired forty times looks like forty unrelated problems.",
        ],
        "done_when": [
            "The per-rule counts are recorded for the commit under review.",
            "The JSON report is stored with that commit hash.",
        ],
        "refs": ["[deptrial rules](https://github.com/Wsh7Ash/deptrial)"],
        "meta": {"phase": "tools"},
    },
    {
        "slug": "tools-suppression-with-reason",
        "title": "Suppress a finding with a reason, not a comment",
        "summary": "Record why a specific rule does not apply and what compensates for it, because a suppression without evidence becomes permanent the moment the reviewer leaves",
        "use_when": "a finding is a true positive that the project has decided to accept",
        "avoid_when": "the finding is actually a false positive, in which case the rule input is wrong and should be fixed",
        "tags": ["tools", "suppression", "risk"],
        "steps": [
            "Record the rule id, the subject and the manifest the finding came from.",
            "Record the compensating control and how it was verified.",
            "Record the date and the person who accepted the risk.",
            "Re-check the suppression when the package version changes.",
        ],
        "signals": ["finding-identified", "control-verified", "owner-recorded"],
        "patterns": [
            (
                "suppression record",
                "rule: DT001\nsubject: lodash@^4.17.21\ncontrol: package-lock.json committed with integrity, npm ci enforced in CI\nverified: 2026-10-30, clean install resolved 4.17.21\nowner: <name>",
            )
        ],
        "pitfalls": [
            "Suppressing by package name so the rule stops firing for every future version.",
            "Recording a control that was never tested, such as a lockfile that CI does not enforce.",
        ],
        "done_when": [
            "Each suppression names a verified control and an owner.",
            "Suppressions are revisited when the pinned version changes.",
        ],
        "refs": ["[Risk acceptance](https://csrc.nist.gov/pubs/sp/800/39/r1/final)"],
        "meta": {"phase": "tools"},
    },
    {
        "slug": "tools-sbom-generate",
        "title": "Produce an SBOM from the resolved tree",
        "summary": "Generate a component inventory from what is installed rather than declared, because an SBOM built from manifests describes intent and not the machine",
        "use_when": "you need to answer which versions are deployed when an advisory lands",
        "avoid_when": "the runtime has no resolvable dependency tree to read",
        "tags": ["tools", "sbom", "inventory"],
        "steps": [
            "Generate the SBOM from the lockfile or the installed environment.",
            "Record the generator and its version alongside the document.",
            "Confirm the component count matches the resolved tree count.",
            "Store the SBOM keyed by commit and build identifier.",
        ],
        "signals": ["sbom-generated", "generator-recorded", "count-matched"],
        "patterns": [
            (
                "npm SBOM",
                "npm sbom --sbom-format cyclonedx > sbom.cdx.json\njq '.components | length' sbom.cdx.json",
            )
        ],
        "pitfalls": [
            "Generating from the manifest, which omits transitive components entirely.",
            "Storing one SBOM for many releases, so an advisory cannot be matched to a version.",
        ],
        "done_when": [
            "The component count matches the resolved tree.",
            "The SBOM is stored per build with its generator recorded.",
        ],
        "refs": ["[CycloneDX](https://cyclonedx.org/specification/overview/)"],
        "meta": {"phase": "tools"},
    },
    {
        "slug": "tools-origin-and-licence-check",
        "title": "Check where each dependency actually comes from",
        "summary": "Record the origin and licence of every direct dependency, because a package that mirrors another's source can be swapped later and a licence change is often the first visible sign",
        "use_when": "you are assembling the trust record for a service",
        "avoid_when": "the dependency set is a handful of first-party workspaces",
        "tags": ["tools", "origin", "licence"],
        "steps": [
            "For each direct dependency, record the repository URL from the registry document and from the tarball manifest.",
            "Record a mismatch between the two, which is how a fork is detected.",
            "Record the licence string from the tarball and compare it with the repository.",
            "Flag packages whose repository is a fork or a mirror rather than the canonical source.",
        ],
        "signals": ["origins-recorded", "mismatches-listed", "licences-compared"],
        "patterns": [
            (
                "origin comparison",
                "jq -r '.repository.url' /tmp/scratch/package/package.json\ncurl -sS https://registry.npmjs.org/PKG | jq -r '.repository.url'",
            )
        ],
        "pitfalls": [
            "Trusting the registry's repository field, which the publisher controls.",
            "Treating a licence mismatch as a legal question and not recording it at all.",
        ],
        "done_when": [
            "Every direct dependency has both origin values recorded.",
            "Mismatches are listed with the file that shows them.",
        ],
        "refs": ["[SPDX licence list](https://spdx.org/licenses/)"],
        "meta": {"phase": "tools"},
    },
    {
        "slug": "review-finding-evidence",
        "title": "Write a supply-chain finding that can be rechecked",
        "summary": "Attach the exact artifact, hash and resolution trace to a finding, because a supply-chain claim without the bytes it refers to cannot be verified after the package changes",
        "use_when": "you are filing a dependency or pipeline finding",
        "avoid_when": "the observation is a hypothesis you have not yet confirmed",
        "tags": ["review", "evidence", "report"],
        "steps": [
            "State the package, version and tarball hash the finding refers to.",
            "Attach the resolution trace or workflow excerpt that demonstrates the behaviour.",
            "State the precondition the exploitation depends on, such as the ability to publish under a name.",
            "Store the artifact so the finding survives a registry change.",
        ],
        "signals": ["artifact-hashed", "trace-attached", "precondition-stated"],
        "patterns": [
            (
                "finding header",
                "Package: internal-billing-client\nVersion: 1.2.0 (tarball sha256 ...)\nPrecondition: ability to publish under a name the private registry does not own\nEvidence: install.log lines 41-58",
            )
        ],
        "pitfalls": [
            "Quoting a version without the hash, when a republish makes the version ambiguous.",
            "Describing a hypothetical instead of the observed resolution.",
        ],
        "done_when": [
            "The finding names an artifact by hash.",
            "The precondition is stated separately from the observation.",
        ],
        "refs": ["[CWE-1104 use of unmaintained third-party components](https://cwe.mitre.org/data/definitions/1104.html)"],
        "meta": {"phase": "review"},
    },
    {
        "slug": "review-severity-basis",
        "title": "Justify severity from capability, not from rule name",
        "summary": "Rate a finding by what the compromised package or job could do in this specific pipeline, because the same missing pin is a critical finding in a release job and a note in a test job",
        "use_when": "you are assigning severity to a supply-chain finding",
        "avoid_when": "the finding has no execution path in the affected environment",
        "tags": ["review", "severity", "impact"],
        "steps": [
            "Record what the affected job or runtime can reach: secrets, registry tokens, production network, signing keys.",
            "Record whether the dependency executes code at install or only at runtime.",
            "State the impact in one sentence with the reachable asset named.",
            "Show the same rule in a lower-privilege job to demonstrate the difference.",
        ],
        "signals": ["capability-recorded", "execution-point-recorded", "asset-named"],
        "patterns": [
            (
                "severity note",
                "Rule: DT003 (install hook)\nJob: release (contents: write, NPM_TOKEN)\nImpact: install-time code can publish to the registry under the org scope",
            )
        ],
        "pitfalls": [
            "Copying severity from a scanner's default rating, which knows nothing about the job.",
            "Rating by the number of downloads rather than the reachable asset.",
        ],
        "done_when": [
            "The severity cites a reachable asset and an execution point.",
            "A contrasting lower-privilege case is recorded.",
        ],
        "refs": ["[CVSS v4](https://www.first.org/cvss/v4-0/specification-document)"],
        "meta": {"phase": "review"},
    },
    {
        "slug": "review-fix-verification",
        "title": "Verify the dependency fix with the same evidence",
        "summary": "Re-run the scan and the resolution trace after the fix and compare with the pre-fix record, because a pin that was added in one manifest and forgotten in another closes nothing",
        "use_when": "remediation has been merged",
        "avoid_when": "the fix has not reached an environment you can test",
        "tags": ["review", "verification", "fix"],
        "steps": [
            "Re-run the same scan command with the same options against the fixed commit.",
            "Compare the finding counts per rule with the pre-fix record.",
            "Re-run the resolution trace for the specific package and confirm the new source.",
            "Record any finding that remains, with the reason it was not fixed.",
        ],
        "signals": ["scan-rerun", "counts-compared", "trace-confirmed"],
        "patterns": [
            (
                "before and after",
                "deptrial scan . --fail-on high --json > after.json\njq -S '.by_rule' before.json after.json",
            )
        ],
        "pitfalls": [
            "Re-running with a different allowlist, which changes the findings for reasons unrelated to the fix.",
            "Accepting a reduced count as proof when the specific package still resolves publicly.",
        ],
        "done_when": [
            "The per-rule counts before and after are both recorded.",
            "The specific package's resolution is shown to have changed.",
        ],
        "refs": ["[NIST SP 800-40 patch management](https://csrc.nist.gov/pubs/sp/800/40/r4/final)"],
        "meta": {"phase": "review"},
    },
    {
        "slug": "review-disclosure-timeline",
        "title": "Agree the disclosure timeline before you report",
        "summary": "Set expectations for a supply-chain issue that spans a registry, a vendor and your own build, because an unmaintained package may never patch and the report has to say what happens then",
        "use_when": "the finding needs a third party, such as a package maintainer or registry, to act",
        "avoid_when": "the fix is entirely inside your own repository",
        "tags": ["review", "disclosure", "timeline"],
        "steps": [
            "Identify every party who must act: maintainer, registry, your own team.",
            "Record the dates: report, acknowledgement, fix target, public disclosure.",
            "State the compensating control that applies in the meantime, such as a pin or a script allowlist.",
            "Record what changes if the maintainer never responds.",
        ],
        "signals": ["parties-listed", "dates-recorded", "interim-control-named"],
        "patterns": [
            (
                "timeline",
                "reported: 2026-10-30\nack: 2026-11-06 target\nfix target: 2026-11-29\ninterim: exact pin + lockfile integrity + install scripts disabled",
            )
        ],
        "pitfalls": [
            "Publishing details before the maintainer has had a chance to publish a fixed version.",
            "Leaving the interim control out, so users have no action to take while they wait.",
        ],
        "done_when": [
            "Every party and date is recorded.",
            "An interim control is stated and verified to be in place.",
        ],
        "refs": ["[CERT/CC vulnerability disclosure](https://www.kb.cert.org/vuls/)", "[ISO/IEC 29147](https://www.iso.org/standard/72311.html)"],
        "meta": {"phase": "review"},
    },
]
