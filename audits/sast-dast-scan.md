# SAST/DAST Scan Report
**Project**: supply-chain-security (Supply Chain Security Auditor Skill)
**Date**: 2026-03-29
**Commit**: 471a381 — style: fix flake8 violations
**Branch**: master
**Audit Type**: POST-FIX Re-audit (verifying HIGH resolution)
**Prior Audit**: CONDITIONAL PASS — 2 HIGH, 4 MEDIUM, 2 LOW, 1 INFO

---

## Executive Summary

All 2 HIGH and all 4 MEDIUM findings from the prior audit have been successfully remediated. The codebase is now clean of critical and high-severity vulnerabilities. Two low-severity and one informational finding remain as accepted residual risk.

**Overall Result: PASS**

### Before / After Delta

| Severity | Prior | Current | Delta |
|----------|-------|---------|-------|
| CRITICAL | 0 | 0 | — |
| HIGH | 2 | 0 | -2 RESOLVED |
| MEDIUM | 4 | 0 | -4 RESOLVED |
| LOW | 2 | 2 | — (accepted) |
| INFO | 1 | 1 | — (known gap) |
| **Total** | **9** | **3** | **-6** |

---

## Resolved Findings

### [RESOLVED] H1 — Unpinned GitHub Actions (CWE-829)
**File**: `.github/workflows/lint.yml`
**Prior State**: All three actions were pinned only to mutable version tags (`@v4`, `@2.0.0`, `@v5`), allowing tag re-pointing to deliver compromised code into the pipeline without notice.
**Fix Applied** (commit `10812c3`): All actions are now SHA-pinned to immutable commit hashes:
- `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4`
- `ludeeus/action-shellcheck@00cae500b08a931fb5698e11e79bfbd38e612a38 # 2.0.0`
- `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5`

**Verification**: No `uses: .*@v[0-9]` references remain in any workflow file.

---

### [RESOLVED] H2 — Missing Least-Privilege Permissions (CWE-269)
**File**: `.github/workflows/lint.yml`
**Prior State**: No `permissions` block present; GITHUB_TOKEN defaulted to broad read/write access across all repository scopes, enabling potential privilege escalation if a step was compromised.
**Fix Applied** (commit `10812c3`):
```yaml
permissions:
  contents: read
```
The token is now restricted to the minimum scope required for checkout. All other capabilities are implicitly denied.

**Verification**: `permissions: contents: read` confirmed present at workflow top level.

---

### [RESOLVED] M1 — Command Injection via Heredoc JSON in SBOM Generator (CWE-78)
**File**: `skills/supply-chain-auditor/scripts/generate-sbom.sh`
**Prior State**: `generate_python_sbom`, `generate_rust_sbom`, and `generate_go_sbom` constructed JSON output via shell heredoc with unquoted variable interpolation (`${name}`, `${version}`). A crafted filename or metadata value containing shell metacharacters or JSON special characters could corrupt the SBOM output or inject commands.
**Fix Applied** (commit `10812c3`): All three generators now use `jq -n --arg name "$name" --arg ts "$timestamp"` (and `--arg version` where applicable) to pass values through jq's safe escaping layer before writing JSON.

**Verification**: `jq -n` and `--arg` patterns confirmed in all three generators (lines ~121–135, ~155–167, ~183–196).

---

### [RESOLVED] M2 — Unescaped Workflow Name in JSON Finding Records (CWE-78)
**File**: `skills/supply-chain-auditor/scripts/audit-ci-config.sh`
**Prior State**: All JSON finding records in `audit_github_actions()` were written with bare `echo '{"severity": "...", "file": "'"$workflow_name"'"}' >> "$FINDINGS_FILE"`. A workflow filename containing double-quotes, backslashes, or JSON special characters would produce malformed JSON or enable injection.
**Fix Applied** (commit `10812c3`): All finding writes now use `jq -n --arg file "$workflow_name" '{...}'` ensuring proper JSON escaping regardless of the filename value.

**Verification**: No bare `echo '{"severity"...}' >> "$FINDINGS_FILE"` patterns remain in the GitHub Actions auditor loop.

---

### [RESOLVED] M3 — Wrong Permissions Detection Regex (CWE-697)
**File**: `skills/supply-chain-auditor/scripts/audit-ci-config.sh`
**Prior State**: Excessive-permissions check used the pattern `write: all` which never matches GitHub Actions' actual syntax. Real `write-all` permissions grants were silently missed, creating a false sense of security.
**Fix Applied** (commit `10812c3`): Pattern corrected to:
```bash
grep -qE 'write-all$|permissions:\s+write-all'
```
This matches both the inline (`permissions: write-all`) and block (`permissions:\n  ...\nwrite-all`) forms.

