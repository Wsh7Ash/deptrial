"""Part 2 of the deptrial corpus: pinning and install scripts."""

from __future__ import annotations

from typing import Any

SKILLS: list[dict[str, Any]] = [
    {
        "slug": "pinning-exact-npm",
        "title": "Pin npm dependencies exactly",
        "summary": "Replace caret and tilde ranges with exact versions where a lockfile is not the only control, because a range is a promise to accept code you have not reviewed",
        "use_when": "a package is installed without a lockfile, such as a global tool or a standalone script",
        "avoid_when": "a committed lockfile with integrity hashes already governs the install",
        "tags": ["pinning", "npm", "exact"],
        "steps": [
            "List every dependency whose constraint is not an exact version.",
            "Replace each range with the exact version currently resolved, which is the version running in production today.",
            "Re-install and confirm the resolved tree is unchanged apart from the constraint strings.",
            "Record the resolved tree before and after as the change evidence.",
        ],
        "signals": ["ranges-listed", "pins-applied", "tree-compared"],
        "patterns": [
            (
                "exact version",
                "npm pkg set dependencies.lodash=4.17.21\nnpm install --package-lock-only",
            )
        ],
        "pitfalls": [
            "Pinning everything in one commit, which makes a regression impossible to bisect.",
            "Pinning to a version that was never in the lockfile, which silently upgrades the tree.",
        ],
        "done_when": [
            "No dependency in scope has a floating range.",
            "The resolved tree is identical apart from the manifest constraints.",
        ],
        "refs": ["[npm semantic versioning](https://docs.npmjs.com/about-semantic-versioning)"],
        "meta": {"phase": "pinning"},
    },
    {
        "slug": "pinning-pip-upper-bound",
        "title": "Give a pip requirement an upper bound",
        "summary": "Add a compatible-release or an explicit ceiling to a lower-bound-only requirement, because a bare `>=` accepts every future major version including one that is hostile",
        "use_when": "a requirements file declares a lower bound with no upper bound",
        "avoid_when": "the package is pinned by a lockfile with hashes and a policy of never breaking",
        "tags": ["pinning", "pip", "bounds"],
        "steps": [
            "List requirements that declare only a lower bound.",
            "Choose the style: a compatible release for a stable package, an explicit ceiling for one with a history of breaking changes.",
            "Re-resolve and confirm the installed version is unchanged.",
            "Record the version before and after for every changed requirement.",
        ],
        "signals": ["unbounded-listed", "bounds-chosen", "resolution-compared"],
        "patterns": [
            (
                "bounded requirements",
                "requests>=2.28,<3\nnumpy>=1.26,<2",
            )
        ],
        "pitfalls": [
            "Choosing a ceiling below the version you actually run, which downgrades production.",
            "Adding a ceiling that no released version satisfies, which fails the build later.",
        ],
        "done_when": [
            "Every requirement in scope has an upper bound.",
            "The installed versions are unchanged by the edit.",
        ],
        "refs": ["[PEP 440 version specifiers](https://peps.python.org/pep-0440/#version-specifiers)"],
        "meta": {"phase": "pinning"},
    },
    {
        "slug": "pinning-lockfile-generate",
        "title": "Generate and commit a lockfile",
        "summary": "Produce a lockfile that records every resolved version with its integrity hash, because without one two installs of the same commit are two different dependency trees",
        "use_when": "manifests exist and no lockfile does",
        "avoid_when": "the deployable is a library that deliberately leaves resolution to its consumers",
        "tags": ["pinning", "lockfile", "reproducible"],
        "steps": [
            "Generate the lockfile with the package manager the project actually uses, not a different one.",
            "Commit it and enable the CI flag that fails the build when it is out of date.",
            "Re-install from a clean cache and confirm the resolved versions match.",
            "Record the lockfile hash in the review notes.",
        ],
        "signals": ["lockfile-generated", "ci-flag-enabled", "clean-install-matches"],
        "patterns": [
            (
                "generate and enforce",
                "npm install --package-lock-only\ngit add package-lock.json\nnpm ci --ignore-scripts",
            )
        ],
        "pitfalls": [
            "Committing a lockfile generated on another platform, whose optional dependencies differ.",
            "Leaving the lockfile out of the container build context so the image resolves fresh.",
        ],
        "done_when": [
            "The lockfile is committed and CI refuses to install without it.",
            "A clean install resolves exactly the locked versions.",
        ],
        "refs": ["[npm ci](https://docs.npmjs.com/cli/commands/npm-ci)"],
        "meta": {"phase": "pinning"},
    },
    {
        "slug": "pinning-lockfile-integrity",
        "title": "Verify lockfile integrity data is present and enforced",
        "summary": "Confirm every resolved entry carries an integrity hash and that the installer checks it, because a lockfile of version numbers alone still accepts substituted bytes",
        "use_when": "a lockfile exists and you are relying on it as the control",
        "avoid_when": "a registry mirror pins by digest independently of the client",
        "tags": ["pinning", "lockfile", "integrity"],
        "steps": [
            "Count resolved entries and how many carry an integrity or hash field.",
            "Record the installer version, since some legacy modes skip verification.",
            "Install with the lockfile enforced and confirm a deliberately corrupted entry is rejected.",
            "Record both the coverage ratio and the rejection test.",
        ],
        "signals": ["entries-counted", "installer-version-recorded", "rejection-verified"],
        "patterns": [
            (
                "integrity coverage",
                "jq '[.packages | to_entries[] | select(.key != \"\") | select(.value.integrity == null)] | length' package-lock.json",
            )
        ],
        "pitfalls": [
            "Assuming integrity is enforced because the field exists, when the install path uses a legacy resolver.",
            "Corrupting a lockfile entry on a shared branch to test rejection.",
        ],
        "done_when": [
            "Integrity coverage is recorded as a ratio.",
            "A corrupted entry is proven to be rejected in a sandbox.",
        ],
        "refs": ["[npm package-lock.json](https://docs.npmjs.com/cli/configuring-npm/package-lock-json)"],
        "meta": {"phase": "pinning"},
    },
    {
        "slug": "pinning-replace-url-dependency",
        "title": "Replace a URL or git dependency with a registry pin",
        "summary": "Move a dependency off a mutable branch or tarball URL onto content identified by a hash, because a git branch and an HTTP URL both point at bytes that can change without any version changing",
        "use_when": "a manifest declares a git ref, a branch or an http tarball",
        "avoid_when": "the dependency is genuinely private and its registry publishes signed artifacts",
        "tags": ["pinning", "vcs", "url"],
        "steps": [
            "Identify the commit or tarball actually in use and record its hash.",
            "Locate or publish a registry version containing exactly that content.",
            "Switch the manifest to the registry version with an integrity hash.",
            "Re-install and diff the resolved tree against the previous one.",
        ],
        "signals": ["commit-hash-recorded", "registry-version-found", "tree-compared"],
        "patterns": [
            (
                "pin a git ref to a commit",
                "# before\nexpress: github:expressjs/express#main\n# after, when no registry version matches\nexpress: github:expressjs/express#<40-char-sha>",
            )
        ],
        "pitfalls": [
            "Pinning to a branch that gets rebased, which changes the commit under a stable name.",
            "Losing the diff review because the resolved tree changed while the constraint looked equivalent.",
        ],
        "done_when": [
            "No dependency points at a moving ref.",
            "The resolved content is identical before and after, and that is recorded.",
        ],
        "refs": ["[npm git dependencies](https://docs.npmjs.com/cli/configuring-npm/package-json#git-urls-as-dependencies)"],
        "meta": {"phase": "pinning"},
    },
    {
        "slug": "pinning-update-review",
        "title": "Review a dependency bump before merging it",
        "summary": "Read the diff between the two published versions, because an automated update pull request is the easiest place to slip a new install hook past review",
        "use_when": "an automated update changes a dependency version",
        "avoid_when": "the change is a patch release from a package your own team maintains",
        "tags": ["pinning", "updates", "review"],
        "steps": [
            "Fetch both tarballs and diff their file lists and scripts blocks.",
            "Read every change to lifecycle scripts before any other code.",
            "Compare the maintainer list for the new version with the old one.",
            "Record what was reviewed and what was skipped, by file name.",
        ],
        "signals": ["tarballs-diffed", "scripts-reviewed", "maintainers-compared"],
        "patterns": [
            (
                "script diff",
                "tar xzf old.tgz -C /tmp/old && tar xzf new.tgz -C /tmp/new\ndiff -u /tmp/old/package/package.json /tmp/new/package/package.json",
            )
        ],
        "pitfalls": [
            "Approving the bump because the version looks like a patch release.",
            "Reviewing the repository diff instead of the published tarball diff, which differ.",
        ],
        "done_when": [
            "The scripts block diff is recorded for the version pair.",
            "Any new install hook is either justified or the bump is rejected.",
        ],
        "refs": ["[npm diff](https://docs.npmjs.com/cli/commands/npm-diff)"],
        "meta": {"phase": "pinning"},
    },
    {
        "slug": "scripts-inventory-hooks",
        "title": "Inventory every lifecycle hook that runs at install",
        "summary": "List preinstall, install, postinstall and prepare hooks across the tree, because these run before anyone opens the code and are the usual execution point for a compromised package",
        "use_when": "you are reviewing a package.json or an installed dependency tree",
        "avoid_when": "the installer runs with scripts disabled in every environment",
        "tags": ["scripts", "hooks", "install"],
        "steps": [
            "Extract the scripts block from every package.json in the tree, including installed dependencies.",
            "Separate hooks that run at install from those that run at test or build.",
            "For each install hook, record the command and what it invokes.",
            "Sort the list by whether the command reaches the network or a shell.",
        ],
        "signals": ["hooks-extracted", "commands-recorded", "sinks-classified"],
        "patterns": [
            (
                "hooks across the tree",
                "find . -name package.json -not -path '*/node_modules/*' -exec jq -r 'select(.scripts) | .name as $n | .scripts | to_entries[] | select(.key|test(\"preinstall|install|postinstall|prepare\")) | \"\\($n) \\(.key) \\(.value)\"' {} \\;",
            )
        ],
        "pitfalls": [
            "Reading only the top-level package.json and missing hooks in direct dependencies.",
            "Assuming a hook that runs `node build.js` is local, when build.js downloads a prebuilt binary.",
        ],
        "done_when": [
            "Every install hook in the tree is listed with its command.",
            "Each command is classified as local, network or unknown.",
        ],
        "refs": ["[npm scripts](https://docs.npmjs.com/cli/using-npm/scripts)"],
        "meta": {"phase": "scripts"},
    },
    {
        "slug": "scripts-sandbox-install",
        "title": "Install with hooks disabled, then run them deliberately",
        "summary": "Separate installation from execution so you can inspect what arrived before anything runs, because install-time code has no sandbox unless you build one",
        "use_when": "you must resolve and inspect a dependency tree that contains hooks",
        "avoid_when": "the tree ships no hooks and no native build step",
        "tags": ["scripts", "sandbox", "install"],
        "steps": [
            "Install with scripts disabled and record the resolved tree.",
            "Snapshot the filesystem before running any hook.",
            "Run each hook in a disposable container with no credentials and no host mounts.",
            "Diff the filesystem afterwards and record writes outside the project directory.",
        ],
        "signals": ["tree-resolved", "snapshot-taken", "diff-recorded"],
        "patterns": [
            (
                "two-phase install",
                "npm ci --ignore-scripts\n# then, inside a disposable container only:\nnpm rebuild 2>&1 | tee hooks.log",
            )
        ],
        "pitfalls": [
            "Running hooks on the review workstation because it is faster, with registry tokens in the environment.",
            "Forgetting that `npm rebuild` re-runs hooks for packages installed without them.",
        ],
        "done_when": [
            "The resolved tree was produced before any hook ran.",
            "Hook execution happened only in a container with no credentials, and that is recorded.",
        ],
        "refs": ["[npm ignore-scripts](https://docs.npmjs.com/cli/using-npm/config#ignore-scripts)"],
        "meta": {"phase": "scripts"},
    },
    {
        "slug": "scripts-behaviour-diff",
        "title": "Diff what a hook does between two versions",
        "summary": "Compare the commands and the files a lifecycle hook touches across versions, because a hook that was benign in one release can become a downloader in the next with no change to its name",
        "use_when": "a dependency version moved and the package has install hooks",
        "avoid_when": "the package has no lifecycle hooks in either version",
        "tags": ["scripts", "diff", "behaviour"],
        "steps": [
            "Record the hook command strings for both versions from their tarballs.",
            "Record the files each hook reads and writes, from a container run of each version.",
            "Diff both the commands and the touched-file sets.",
            "Report any new network destination or new write outside the package directory.",
        ],
        "signals": ["commands-diffed", "file-sets-diffed", "destinations-listed"],
        "patterns": [
            (
                "compare hook commands",
                "jq -r '.scripts' /tmp/old/package/package.json > old-scripts.json\njq -r '.scripts' /tmp/new/package/package.json > new-scripts.json\ndiff -u old-scripts.json new-scripts.json || true",
            )
        ],
        "pitfalls": [
            "Comparing only the command text when the invoked script file changed instead.",
            "Running both versions in the same container, so the second inherits the first's writes.",
        ],
        "done_when": [
            "Both the command diff and the touched-file diff are recorded.",
            "Every new destination is either explained or raised.",
        ],
        "refs": ["[npm scripts](https://docs.npmjs.com/cli/using-npm/scripts)"],
        "meta": {"phase": "scripts"},
    },
    {
        "slug": "scripts-allowlist-policy",
        "title": "Allow only known install hooks",
        "summary": "Turn install scripts from an open door into an allowlist, so a new hook in any dependency fails the build instead of running unreviewed",
        "use_when": "the project cannot disable scripts because some dependencies need a native build",
        "avoid_when": "the package manager version in use cannot restrict hooks per package",
        "tags": ["scripts", "policy", "allowlist"],
        "steps": [
            "Record the packages that genuinely need an install hook, with the reason for each.",
            "Enable the package manager's script restriction and allow only those packages.",
            "Run a clean install and confirm the allowed hooks ran and every other hook was skipped.",
            "Commit the allowlist so every addition is a visible diff.",
        ],
        "signals": ["allowlist-recorded", "restriction-enabled", "skip-verified"],
        "patterns": [
            (
                "pnpm allowlist",
                "# pnpm-workspace.yaml or package.json\nonlyBuiltDependencies:\n  - esbuild\n  - sharp",
            )
        ],
        "pitfalls": [
            "Disabling scripts globally, breaking a native dependency, then re-enabling everything.",
            "Leaving the allowlist out of version control so nobody reviews additions.",
        ],
        "done_when": [
            "Every allowed hook is listed with a justification.",
            "A clean install proves unlisted hooks are skipped.",
        ],
        "refs": ["[pnpm onlyBuiltDependencies](https://pnpm.io/settings#onlybuiltdependencies)"],
        "meta": {"phase": "scripts"},
    },
    {
        "slug": "scripts-ci-enforcement",
        "title": "Enforce the script policy in CI",
        "summary": "Install with hooks restricted and fail the build on lockfile or allowlist drift, because a policy that lives only in a document is not a control",
        "use_when": "the policy exists and you want it to hold for every build",
        "avoid_when": "CI cannot install dependencies at all",
        "tags": ["scripts", "ci", "enforcement"],
        "steps": [
            "Set the install step to the restricted form and commit the allowlist.",
            "Add a step that fails when the lockfile changes during install.",
            "Add a step that reports which hooks were skipped, so a new hook is visible in the log.",
            "Record a run where an added hook produced a red build.",
        ],
        "signals": ["restricted-install", "drift-step-added", "skip-report-present"],
        "patterns": [
            (
                "workflow steps",
                "- name: install\n  run: npm ci --ignore-scripts\n- name: lockfile drift\n  run: git diff --exit-code -- package-lock.json",
            )
        ],
        "pitfalls": [
            "Placing the drift check before the install, when nothing has changed yet.",
            "Making the skip report an annotation nobody reads instead of a step that fails on an unknown hook.",
        ],
        "done_when": [
            "A build with an unlisted hook is proven to fail.",
            "The skip report appears in the job log on every run.",
        ],
        "refs": ["[npm ci](https://docs.npmjs.com/cli/commands/npm-ci)"],
        "meta": {"phase": "scripts"},
    },
]
