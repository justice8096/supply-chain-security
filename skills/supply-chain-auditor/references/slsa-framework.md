# SLSA Framework v1.0 Reference

## Overview

SLSA (Supply chain Levels for Software Artifacts) is a framework for securing software artifacts against tampering and unauthorized modification. Developed by Google, Microsoft, Purdue, and others, SLSA provides four maturity levels (L0-L4) that progressively strengthen security controls across source, build, and packaging.

## SLSA Levels

### Level 0 (L0): No Requirements
**State**: Baseline; no security properties

- No provenance available
- No build recipe
- No version control
- Ad-hoc or manual builds

**Use case**: Internal tools, experiments, research prototypes

### Level 1 (L1): Provenance, Version Control, Build Recipe

**Provenance**: Machine-readable record of artifact generation
- Artifact ID (e.g., docker.io/acme/app@sha256:abcd...)
- Builder ID (e.g., GitHub Actions)
- Build timestamp
- Build parameters (git ref, commit hash)

**Requirements**:
1. Artifact has available provenance
2. Version control system (Git, Mercurial, etc.)
3. Build executed on hosted build platform (GitHub, GitLab, Jenkins)
4. Build recipe (Dockerfile, Makefile, build script) committed to version control

**Verification**: Provenance references source commit; recipe is verifiable

**Effort**: ~1-2 days; mostly infrastructure setup

**Implementation**:
```yaml
# GitHub Actions provenance (L1)
name: Build and Release
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: ./build.sh
      - uses: actions/upload-artifact@v3
        with:
          name: artifact
          path: dist/
```

### Level 2 (L2): Signed Provenance, No Modification During Build

**Provenance Signing**: Cryptographic proof of artifact authenticity
- Signed by build platform (e.g., Sigstore OIDC tokens)
- Verifiable by third parties
- Tamper-evident (signature invalidated if modified)

**Source Integrity**: Repository not modified during build
- Read-only checkout
- No dynamic source updates
- Commit hash pinned

**Build Logs**: Retained for audit
- Build steps logged
- Accessible for incident response
- Not cleared post-build

**Requirements** (all L1 + these):
1. Provenance signed by build platform
2. Repository commits immutable (no force-push, rebases only)
3. Build platform prevents repository modification
4. Build logs retained and accessible (90+ days recommended)

**Verification**: Signature validation, commit history immutability

**Effort**: ~2-5 days; storage and signing infrastructure

**Implementation**:
```yaml
# GitHub Actions with provenance signing
- uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.4.0
  with:
    base64-subjects: ${{ needs.build.outputs.digests }}
    upload-assets: true
```

### Level 3 (L3): Build Script Isolation, Immutable Source, Retention

**Build Isolation**: Untrusted code cannot modify build
- Build environment ephemeral (destroyed post-build)
- Dependencies fetched from network (not ambient system)
- No user code execution outside build container
- Build as a service (BaaS) or containerized

**Source Immutability**: Repository enforced immutable
- No rebase-and-force-push
- All commits signed (GPG/SSH)
- Pull requests require review + approval

**Artifact Integrity**: Hash verification
- Artifacts referenced by content hash (digest)
- Transitive dependencies pinned
- No floating versions (package.json with ^ or ~)

**Requirements** (all L2 + these):
1. Build isolated: runs in container/VM without access to ambient system state
2. Repository prevents historical rewriting (no force-push)
3. All commits signed and require merge approval
4. Artifacts referenced by hash (no floating tags)
5. All transitive dependencies pinned

**Effort**: ~1-3 weeks; architectural changes to CI/CD, version pinning

**Implementation**:
```dockerfile
# Containerized, isolated build
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y node.js
COPY . /src
WORKDIR /src
RUN npm ci --prefer-offline --no-audit
RUN npm run build
```

### Level 4 (L4): Hermetic Build, All Dependencies Pinned, Reproducible, Cryptographic Identity

**Hermetic Build**: Complete isolation, all inputs specified
- No ambient OS state used
- Network access disabled (or to whitelist only)
- All dependencies specified explicitly
- Build is reproducible: same inputs = same outputs

**Dependency Pinning**: All transitive deps locked
- Cargo.lock, package-lock.json, poetry.lock, go.sum committed
- No floating ranges (^1.0.0)
- Transitive deps pinned to commit hash or digest
- Binary caches validated by hash

**Reproducibility**: Deterministic builds
- Same source + same environment = identical artifact
- Byte-for-byte reproducibility (or hash match)
- Compiler options fixed
- Timestamps deterministic