**Verification**: Updated grep pattern confirmed in `audit_github_actions()`.

---

### [RESOLVED] M4 — `wc -l` Whitespace Portability Bug (CWE-20)
**File**: `skills/supply-chain-auditor/scripts/audit-ci-config.sh`
**Prior State**: `wc -l "$FINDINGS_FILE"` outputs `"       3 filename"` on macOS (leading whitespace + filename), causing `[ "$total_findings" -eq 0 ]` to fail with a bash arithmetic syntax error. On macOS the findings count was effectively unchecked, masking all findings silently.
**Fix Applied** (commit `10812c3`): Replaced with `grep -c '' "$FINDINGS_FILE"` which returns a plain integer on all POSIX platforms (Linux, macOS, BSD).

**Verification**: `grep -c '' "$FINDINGS_FILE"` confirmed in `generate_summary()`.

---

### [RESOLVED] L1 (Prior Audit) — Lockfile Entries in .gitignore (CWE-494)
**File**: `.gitignore`
**Prior State**: Lockfile patterns were present in `.gitignore`, preventing `package-lock.json` and similar files from being committed. This undermined reproducible builds and SBOM integrity.
**Fix Applied**: Lockfile entries removed from `.gitignore`.

**Verification**: Confirmed resolved per commit history.

---

### [RESOLVED] Code Quality — flake8 Violations in generate-report.py
**File**: `skills/supply-chain-auditor/scripts/generate-report.py`
**Fix Applied** (commit `471a381`): Unused import removed, blank line formatting corrected, spurious f-strings without interpolation converted to plain strings. CI python-lint step now passes cleanly.

---

## Active Findings (Accepted Residual Risk)

### L1 — Diagnostic Output to stdout (CWE-532)
**Severity**: LOW
**File**: `skills/supply-chain-auditor/scripts/generate-sbom.sh`
**Description**: Project path and package manager name are echoed to stdout during execution. In CI pipelines these messages appear in build logs. No credentials or secrets are involved. Accepted as operational verbosity.
**Remediation**: Add `--quiet` flag to suppress non-essential output. Low priority.

---

### L2 — Bare Echo JSON in GitLab/Jenkins/Docker Auditors (CWE-78)
**Severity**: LOW
**File**: `skills/supply-chain-auditor/scripts/audit-ci-config.sh` (lines ~119, ~130, ~155, ~177, ~183)
**Description**: The GitLab CI, Jenkins, and Docker auditor branches still use `echo '{"severity": ...}'` for JSON findings. These branches do not interpolate user-controlled filenames (paths are hardcoded strings), so actual injection risk is negligible. However, the inconsistency with the GitHub Actions auditor is a maintenance concern.
**Remediation**: Migrate to `jq -n` for consistency. Low priority.

---

### INFO-1 — Maven/Gradle SBOM Not Implemented
**Severity**: INFO
**File**: `skills/supply-chain-auditor/scripts/generate-sbom.sh` (line ~222)
**Description**: Maven/Gradle projects cause the script to exit with status 1. This is a documented known gap (`echo "Maven/Gradle support coming soon"`).
**Remediation**: Implement in a future iteration.

---

## DAST Assessment

This project is a CLI/script toolset with no HTTP service or API surface. Standard DAST checks (HTTP headers, CORS, TLS, cookie flags, authentication flows) are not applicable. The CI pipeline (lint.yml) was assessed above for workflow injection vectors; all vectors are now mitigated.

---

## Summary Table

| ID | Severity | CWE | Status | File |
|----|----------|-----|--------|------|
| H1 | HIGH | CWE-829 | RESOLVED | lint.yml |
| H2 | HIGH | CWE-269 | RESOLVED | lint.yml |
| M1 | MEDIUM | CWE-78 | RESOLVED | generate-sbom.sh |
| M2 | MEDIUM | CWE-78 | RESOLVED | audit-ci-config.sh |
| M3 | MEDIUM | CWE-697 | RESOLVED | audit-ci-config.sh |
| M4 | MEDIUM | CWE-20 | RESOLVED | audit-ci-config.sh |
| L1 | LOW | CWE-532 | ACCEPTED | generate-sbom.sh |
| L2 | LOW | CWE-78 | ACCEPTED | audit-ci-config.sh |
| I1 | INFO | N/A | KNOWN GAP | generate-sbom.sh |
