# Supply Chain Audit Report
**Project**: supply-chain-security (Supply Chain Security Auditor Skill)
**Date**: 2026-03-29
**Commit**: 471a381 — style: fix flake8 violations
**Branch**: master
**Audit Type**: POST-FIX Re-audit
**Prior Audit Result**: FAIL — SLSA Level 1 (partial), 5 issues (2 HIGH, 3 MEDIUM)

---

## Executive Summary

All 5 supply chain issues from the prior audit have been remediated. GitHub Actions are now fully SHA-pinned, workflow permissions are restricted to `contents: read`, JSON output in scripts uses safe `jq --arg` construction, the permissions detection regex is correct, and the `wc -l` portability bug is fixed. SLSA level has advanced from L1 (partial) to L2.

**Overall Result: PASS**

### Before / After Delta

| Category | Prior | Current | Delta |
|----------|-------|---------|-------|
| SLSA Level | L1 (partial) | L2 | +1 |
| HIGH Issues | 2 | 0 | -2 RESOLVED |
| MEDIUM Issues | 3 | 0 | -3 RESOLVED |
| SHA-pinned Actions | No | Yes | RESOLVED |
| Least-Privilege Permissions | No | Yes | RESOLVED |
| jq-safe JSON output | Partial (npm only) | Full | RESOLVED |
| Signed Commits | Verified | Verified | — |
| SBOM Coverage | npm/Python/Rust/Go | npm/Python/Rust/Go | — |

---

## SLSA Assessment

### Current Level: SLSA L2

| Requirement | Level | Status | Evidence |
|-------------|-------|--------|----------|
| Scripted build | L1 | PASS | lint.yml defines all build steps |
| Build provenance available | L1 | PASS | GitHub Actions generates workflow run metadata |
| Hosted build platform | L2 | PASS | GitHub-hosted `ubuntu-latest` runners |
| Source version controlled | L2 | PASS | Git repository with signed commits |
| Build isolated from developer machine | L2 | PASS | Ephemeral GitHub-hosted runners |
| All CI actions SHA-pinned | L2 | PASS | All 3 actions pinned to commit hashes |
| Source integrity verified (branch protection + reviews) | L3 | PARTIAL | No required reviewers configured |
| Non-falsifiable provenance (Sigstore/in-toto) | L3 | NOT MET | Not implemented |
| Hermetic build (no runtime fetches) | L4 | NOT MET | `pip install flake8` fetches at runtime |

**Path to L3**: Add branch protection rule with at least 1 required reviewer and a CODEOWNERS file. Enable `actions/attest-build-provenance` for Sigstore-backed attestations.

**Path to L4**: Replace the `pip install flake8` step with a pre-baked container image (`docker://ghcr.io/...`) pinned by digest.

---

## GitHub Actions Dependency Pinning

### Prior State (FAIL)
All actions referenced mutable version tags that any upstream maintainer could re-point to different (potentially malicious) commits:
- `actions/checkout@v4`
- `ludeeus/action-shellcheck@2.0.0`
- `actions/setup-python@v5`

### Current State (PASS)
All actions are pinned to immutable commit SHAs with inline version comments:

```yaml
- uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5  # v4
- uses: ludeeus/action-shellcheck@00cae500b08a931fb5698e11e79bfbd38e612a38  # 2.0.0
- uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
```

This eliminates CWE-829 (Inclusion of Functionality from Untrusted Control Sphere) for the CI pipeline.

---

## CI/CD Permissions Hardening

### Prior State (FAIL)
No `permissions` block in lint.yml. GITHUB_TOKEN defaulted to `contents: write` and additional scopes depending on repository settings, enabling potential privilege escalation if a workflow step was compromised.

### Current State (PASS)
```yaml
permissions:
  contents: read
```

`contents: read` is the minimum required for `actions/checkout`. All other GITHUB_TOKEN capabilities (write, pull_request, issues, packages, etc.) are implicitly denied. This resolves H2 / CWE-269 (Improper Privilege Management).

---

## Script Security Hardening

### JSON Construction (CWE-78) — RESOLVED

All JSON output in the auditor scripts now uses `jq -n --arg` for safe construction:

