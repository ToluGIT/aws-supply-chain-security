# aws-supply-chain-security

Keyless container supply chain pipeline: build → SBOM → Inspector scan gate → Cosign keyless sign → SLSA provenance → verify.

This repo is the GitHub Actions side of a portfolio project demonstrating end-to-end software supply chain security on AWS. The image is signed with Cosign keyless (Sigstore), so it can be cryptographically tied to this exact repo and workflow, and verified by anyone without shared secrets.

## Layout

| Path | Purpose |
|---|---|
| `app/` | Clean sample app — minimal deps, passes the CVE gate |
| `app-vulnerable/` | Same app with deliberately CVE-laden dependencies — fails the CVE gate (test) |
| `.github/workflows/supply-chain.yml` | The pipeline |

## What the pipeline does

1. Assume an AWS IAM role via GitHub OIDC — no stored AWS keys
2. Build the container image, push to a private ECR repo with an immutable `git-<sha>` tag
3. Amazon Inspector scans the image on push
4. CVE gate: fail closed if any CRITICAL finding
5. Generate a CycloneDX SBOM with Syft
6. (Phase 3) Cosign keyless sign + SLSA Level 3 provenance + verification gate

## Verifying a signed image

```bash
cosign verify \
  --certificate-identity-regexp "https://github.com/ToluGIT/aws-supply-chain-security/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  221082197153.dkr.ecr.us-east-1.amazonaws.com/scs-prod-ecr-app:git-<sha>
```

The two `--certificate-*` flags are the security boundary: without them, verification only proves "signed by some keyless workflow"; with them, it proves "signed by this repo's workflow."
