---
name: provenance-verify-signature
description: "Check the artifact signature against the publisher identity you expect, because a signature that verifies against the wrong identity proves only that someone signed it. Use when the package ships a signature bundle or a registry attestation"
pack: deptrial
version: 1.0.0
category: supply-chain
tags: [provenance, signature, identity]
phase: provenance
---

# Verify a signature instead of reading it

> Check the artifact signature against the publisher identity you expect, because a signature that verifies against the wrong identity proves only that someone signed it

**Use when:** the package ships a signature bundle or a registry attestation

**Avoid when:** no signature exists and none is claimed

## Procedure

1. Record the identity the signature claims, including the issuer and the workflow ref.
2. Verify with the tool the ecosystem documents, offline against the stored bundle.
3. Compare the verified identity with the expected repository and workflow.
4. Record the verification output verbatim, including the certificate subject.

## Signals

- identity-recorded
- verification-run
- subject-compared

## Patterns

**1. sigstore verify**

```
cosign verify-blob --bundle pkg.sigstore --certificate-identity-regexp 'https://github.com/ORG/.+' pkg.tgz
```

## Pitfalls

- Accepting a valid signature without checking which identity it belongs to.
- Verifying online against a transparency log from a network you do not control, then trusting the response.

## Done when

- The verified identity matches the expected publisher, or the mismatch is recorded.
- The verification command and output are stored with the finding.

## References

- [sigstore cosign](https://docs.sigstore.dev/cosign/overview/)