| Generator | Prior Method | Current Method | Status |
|-----------|-------------|----------------|--------|
| `generate_python_sbom` | Shell heredoc with `${name}` | `jq -n --arg name "$name"` | RESOLVED |
| `generate_rust_sbom` | Shell heredoc with `${name}`, `${version}` | `jq -n --arg name ... --arg version ...` | RESOLVED |
| `generate_go_sbom` | Shell heredoc with `${name}` | `jq -n --arg name "$name"` | RESOLVED |
| `audit_github_actions` findings | `echo '{"file": "'"$workflow_name"'"}' ` | `jq -n --arg file "$workflow_name"` | RESOLVED |

### Permissions Detection Regex (CWE-697) — RESOLVED

| | Prior Pattern | Current Pattern |
|-|--------------|----------------|
| Pattern | `grep -q 'write: all'` | `grep -qE 'write-all$\|permissions:\s+write-all'` |
| Matches real syntax | No — never triggered | Yes — correct GitHub Actions syntax |

### Portability Fix (CWE-20) — RESOLVED

| | Prior | Current |
|-|-------|---------|
| Line count | `wc -l "$FINDINGS_FILE"` | `grep -c '' "$FINDINGS_FILE"` |
| macOS output | `"       3 filename"` (breaks arithmetic) | `"3"` (clean integer) |

---

## SBOM Coverage

The `generate-sbom.sh` script generates CycloneDX 1.4 SBOMs:

| Ecosystem | Detection File | JSON Construction | Status |
|-----------|---------------|-------------------|--------|
| npm / yarn / pnpm | package-lock.json, yarn.lock, pnpm-lock.yaml | `jq -n --arg` | SUPPORTED |
| Python (poetry/pipenv) | Pipfile, poetry.lock | `jq -n --arg` | SUPPORTED |
| Rust | Cargo.lock | `jq -n --arg` | SUPPORTED |
| Go | go.sum | `jq -n --arg` | SUPPORTED |
| Maven | pom.xml | N/A | NOT IMPLEMENTED |
| Gradle | build.gradle | N/A | NOT IMPLEMENTED |

---

## Secret Management

| Check | Status | Notes |
|-------|--------|-------|
| Hardcoded secrets in scripts | PASS | No credentials found in any script |
| Secrets in workflow env vars | PASS | No `env:` secret assignments in lint.yml |
| GITHUB_TOKEN scope | PASS | `contents: read` only |
| `.gitignore` lockfile exclusions | PASS | Lockfile entries removed (L1 prior fix) |
| Signed commits | PASS | GPG signing verified on recent commits |
| Wildcard secrets access | PASS | No `secrets.*` wildcards in workflows |

---

## Risk Matrix

| Risk | Likelihood | Impact | Residual Risk | Treatment |
|------|-----------|--------|---------------|-----------|
| Compromised action via tag re-point | LOW | HIGH | MITIGATED | SHA pinning applied |
| GITHUB_TOKEN privilege escalation | LOW | HIGH | MITIGATED | `permissions: contents: read` |
| JSON injection via crafted filenames | LOW | MEDIUM | MITIGATED | `jq --arg` applied |
| False-negative permissions detection | LOW | MEDIUM | MITIGATED | Regex corrected |
| Non-hermetic `pip install` in CI | MEDIUM | LOW | ACCEPTED | Lint-only; no artifacts shipped |
| Missing Maven/Gradle SBOM | LOW | LOW | ACCEPTED | Known gap, documented |
| Missing branch protection rules | LOW | MEDIUM | OPEN | Requires repo admin action |

---

## Framework Compliance

| Framework | Requirement | Prior | Current |
|-----------|-------------|-------|---------|
| SLSA v1.0 | L2 Build integrity | FAIL | PASS |
| NIST SP 800-218A | Secure build environment (PW.1.2) | FAIL | PASS |
| OWASP CI/CD Sec Top 10 | CICD-SEC-3: Dependency chain abuse | FAIL | PASS |
| OWASP CI/CD Sec Top 10 | CICD-SEC-6: Insufficient credential hygiene | FAIL | PASS |
| ISO 27001 A.15 | Supplier relationships | PARTIAL | PARTIAL |
| EU AI Act Art. 25 | Risk management | PASS | PASS |