**Cryptographic Identity**: Artifact bound to identity
- Signing key tied to build identity (e.g., Sigstore)
- Revocation capability (if key compromised)
- Artifact only created by authorized builder
- No key shared across projects

**Requirements** (all L3 + these):
1. Build is hermetic: all inputs declared, reproducible
2. All transitive dependencies pinned by hash/digest
3. Artifacts built twice independently produce identical results
4. Signing keys separate per build, non-shared
5. Revocation capability for signing keys

**Effort**: ~4-12 weeks; hermetic build infrastructure, reproducibility testing

**Implementation**:
```bash
# Reproducible Rust build
cargo build --locked --release --target-dir /tmp/build1
cargo build --locked --release --target-dir /tmp/build2
diff /tmp/build1/release/app /tmp/build2/release/app  # Must be identical
```

## SLSA in Practice

### GitHub Actions Path to SLSA 3

1. **L1**: Use GitHub Actions with checkout and upload-artifact
2. **L2**: Integrate SLSA GitHub Generator for signed provenance
3. **L3**:
   - Pin all actions to commit hash: `@a1b2c3d4e5f6` not `@v1`
   - Enable branch protection (require reviews, dismiss stale PRs)
   - Enable commit signing (GitHub's signature or GPG)
   - Use `npm ci` with lockfile instead of `npm install`

### Container Image Supply Chain

```dockerfile
# SLSA L3+ container build
FROM alpine:3.18@sha256:abcd1234...  # Pin by digest
RUN apk add --no-cache node npm
COPY package*.json ./
RUN npm ci --prefer-offline --no-audit
COPY . .
RUN npm run build
FROM alpine:3.18@sha256:abcd1234...
COPY --from=builder /app/dist /app
ENTRYPOINT ["node", "/app/index.js"]
```

Build with signing:
```bash
docker build -t myapp:1.0.0 .
cosign sign --key cosign.key myapp:1.0.0@sha256:xyz...
# Verify
cosign verify --key cosign.pub myapp:1.0.0@sha256:xyz...
```

## SLSA vs Other Standards

| Standard | Focus | Maturity Levels | Key Requirement |
|----------|-------|-----------------|-----------------|
| SLSA | Artifact integrity | 0-4 | Provenance |
| SSC (NIST 800-218) | Process maturity | L0-L3 | Secure practices |
| Sigstore | Key management | Implicit | Key issuance, signing |
| CycloneDX/SPDX | Component transparency | N/A | SBOM format |

## Threat Model

**SLSA Protects Against**:
- Artifact tampering (substitution of malicious version)
- Unauthorized modification (compromised developer account)
- Ambient OS contamination (malware on build machine)
- Dependency injection (attacker-controlled dependency)
- Account compromise recovery (revoke signing keys)

**SLSA Does NOT Protect Against**:
- Malicious source code (code review required)
- Logic bugs (testing required)
- Zero-day vulnerabilities (patching required)
- Supply chain attacks upstream of build (e.g., typosquatting)

## Assessment Methodology

### Current Level Determination

**L0**: No CI/CD, manual builds, no version control
**L1**: Has Git, CI/CD, build recipe visible
**L2**: Provenance available, immutable commits, build logs retained
**L3**: Build isolation, commit signing enforced, deps pinned
**L4**: Hermetic builds, reproducibility verified, keys separated

### Gap Analysis

1. Review build logs for L2 gaps (unsigned provenance, modifiable repo)
2. Check CI/CD container usage (L3 requires isolation)
3. Audit dependency management (lockfiles, pinned ranges)
4. Verify signing keys per-build (L4 requirement)
5. Test reproducibility (rebuild artifact, compare hash)

### Improvement Roadmap

- **Quick wins** (L0 to L1): Migrate to GitHub Actions, commit Dockerfile
- **Medium-term** (L1 to L2): Integrate SLSA generator, enforce commit signing
- **Long-term** (L2 to L3/L4): Hermetic build system, reproducibility testing

## Tools

- **SLSA GitHub Generator**: Automatic provenance generation for GitHub Actions
- **cosign**: Sign and verify container images (Sigstore)
- **syft/grype**: SBOM generation and vulnerability scanning
- **nix**: Deterministic, reproducible builds
- **bazel**: Hermetic build system with dependency pinning
- **OPA/Rego**: Policy as code for supply chain validation

## Resources

- Official SLSA Framework: https://slsa.dev
- SLSA GitHub Generator: https://github.com/slsa-framework/slsa-github-generator
- Sigstore Project: https://sigstore.dev
- NIST 800-218: Secure Software Development Framework
