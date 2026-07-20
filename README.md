# aws-supply-chain-security

This repository holds the GitHub Actions pipeline for a portfolio project. The project demonstrates software supply chain security on AWS.

The pipeline builds a container image, generates an SBOM, scans the image with Amazon Inspector, signs the image with Cosign in keyless mode, attaches SLSA provenance data, and verifies every check before it calls the image deployable.

Cosign keyless signing uses Sigstore. This method ties the signature to the exact repository and workflow that built the image. Anyone can verify the signature. Verification needs no shared secret.

## Layout

| Path | Purpose |
|---|---|
| `app/` | Clean sample app. Minimal dependencies. Passes the CVE gate. |
| `app-vulnerable/` | Same app, with dependencies that carry known CVEs on purpose. Fails the CVE gate. This is a test fixture. |
| `tamper/` | A Dockerfile that builds a tampered image from a signed base image. This is a test fixture for the signature-verification gate. |
| `.github/workflows/supply-chain.yml` | The pipeline. |

## What the Pipeline Does

1. The pipeline assumes an AWS IAM role through GitHub OIDC. It stores no AWS keys.
2. The pipeline builds the container image. It pushes the image to a private ECR repository with an immutable `git-<sha>` tag.
3. Amazon Inspector scans the image on push.
4. The CVE gate checks the scan result. Note: the gate fails closed only on findings that have a fix available. A CRITICAL finding with no fix, such as a known issue in a base image package, does not fail the gate on its own. This is a deliberate design choice. A gate that blocks on every CRITICAL finding, fixable or not, blocks every build forever.
5. The pipeline generates a CycloneDX SBOM with Syft.
6. The pipeline signs the image with Cosign in keyless mode. It attaches a SLSA provenance attestation. Note on the SLSA level: this pipeline reaches SLSA Build Level 2, not Level 3. The provenance attestation runs in the same job as the build. Level 3 needs an isolated builder job that the build job itself cannot alter.
7. The pipeline runs a verify gate. This gate checks the signature, the certificate identity, and the SLSA attestation together. The pipeline calls the image deployable only when every check passes.

## Verifying a Signed Image

```bash
cosign verify \
  --certificate-identity-regexp "https://github.com/ToluGIT/aws-supply-chain-security/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/scs-prod-ecr-app:git-<sha>
```

Note on the 2 `--certificate-*` flags: these flags are the security boundary of this check. Without them, a verify command proves only that some keyless workflow signed the image. With them, a verify command proves that this exact repository's workflow signed the image.
