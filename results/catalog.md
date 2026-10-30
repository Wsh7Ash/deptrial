deptrial Skill Catalog

50 skills across 10 phases.

| `slug` | title | phase |
|---|---|---|
| `ci-cache-key-trust` | Make cache keys unforgeable | ci |
| `ci-dependency-review-gate` | Fail the build on a new high-severity dependency finding | ci |
| `ci-pull-request-target` | Keep untrusted pull request code out of secret-bearing jobs | ci |
| `ci-secret-exposure` | Check what an install step can read | ci |
| `ci-token-least-privilege` | Reduce the pipeline token to what the job needs | ci |
| `confusion-build-log-evidence` | Capture resolver evidence from a real build | confusion |
| `confusion-enumerate-internal-names` | Enumerate the internal names that are resolvable publicly | confusion |
| `confusion-fix-verification` | Verify the confusion fix after it ships | confusion |
| `confusion-higher-version-wins` | Show that a higher public version outranks the private one | confusion |
| `confusion-resolution-order` | Prove which registry wins for one name | confusion |
| `confusion-scope-pinning` | Pin a private scope to one registry | confusion |
| `pinning-exact-npm` | Pin npm dependencies exactly | pinning |
| `pinning-lockfile-generate` | Generate and commit a lockfile | pinning |
| `pinning-lockfile-integrity` | Verify lockfile integrity data is present and enforced | pinning |
| `pinning-pip-upper-bound` | Give a pip requirement an upper bound | pinning |
| `pinning-replace-url-dependency` | Replace a URL or git dependency with a registry pin | pinning |
| `pinning-update-review` | Review a dependency bump before merging it | pinning |
| `provenance-attestation-check` | Check whether a package publishes a build attestation | provenance |
| `provenance-missing-attestation-triage` | Decide what to do about a missing attestation | provenance |
| `provenance-reproduce-build` | Rebuild a package from source and compare | provenance |
| `provenance-source-tag-match` | Confirm the published version matches a real tag | provenance |
| `provenance-verify-signature` | Verify a signature instead of reading it | provenance |
| `recon-ci-install-path` | Read the CI install path before blaming the manifest | recon |
| `recon-dependency-graph` | Split direct dependencies from the resolved tree | recon |
| `recon-manifest-inventory` | Inventory every manifest and lockfile in the tree | recon |
| `recon-private-scope-map` | Map which names are supposed to be private | recon |
| `recon-registry-metadata` | Read registry metadata for the packages that matter | recon |
| `registry-maintainer-change` | Detect a maintainer or ownership change | registry |
| `registry-new-package-triage` | Triage a newly published package in your tree | registry |
| `registry-scope-claim-check` | Check whether a private scope is claimed publicly | registry |
| `registry-tarball-source-diff` | Diff a published tarball against its source tag | registry |
| `registry-yank-republish` | Check for a yanked version that came back | registry |
| `review-disclosure-timeline` | Agree the disclosure timeline before you report | review |
| `review-finding-evidence` | Write a supply-chain finding that can be rechecked | review |
| `review-fix-verification` | Verify the dependency fix with the same evidence | review |
| `review-severity-basis` | Justify severity from capability, not from rule name | review |
| `scripts-allowlist-policy` | Allow only known install hooks | scripts |
| `scripts-behaviour-diff` | Diff what a hook does between two versions | scripts |
| `scripts-ci-enforcement` | Enforce the script policy in CI | scripts |
| `scripts-inventory-hooks` | Inventory every lifecycle hook that runs at install | scripts |
| `scripts-sandbox-install` | Install with hooks disabled, then run them deliberately | scripts |
| `tools-origin-and-licence-check` | Check where each dependency actually comes from | tools |
| `tools-run-manifest-scan` | Run the manifest scan and read the report | tools |
| `tools-sbom-generate` | Produce an SBOM from the resolved tree | tools |
| `tools-suppression-with-reason` | Suppress a finding with a reason, not a comment | tools |
| `typosquat-edit-distance-scan` | Scan a manifest for names one edit away from trusted ones | typosquat |
| `typosquat-homoglyph-check` | Check for homoglyph and unicode lookalikes | typosquat |
| `typosquat-keyboard-adjacent` | Check keyboard-adjacent misspellings | typosquat |
| `typosquat-repo-wide-scan` | Scan imports, not just manifests | typosquat |
| `typosquat-suspicious-package-triage` | Triage a suspicious package without installing it | typosquat |
