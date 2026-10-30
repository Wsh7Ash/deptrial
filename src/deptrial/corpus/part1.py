"""Part 1 of the deptrial corpus: recon, registry, confusion."""

from __future__ import annotations

from typing import Any

SKILLS: list[dict[str, Any]] = [
    {
        "slug": "recon-manifest-inventory",
        "title": "Inventory every manifest and lockfile in the tree",
        "summary": "List the files that decide what gets installed before you reason about any single dependency, because the manifest you read first is rarely the one that wins",
        "use_when": "you are starting a review of a repository you did not write",
        "avoid_when": "the review is scoped to one already-identified package",
        "tags": ["recon", "manifests", "inventory"],
        "steps": [
            "Find every package.json, requirements*.txt, pyproject.toml and lockfile, excluding node_modules and virtualenvs.",
            "Record the directory of each one, because nested manifests are separate install roots with their own resolution.",
            "Match each manifest to its lockfile, and note manifests with none.",
            "Write the inventory to a file and hash it, so the review is tied to one commit.",
        ],
        "signals": ["manifests-listed", "lockfile-mapping-recorded", "inventory-hashed"],
        "patterns": [
            (
                "inventory",
                "find . -type f \\( -name package.json -o -name 'requirements*.txt' \\\n  -o -name pyproject.toml -o -name 'package-lock.json' -o -name 'yarn.lock' \\\n  -o -name 'poetry.lock' -o -name 'uv.lock' \\) \\\n  -not -path '*/node_modules/*' -not -path '*/.venv/*' | sort | tee manifests.txt",
            )
        ],
        "pitfalls": [
            "Reading only the root manifest, while a service directory installs its own dependencies with different pins.",
            "Counting a lockfile that belongs to a different manifest in a sibling directory.",
        ],
        "done_when": [
            "Every manifest has a recorded path and a lockfile association or an explicit none.",
            "The inventory is committed to the engagement notes.",
        ],
        "refs": ["[npm package.json](https://docs.npmjs.com/cli/configuring-npm/package-json)"],
        "meta": {"phase": "recon"},
    },
    {
        "slug": "recon-registry-metadata",
        "title": "Read registry metadata for the packages that matter",
        "summary": "Pull the registry document for each dependency and read maintainers, publish times and dist integrity, because the version string tells you nothing about who published it",
        "use_when": "a dependency is load-bearing enough that its compromise would matter",
        "avoid_when": "the package is a local workspace entry with no registry presence",
        "tags": ["recon", "registry", "metadata"],
        "steps": [
            "Fetch the registry document for the package and store it unmodified.",
            "Record the maintainers, the latest publish time and the number of published versions.",
            "Compare the maintainer list with what the repository or documentation claims.",
            "Record the dist integrity value so a later tarball can be compared with it.",
        ],
        "signals": ["registry-document-stored", "maintainers-recorded", "integrity-recorded"],
        "patterns": [
            (
                "npm registry document",
                "curl -sS https://registry.npmjs.org/lodash | jq '{maintainers, time: .time.modified, versions: (.versions|length)}'",
            )
        ],
        "pitfalls": [
            "Trusting the version number, when a maintainer account change is the signal that matters.",
            "Fetching through a proxy that rewrites the document and then treating the result as authoritative.",
        ],
        "done_when": [
            "The registry document is stored for every load-bearing dependency.",
            "Maintainer and publish-time values are in the notes, not in memory.",
        ],
        "refs": ["[npm registry API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)"],
        "meta": {"phase": "recon"},
    },
    {
        "slug": "recon-dependency-graph",
        "title": "Split direct dependencies from the resolved tree",
        "summary": "Distinguish what the manifest declares from what the lockfile actually installs, since the transitive set is where most compromise lands and it is invisible in the manifest",
        "use_when": "you need to know whether a risky package is actually installed or merely declared",
        "avoid_when": "the project vendors no lockfile and has no installed tree to read",
        "tags": ["recon", "transitive", "graph"],
        "steps": [
            "Produce the resolved tree from the lockfile rather than from the manifest.",
            "Mark each entry direct or transitive, and record which direct dependency pulled it in.",
            "Count transitive entries that come from a vcs or url source, since those bypass registry integrity.",
            "Record the deepest chain length, which bounds how far a single compromised package can reach.",
        ],
        "signals": ["tree-produced", "direct-marked", "transitive-counted"],
        "patterns": [
            (
                "resolved tree",
                "npm ls --all --json > tree.json 2>/dev/null; jq '[.. | objects | select(.version?) | .version] | length' tree.json",
            )
        ],
        "pitfalls": [
            "Treating a declared dependency as installed when the lockfile excludes it.",
            "Reporting a transitive package as reachable without naming the direct dependency that pulls it in.",
        ],
        "done_when": [
            "Every risky package is labelled direct or transitive with its parent named.",
            "The transitive count is recorded as a number, not an impression.",
        ],
        "refs": ["[npm ls](https://docs.npmjs.com/cli/commands/npm-ls)"],
        "meta": {"phase": "recon"},
    },
    {
        "slug": "recon-ci-install-path",
        "title": "Read the CI install path before blaming the manifest",
        "summary": "Find the exact command a pipeline runs to install dependencies, because a flag in that command overrides everything the manifest declares",
        "use_when": "the repository builds in CI and the build has access to secrets or a publish token",
        "avoid_when": "there is no CI configuration in scope",
        "tags": ["recon", "ci", "install"],
        "steps": [
            "Open every workflow and pipeline definition and locate the install step.",
            "Record the flags: --ignore-scripts, --frozen-lockfile, --no-deps, --only=prod and any registry override.",
            "Record which secrets the job can read, including the default token.",
            "Note whether the job runs on pull requests from forks, which decides who can influence the install.",
        ],
        "signals": ["install-command-recorded", "flags-listed", "secret-scope-recorded"],
        "patterns": [
            (
                "install step",
                "grep -rn -E 'npm (ci|install)|yarn (install|add)|pip install|poetry install' .github/workflows/ || true",
            )
        ],
        "pitfalls": [
            "Assuming --ignore-scripts is set because the README says so, when the workflow omits it.",
            "Missing a second workflow that installs with different flags for a different job.",
        ],
        "done_when": [
            "The install command and its flags are quoted verbatim in the notes.",
            "The secret scope of that job is recorded.",
        ],
        "refs": ["[GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)"],
        "meta": {"phase": "recon"},
    },
    {
        "slug": "recon-private-scope-map",
        "title": "Map which names are supposed to be private",
        "summary": "Build the list of package names your organisation treats as internal, because every name on that list is a dependency-confusion candidate the moment it is unbounded",
        "use_when": "the organisation publishes private packages alongside public ones",
        "avoid_when": "every dependency is verified public and none is internal",
        "tags": ["recon", "scope", "internal"],
        "steps": [
            "Collect internal names from manifests, import statements and the private registry's own index.",
            "Record the intended registry for each name, whether a scope or a prefix.",
            "Mark names that carry no scope and no registry pin, which are the ambiguous ones.",
            "Store the list as the input to the scanner's internal-prefix option rather than retyping it later.",
        ],
        "signals": ["internal-names-listed", "intended-registry-recorded", "unscoped-names-marked"],
        "patterns": [
            (
                "unscoped internal names",
                "grep -rhoE '\"(internal-[a-z0-9-]+|@acme/[a-z0-9-]+)\"' --include=package.json . | sort -u",
            )
        ],
        "pitfalls": [
            "Treating a scoped name as safe without checking that the scope is actually claimed on the public registry.",
            "Missing internal names that are imported but never declared, which still resolve at runtime.",
        ],
        "done_when": [
            "Every internal name is listed with its intended registry.",
            "The list is saved where the scanner can read it.",
        ],
        "refs": ["[npm scopes](https://docs.npmjs.com/cli/using-npm/scope)"],
        "meta": {"phase": "recon"},
    },
    {
        "slug": "registry-scope-claim-check",
        "title": "Check whether a private scope is claimed publicly",
        "summary": "Look up the scope on the public registry before you trust it, because an unclaimed scope lets anyone publish under your own namespace",
        "use_when": "the project depends on scoped packages such as @acme/design-tokens",
        "avoid_when": "the scope is an organisation on the public registry with enforced membership",
        "tags": ["registry", "scope", "namespace"],
        "steps": [
            "Query the public registry for the organisation that owns the scope.",
            "If it resolves, record the owning user or org and its member list visibility.",
            "If it does not resolve, record that the scope is unclaimed, which is the finding.",
            "Attempt nothing further on the public registry; the check is read-only.",
        ],
        "signals": ["scope-query-answered", "owner-recorded", "claim-status-recorded"],
        "patterns": [
            (
                "scope lookup",
                "curl -sS -o /dev/null -w '%{http_code}\\n' https://registry.npmjs.org/-/org/acme/user",
            )
        ],
        "pitfalls": [
            "Reporting an unclaimed scope as exploitable without confirming the private package name is used unresolved.",
            "Publishing anything to prove the claim; that is a change to a third-party system and out of scope.",
        ],
        "done_when": [
            "Each scope in use has a recorded claim status and owner.",
            "Any unclaimed scope is linked to the packages that depend on it.",
        ],
        "refs": ["[npm organizations](https://docs.npmjs.com/organizations)"],
        "meta": {"phase": "registry"},
    },
    {
        "slug": "registry-maintainer-change",
        "title": "Detect a maintainer or ownership change",
        "summary": "Compare the maintainer list across the versions you depend on, because a package that gained a maintainer six weeks ago is a different trust proposition than the one in your review notes",
        "use_when": "the dependency was pinned long ago and nobody has re-reviewed it",
        "avoid_when": "the package has a single maintainer and always has",
        "tags": ["registry", "maintainers", "ownership"],
        "steps": [
            "Fetch the registry document and record the maintainer list with the current version.",
            "Fetch the same fields for the version you have pinned.",
            "Diff the two lists and record additions and removals with publish dates.",
            "For an addition, record the new maintainer's other packages, which is how a takeover is recognised.",
        ],
        "signals": ["maintainer-diff-recorded", "dates-captured", "other-packages-listed"],
        "patterns": [
            (
                "maintainer diff",
                "curl -sS https://registry.npmjs.org/PKG | jq -r '.versions[.\\\"dist-tags\\\".latest].maintainers[]?.name' | sort > now.txt\ndiff pinned.txt now.txt || true",
            )
        ],
        "pitfalls": [
            "Treating an added maintainer as malicious without evidence; it is a reason to look, not a finding.",
            "Comparing only the latest version, so a change that happened before your pin is missed.",
        ],
        "done_when": [
            "The maintainer list for both versions is recorded with dates.",
            "Any addition is either explained or escalated.",
        ],
        "refs": ["[npm provenance](https://docs.npmjs.com/generating-provenance-statements)"],
        "meta": {"phase": "registry"},
    },
    {
        "slug": "registry-yank-republish",
        "title": "Check for a yanked version that came back",
        "summary": "Look for versions that were unpublished then republished with different content, because a lockfile pin to that version no longer identifies the bytes you reviewed",
        "use_when": "the lockfile pins exact versions and the project installs from the public registry",
        "avoid_when": "your registry mirror pins by digest and refuses re-published content",
        "tags": ["registry", "yank", "republish"],
        "steps": [
            "For each pinned version, record the dist integrity value from the registry document.",
            "Compare it with the integrity recorded in the lockfile.",
            "Where they differ, record both and the publish time, which is the evidence of a republish.",
            "Re-run the install in a clean cache and confirm which bytes arrive.",
        ],
        "signals": ["integrity-compared", "mismatch-recorded", "clean-install-confirmed"],
        "patterns": [
            (
                "compare pin with registry",
                "jq -r '.packages[\"node_modules/PKG\"].integrity' package-lock.json\ncurl -sS https://registry.npmjs.org/PKG/1.2.3 | jq -r '.dist.integrity'",
            )
        ],
        "pitfalls": [
            "Comparing integrity for the wrong version because the lockfile resolved a different one.",
            "Reporting a mismatch caused by a private mirror rewriting tarballs.",
        ],
        "done_when": [
            "Every pinned version in scope has both integrity values recorded.",
            "Mismatches are either explained by the mirror or raised.",
        ],
        "refs": ["[npm dist.integrity](https://docs.npmjs.com/cli/using-npm/registry)"],
        "meta": {"phase": "registry"},
    },
    {
        "slug": "registry-tarball-source-diff",
        "title": "Diff a published tarball against its source tag",
        "summary": "Download the tarball the registry serves and compare it with the matching git tag, because a published package can contain files the repository never had",
        "use_when": "the package runs at install time or ships a native build step",
        "avoid_when": "the package is a thin re-export whose published output is reproducible from the tag by inspection",
        "tags": ["registry", "tarball", "diff"],
        "steps": [
            "Download the exact tarball for the pinned version and record its shasum.",
            "Extract it into a scratch directory that is not on any load path.",
            "Clone the repository at the tag the version claims and compare the two trees.",
            "Report files that exist only in the tarball, and inspect any script those files are wired to.",
        ],
        "signals": ["tarball-hashed", "trees-compared", "extra-files-listed"],
        "patterns": [
            (
                "fetch and hash",
                "curl -sSL https://registry.npmjs.org/PKG/-/PKG-1.2.3.tgz -o pkg.tgz\nsha256sum pkg.tgz\ntar tzf pkg.tgz | sort > tarball-files.txt",
            )
        ],
        "pitfalls": [
            "Extracting the tarball inside the project so its package.json shadows the real one.",
            "Diffing against a branch tip rather than the tag, which produces noise instead of evidence.",
        ],
        "done_when": [
            "The tarball hash is recorded next to the registry's published value.",
            "Every file present only in the tarball is listed and explained.",
        ],
        "refs": ["[npm pack](https://docs.npmjs.com/cli/commands/npm-pack)"],
        "meta": {"phase": "registry"},
    },
    {
        "slug": "registry-new-package-triage",
        "title": "Triage a newly published package in your tree",
        "summary": "Decide in ten minutes whether a package that appeared last week is a legitimate dependency or a name someone registered to be installed",
        "use_when": "the resolved tree contains a version published after your last review",
        "avoid_when": "the package predates the project and has a long publish history",
        "tags": ["registry", "triage", "new"],
        "steps": [
            "Record the first publish date, the version count and the maintainer count.",
            "Read the package's source for network calls, child processes and environment reads.",
            "Check whether the name is one edit from a package already in the tree.",
            "Record the verdict with the evidence that decided it, and keep the tarball.",
        ],
        "signals": ["dates-recorded", "source-read", "distance-checked"],
        "patterns": [
            (
                "first publish",
                "curl -sS https://registry.npmjs.org/PKG | jq -r '.time.created, (.versions|length), (.maintainers|length)'",
            )
        ],
        "pitfalls": [
            "Judging by download counts, which a new malicious package can inflate cheaply.",
            "Opening the package's README for instructions instead of its source for behaviour.",
        ],
        "done_when": [
            "The package has a verdict with three supporting facts.",
            "The tarball is retained so the verdict can be re-checked.",
        ],
        "refs": ["[npm registry API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)"],
        "meta": {"phase": "registry"},
    },
    {
        "slug": "confusion-enumerate-internal-names",
        "title": "Enumerate the internal names that are resolvable publicly",
        "summary": "Produce the exact list of internal package names that have no public registration, because that list is the attack surface for dependency confusion",
        "use_when": "the organisation runs a private registry next to a public one",
        "avoid_when": "the build resolves every dependency through one locked registry",
        "tags": ["confusion", "enumeration", "internal"],
        "steps": [
            "Collect internal names from manifests, lockfiles and import statements.",
            "Query the public registry for each name and record the status code.",
            "Record names that return 404 as unregistered, which is the candidate set.",
            "Record names that resolve but whose maintainer is not your organisation, which is the stronger case.",
        ],
        "signals": ["names-collected", "status-codes-recorded", "unregistered-listed"],
        "patterns": [
            (
                "public registration check",
                "while read -r n; do\n  code=$(curl -sS -o /dev/null -w '%{http_code}' --get --data-urlencode \"x=1\" \"https://registry.npmjs.org/$n\")\n  printf '%s %s\\n' \"$code\" \"$n\"\ndone < internal-names.txt",
            )
        ],
        "pitfalls": [
            "Querying names for packages that are already scoped to a private registry, which cannot be confused.",
            "Publishing a placeholder to prove the gap; that is an unauthorised change to a public registry.",
        ],
        "done_when": [
            "Every internal name has a recorded public status.",
            "Unregistered names are listed and tied to the manifests that declare them.",
        ],
        "refs": ["[Dependency confusion](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610)"],
        "meta": {"phase": "confusion"},
    },
    {
        "slug": "confusion-resolution-order",
        "title": "Prove which registry wins for one name",
        "summary": "Show how the client resolves a name when both the private and the public registry can answer, because the answer decides whether the finding is real",
        "use_when": "a name is unregistered publicly and the client is configured with two registries",
        "avoid_when": "the client is pinned to a single registry with no fallback",
        "tags": ["confusion", "resolution", "registries"],
        "steps": [
            "Read the effective npm config for the project, including .npmrc and any environment override.",
            "Record the registry for the exact scope or prefix, not just the default registry.",
            "Resolve one dependency with verbose logging and capture which URL answered.",
            "Record the resolver output as the evidence, with the version it chose.",
        ],
        "signals": ["effective-config-recorded", "url-captured", "version-recorded"],
        "patterns": [
            (
                "resolution trace",
                "npm config get registry\nnpm view internal-billing-client version --loglevel=silly 2>&1 | grep -E 'http fetch|registry' | head -20",
            )
        ],
        "pitfalls": [
            "Reading the global .npmrc and missing the project one, which usually wins.",
            "Concluding the finding from config alone instead of a resolution trace.",
        ],
        "done_when": [
            "The registry that answered for the name is quoted from the log.",
            "The chosen version is recorded with its source URL.",
        ],
        "refs": ["[npm config](https://docs.npmjs.com/cli/using-npm/config)"],
        "meta": {"phase": "confusion"},
    },
    {
        "slug": "confusion-scope-pinning",
        "title": "Pin a private scope to one registry",
        "summary": "Configure the client so a scope can only ever come from the private registry, which removes the fallback that makes confusion possible",
        "use_when": "the organisation publishes under a scope and wants the gap closed rather than monitored",
        "avoid_when": "the packages are unscoped and cannot be renamed to a scope",
        "tags": ["confusion", "scope", "fix"],
        "steps": [
            "Add a scoped registry line for the organisation's scope, with no default fallback for it.",
            "Set the token for that scope only, never globally.",
            "Verify by resolving a package in the scope and confirming the private URL answered.",
            "Record the before and after resolution traces as the fix evidence.",
        ],
        "signals": ["scope-configured", "token-scoped", "resolution-verified"],
        "patterns": [
            (
                ".npmrc",
                "@acme:registry=https://npm.acme.internal/\n//npm.acme.internal/:_authToken=${NPM_TOKEN}\nalways-auth=true",
            )
        ],
        "pitfalls": [
            "Leaving a corporate proxy as the default registry that mirrors public packages, which restores the fallback.",
            "Committing a token to .npmrc instead of reading it from the environment.",
        ],
        "done_when": [
            "Resolution for the scope is proven to hit only the private URL.",
            "The token is environment-provided and absent from the repository.",
        ],
        "refs": ["[npm scope registry config](https://docs.npmjs.com/cli/using-npm/scope)"],
        "meta": {"phase": "confusion"},
    },
    {
        "slug": "confusion-higher-version-wins",
        "title": "Show that a higher public version outranks the private one",
        "summary": "Demonstrate the version arithmetic that makes confusion work, so the finding explains why a newer public release is chosen over the private package you actually wanted",
        "use_when": "a range rather than an exact pin is declared for an internal name",
        "avoid_when": "the name is exact-pinned in every manifest and lockfile",
        "tags": ["confusion", "version", "semver"],
        "steps": [
            "Record the constraint as declared and the private version that satisfies it.",
            "Record what a semver resolution does when a much higher version exists in the other registry.",
            "Show the arithmetic in the report: declared range, private max, hypothetical public max.",
            "State the precondition plainly: the attacker must be able to publish under that name.",
        ],
        "signals": ["constraint-quoted", "private-version-recorded", "arithmetic-shown"],
        "patterns": [
            (
                "range vs pin",
                "jq -r '.dependencies[\"internal-billing-client\"]' package.json   # >=1.0.0\n# a public 99.0.0 satisfies the range and outranks any private 1.x",
            )
        ],
        "pitfalls": [
            "Claiming the attack without the publish precondition, which makes the report unfalsifiable.",
            "Forgetting that an exact pin plus a lockfile removes the choice entirely.",
        ],
        "done_when": [
            "The report shows the declared range and both candidate maximums.",
            "The precondition is stated as a precondition, not as an accomplished fact.",
        ],
        "refs": ["[semver ranges](https://github.com/npm/node-semver#ranges)"],
        "meta": {"phase": "confusion"},
    },
    {
        "slug": "confusion-build-log-evidence",
        "title": "Capture resolver evidence from a real build",
        "summary": "Run the install in a sandbox with logging and keep the log, because a resolver trace from the project's own build is the evidence a maintainer cannot dismiss",
        "use_when": "you need evidence rather than a configuration argument",
        "avoid_when": "running the install would execute untrusted scripts on a machine with credentials",
        "tags": ["confusion", "evidence", "logs"],
        "steps": [
            "Create a disposable environment with no credentials and no access to production networks.",
            "Install with lifecycle scripts disabled and full logging to a file.",
            "Extract the lines that show which URL served the package and which version was chosen.",
            "Keep the log and the exact commands beside the finding.",
        ],
        "signals": ["sandbox-created", "log-captured", "urls-extracted"],
        "patterns": [
            (
                "sandboxed install",
                "npm ci --ignore-scripts --loglevel=silly > install.log 2>&1 || true\ngrep -E 'http fetch GET .* (internal-|@acme/)' install.log | head -20",
            )
        ],
        "pitfalls": [
            "Running the install on a workstation that holds registry tokens, which turns evidence collection into an incident.",
            "Trimming the log until the URL that served the package is gone.",
        ],
        "done_when": [
            "The log names the URL and version for the package in question.",
            "The sandbox had no credentials, and that is recorded.",
        ],
        "refs": ["[npm ci](https://docs.npmjs.com/cli/commands/npm-ci)"],
        "meta": {"phase": "confusion"},
    },
    {
        "slug": "confusion-fix-verification",
        "title": "Verify the confusion fix after it ships",
        "summary": "Re-run the resolution trace after the fix and confirm the public registry can no longer answer for the name, because a fix that only changes a default registry is undone by the next override",
        "use_when": "the remediation claims to have pinned a scope or exact-pinned a name",
        "avoid_when": "the fix is not yet deployed to the environment you can test",
        "tags": ["confusion", "verification", "fix"],
        "steps": [
            "Re-read the effective config in the fixed environment rather than the repository.",
            "Re-run the same resolution trace used before the fix.",
            "Confirm the public registry returns nothing for the name, or that it is never consulted.",
            "Record the before and after traces side by side.",
        ],
        "signals": ["config-reread", "trace-rerun", "before-after-recorded"],
        "patterns": [
            (
                "post-fix check",
                "npm config get @acme:registry\nnpm view internal-billing-client version --loglevel=silly 2>&1 | grep 'http fetch' | head -5",
            )
        ],
        "pitfalls": [
            "Verifying on a developer laptop whose global config differs from CI.",
            "Accepting a fix that removes the name from one manifest while another still declares it unbounded.",
        ],
        "done_when": [
            "The trace after the fix shows only the private registry.",
            "Every manifest that declared the name is covered by the verification.",
        ],
        "refs": ["[npm config](https://docs.npmjs.com/cli/using-npm/config)"],
        "meta": {"phase": "confusion"},
    },
    {
        "slug": "typosquat-edit-distance-scan",
        "title": "Scan a manifest for names one edit away from trusted ones",
        "summary": "Compute edit distance between every declared name and the names you actually trust, because a substitution or a missing hyphen is the cheapest way to be installed by accident",
        "use_when": "the project declares many dependencies and nobody has reviewed the names recently",
        "avoid_when": "the dependency set is small enough to read line by line",
        "tags": ["typosquat", "distance", "scan"],
        "steps": [
            "Collect the trusted names from the organisation's own allowlist, not from the manifest under test.",
            "Normalise case, underscores and dots before comparing, since registries treat them as equivalent variants.",
            "Compute edit distance for each declared name against the allowlist and keep distances of one and two.",
            "Record each near miss with both names and the distance.",
        ],
        "signals": ["allowlist-collected", "distances-computed", "near-misses-listed"],
        "patterns": [
            (
                "deptrial",
                "deptrial scan . --allowlist react --allowlist lodash --allowlist express --fail-on high",
            )
        ],
        "pitfalls": [
            "Using the manifest itself as the allowlist, which makes every name trivially trusted.",
            "Flagging a legitimate short name that happens to be close to another short name without checking its history.",
        ],
        "done_when": [
            "Every declared name has a recorded minimum distance to the allowlist.",
            "Near misses are listed with distance and publish date.",
        ],
        "refs": ["[Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)"],
        "meta": {"phase": "typosquat"},
    },
    {
        "slug": "typosquat-homoglyph-check",
        "title": "Check for homoglyph and unicode lookalikes",
        "summary": "Compare declared names byte by byte against trusted ones, because a Cyrillic character or a zero-width joiner renders identically in a review and resolves to a different package",
        "use_when": "a name renders identically to a trusted one but the install resolves elsewhere",
        "avoid_when": "the name is plain ASCII and matches the trusted name exactly",
        "tags": ["typosquat", "unicode", "homoglyph"],
        "steps": [
            "Dump each declared name as code points, not as rendered text.",
            "Flag names containing characters outside the ASCII range, and names containing zero-width or bidirectional control characters.",
            "Compare the code-point sequence with the trusted name it resembles.",
            "Record the code points in the finding, since the rendered name is the misleading part.",
        ],
        "signals": ["code-points-dumped", "non-ascii-flagged", "comparison-recorded"],
        "patterns": [
            (
                "code points",
                "python -c \"import sys;print([hex(ord(c)) for c in sys.argv[1]])\" 'lοdash'  # Greek omicron",
            )
        ],
        "pitfalls": [
            "Copying the name from a rendered page into a terminal, which normalises it and hides the difference.",
            "Reporting a non-ASCII name as malicious when the registry allows it legitimately.",
        ],
        "done_when": [
            "The code points of both names are in the finding.",
            "Registry resolution for the lookalike is recorded.",
        ],
        "refs": ["[Unicode confusables](https://www.unicode.org/reports/tr39/)"],
        "meta": {"phase": "typosquat"},
    },
    {
        "slug": "typosquat-keyboard-adjacent",
        "title": "Check keyboard-adjacent misspellings",
        "summary": "Catch the mistyped-but-plausible names that edit distance misses, because swapping two adjacent keys produces a different string at the same length and often a real registered package",
        "use_when": "the team installs dependencies by typing them rather than copying from documentation",
        "avoid_when": "dependencies are added only through a reviewed lockfile change",
        "tags": ["typosquat", "keyboard", "typo"],
        "steps": [
            "Build the keyboard-adjacency pairs for the layout the team uses.",
            "For each trusted name, generate the single-key substitution and transposition variants.",
            "Check which variants are registered and, for those, whether they are recent.",
            "Record registered variants with publish date and maintainer count.",
        ],
        "signals": ["variants-generated", "registration-checked", "dates-recorded"],
        "patterns": [
            (
                "adjacent pair check",
                "for v in lodahs lodasj lodashh; do printf '%s %s\\n' \"$(curl -sS -o /dev/null -w '%{http_code}' https://registry.npmjs.org/$v)\" \"$v\"; done",
            )
        ],
        "pitfalls": [
            "Generating thousands of variants against the public registry and getting rate limited mid-scan.",
            "Treating every registered variant as malicious when most are abandoned placeholders.",
        ],
        "done_when": [
            "Registered variants are listed with dates and maintainers.",
            "Rate-limit behaviour during the scan is recorded.",
        ],
        "refs": ["[npm registry API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)"],
        "meta": {"phase": "typosquat"},
    },
    {
        "slug": "typosquat-repo-wide-scan",
        "title": "Scan imports, not just manifests",
        "summary": "Search source files for import statements naming packages absent from every manifest, because an undeclared import still resolves at runtime and nothing in the dependency review sees it",
        "use_when": "the project has dynamic imports or a history of ad-hoc installs",
        "avoid_when": "the build fails closed on any unresolved import",
        "tags": ["typosquat", "imports", "undeclared"],
        "steps": [
            "Extract import specifiers from source files and strip relative paths.",
            "Diff that set against declared dependencies and their transitive closure.",
            "Record each undeclared name with the file and line that imports it.",
            "Check each undeclared name for near-miss distance against the allowlist.",
        ],
        "signals": ["imports-extracted", "diff-produced", "undeclared-listed"],
        "patterns": [
            (
                "import scan",
                "grep -rhoE \"(from|require\\()\\s*['\\\"][^.'\\\"][^'\\\"]*['\\\"]\" src \\\n  | sed -E \"s/.*['\\\"]([^'\\\"]+)['\\\"].*/\\1/\" | cut -d/ -f1 | sort -u > imports.txt",
            )
        ],
        "pitfalls": [
            "Counting scoped names as their first path segment and losing the scope.",
            "Ignoring aliases configured in the bundler, which produce false positives for internal paths.",
        ],
        "done_when": [
            "Every undeclared import has a file and line recorded.",
            "Each one is either added to the manifest or removed from the source.",
        ],
        "refs": ["[npm package.json dependencies](https://docs.npmjs.com/cli/configuring-npm/package-json#dependencies)"],
        "meta": {"phase": "typosquat"},
    },
    {
        "slug": "typosquat-suspicious-package-triage",
        "title": "Triage a suspicious package without installing it",
        "summary": "Read a candidate package from its tarball in a scratch directory, because installing it to see what it does is how the investigation becomes the incident",
        "use_when": "a near-miss or a new dependency needs a verdict",
        "avoid_when": "the package is already installed in the environment under review",
        "tags": ["typosquat", "triage", "static"],
        "steps": [
            "Download the tarball only, and record its hash.",
            "List its files and read the entry point, install scripts and any file that opens a socket or a child process.",
            "Record the network destinations and environment variables it reads.",
            "Write the verdict with the file and line for each claim.",
        ],
        "signals": ["tarball-hashed", "files-listed", "sinks-recorded"],
        "patterns": [
            (
                "static look",
                "tar xzf pkg.tgz -C /tmp/scratch\nrg -n \"child_process|exec\\(|https?://|process\\.env\" /tmp/scratch/package | head -30",
            )
        ],
        "pitfalls": [
            "Running npm install to inspect the package, which executes its install hooks.",
            "Reading only index.js and missing a file referenced from its scripts block.",
        ],
        "done_when": [
            "Every claim in the verdict cites a file and line in the extracted tarball.",
            "The tarball hash is retained with the verdict.",
        ],
        "refs": ["[npm pack](https://docs.npmjs.com/cli/commands/npm-pack)"],
        "meta": {"phase": "typosquat"},
    },
]
