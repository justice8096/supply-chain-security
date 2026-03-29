---
name: supply-chain-security
description: >
  This skill should be used when the user asks to audit dependencies for vulnerabilities,
  check if their dependencies are safe, generate a software bill of materials (SBOM),
  assess SLSA compliance, audit CI/CD pipeline configuration for supply chain risks,
  scan container images for supply chain threats, check license compliance, detect
  hardcoded secrets in CI configuration, or map findings to NIST SP 800-218A, EU AI Act,
  OpenSSF Scorecard, CISA secure development controls, ISO 42001, ENISA 2025, or SLSA v1.0.
  Trigger phrases include: "supply chain", "SBOM", "dependency audit", "are my dependencies
  safe", "license check", "SLSA", "software bill of materials", "check my package.json",
  "vulnerability scan", "is this library safe", "dependency risk", "container security",
  "image scan", "supply chain risk", "software provenance".
---

# Supply Chain Security Auditor

Audit software projects across five dimensions: dependency analysis, CI/CD pipeline security,
SBOM generation, SLSA compliance assessment, and container/runtime supply chain analysis.
All findings map to NIST SP 800-218A, EU AI Act Article 25, OpenSSF Scorecard, CISA secure
development controls, ISO 42001, ENISA 2025, and SLSA v1.0.

---

## Audit Workflow

Execute audits in this order to produce a complete supply chain security assessment:

1. **Intake** — Accept a package manifest, lockfile, CI config, Dockerfile, or repository URL.
2. **Detection** — Identify package manager, build system, and container setup.
3. **Parallel Analysis** — Run dependency, CI/CD, and container audits concurrently.
4. **SBOM Generation** — Produce CycloneDX 1.4 or SPDX document with VEX statements.
5. **SLSA Assessment** — Determine current level (L0–L4) and enumerate gaps.
6. **Report** — Deliver executive summary, risk matrix, remediation roadmap, and framework table.
7. **Prioritization** — Address critical/high findings first, then quick wins.

---

## Dimension 1: Dependency Analysis

### What to analyze

- Detect package manager from manifest files: `package.json` / lockfile (npm, yarn, pnpm),
  `requirements.txt` / `poetry.lock` (pip/poetry), `Cargo.toml` / `Cargo.lock` (cargo),
  `go.mod` / `go.sum` (go mod), `pom.xml` (maven), `build.gradle` (gradle).
- Build the full dependency tree distinguishing direct vs transitive dependencies.
- Flag floating version constraints (`^`, `~`, `>=`) versus exact pins.
- Check each dependency against NVD/CVE databases; record CVSS scores.
- Inventory SPDX license identifiers; flag GPL contamination in non-GPL projects;
  evaluate license compatibility (e.g., MIT + AGPL = risk).
- Assess maintenance health: last release date, commit frequency, open issue count,
  contributor count (bus factor).
- Detect typosquatting risk via name-similarity matching against known registry packages.
- Identify abandoned or deprecated packages and account-compromise patterns
  (sudden unexpected version bumps, new maintainer with no history).

### Script

Use `scripts/check-lockfiles.sh <project-path>` to verify lockfile presence and integrity
and detect manifest/lockfile mismatches.

### Outputs

| Output | Contents |
|---|---|
| Dependency tree | Version constraints, direct vs transitive |
| CVE list | CVSS score, affected versions, remediation status |
| License report | SPDX identifiers, compatibility issues |
| Maintenance dashboard | Last update, bus factor, abandonment signals |

### Common critical findings

- No lockfile present → non-deterministic builds.
- GPL dependency in a proprietary or MIT-licensed project → potential license violation.
- Transitive dependency with known CVE (CVSS ≥ 7.0).
- Unmaintained dependency (>1 year without release).

---

## Dimension 2: CI/CD Pipeline Security

### What to analyze

**Third-party action/plugin trust:**
- Flag actions pinned to a mutable ref (`uses: org/action@main`) versus an immutable
  commit SHA (`uses: org/action@abc1234`).
- Assess official vs community actions; check action repository health.

**Secret management:**
- Detect hardcoded secrets (API keys, tokens, passwords) in YAML pipeline configs.
- Evaluate Vault/OIDC adoption versus plain environment variables.
- Check for secret values echoed in build log steps.

**Permissions:**
- Evaluate `GITHUB_TOKEN` scope; flag write-all or missing `permissions:` blocks.
- Check container registry push permissions and wildcard secret access.

**Build reproducibility:**
- Assess Docker layer caching strategy, deterministic dependency resolution,
  and artifact versioning.

**Artifact signing and provenance:**
- Check for Sigstore/cosign integration and SLSA provenance generation.

### Script

Use `scripts/audit-ci-config.sh <project-path> [platform]` where platform is one of
`github`, `gitlab`, or `jenkins`. The script parses:
- GitHub Actions: `.github/workflows/*.yml`
- GitLab CI: `.gitlab-ci.yml`
- Jenkins: `Jenkinsfile`

### Outputs

- Risk matrix (critical / high / medium / low) per finding.
- Remediation roadmap sorted by severity.
- SLSA level baseline derived from pipeline practices.

---

## Dimension 3: SBOM Generation

Generate a standardized component inventory for vulnerability tracking and software transparency.

### Formats

**CycloneDX 1.4** (JSON or XML):
- Component type: library, framework, application, container, OS.
- License SPDX identifier.
- Component version and purl (package URL).
- Known vulnerabilities and VEX statements.

**SPDX** (JSON or YAML):
- File-level license metadata.
- Creator and generated timestamp.
- Relationship graph: `CONTAINS`, `DEPENDS_ON`.

### VEX statements

For each known vulnerability, record:
- Status: `affected` / `not_affected` / `under_investigation`.
- Justification for `not_affected` (e.g., `vulnerable_code_not_in_execute_path`).
- Impact assessment: is the vulnerable code path reachable in this deployment?

### Script

Use `scripts/generate-sbom.sh <project-path> [output-file.json]` to produce a
CycloneDX JSON SBOM from:

| Manifest | Ecosystem |
|---|---|
| `package.json` / `package-lock.json` | npm |
| `requirements.txt` / `poetry.lock` | Python |
| `Cargo.toml` / `Cargo.lock` | Rust |
| `go.mod` / `go.sum` | Go |
| `pom.xml` / `settings.xml` | Maven |

See `references/sbom-guide.md` for full format details and CycloneDX vs SPDX comparison.

---

## Dimension 4: SLSA Compliance Assessment

Determine the current SLSA v1.0 maturity level and produce a gap analysis.

### Level definitions

| Level | Requirements |
|---|---|
| L0 | No requirements; baseline (unevaluated) |
| L1 | Provenance available; version control; build recipe recorded |
| L2 | Provenance signed; no repository modification during build; build logs retained |
| L3 | Build script isolation; immutable version control; source and build log retention |
| L4 | Hermetically sealed provenance; all dependencies pinned; reproducible builds; cryptographic identity binding |

### Assessment steps

1. Determine the current level from observed build practices.
2. Enumerate gaps: list the specific controls required to reach the next level.
3. Verify Sigstore OIDC integration for provenance signing.
4. Test build reproducibility where feasible.
5. Audit source isolation (no modification of source during build).

See `references/slsa-framework.md` for detailed requirements per level and an
implementation guide.

---

## Dimension 5: Container and Runtime Supply Chain

### What to analyze

**Base image:**
- Scan for known CVEs in the base image layers.
- Check base image age and end-of-life status.
- Flag `:latest` tag anti-pattern; require digest-pinned references.
- Recommend distroless or minimal base images.

**Layer inspection:**
- Inventory components per layer; detect unexpected binaries or package additions.

**Image signing:**
- Verify cosign or notation signatures.
- Assess Notary v2 / content-addressable registry configuration.

**Dockerfile best practices:**
- Multi-stage build adoption.
- Non-root user enforcement.
- `COPY --chown` vs post-copy `chmod` patterns.

---

## Report Generation

Use `scripts/generate-report.py findings.json --output report.md` to transform a
structured findings JSON file into a complete markdown report containing:

- **Executive summary**: risk overview, top 3 findings, SLSA level, compliance status.
- **Risk matrix**: severity × likelihood grid with affected components.
- **SBOM**: CycloneDX JSON with VEX statements.
- **Remediation roadmap**: prioritized actions with estimated effort.
- **Framework mapping table**: finding → NIST 800-218A + EU AI Act + OpenSSF + CISA +
  ISO 42001 + ENISA control identifiers.
- **SLSA path**: current level + specific gaps to the next level.

---

## Framework Mapping Summary

All findings are tagged to one or more of the following controls.
See `references/framework-mapping.md` for the full mapping table.

| Framework | Key Controls |
|---|---|
| NIST SP 800-218A (SSDF) | PO.1.1, PS.2.1, PS.3.1, PS.3.2 |
| EU AI Act Article 25 | Technical documentation, risk management, transparency logs |
| OpenSSF Scorecard | 20 security practice metrics |
| CISA Secure Software Development | 8 critical controls |
| ISO 42001 | Design controls, risk assessment, AI management system |
| ENISA 2025 | Supply chain risk, vendor security, incident response |
| SLSA v1.0 | Provenance, source integrity, build integrity, packaging integrity |

---

## Reference Files

| File | Contents |
|---|---|
| `references/sbom-guide.md` | SBOM generation guide; CycloneDX vs SPDX comparison; VEX statement authoring |
| `references/slsa-framework.md` | SLSA v1.0 level requirements; implementation guide; provenance verification |
| `references/supply-chain-threats.md` | MITRE ATT&CK attack patterns; dependency confusion; typosquatting; account compromise |
| `references/framework-mapping.md` | Finding-to-control mapping across all six compliance frameworks |

---

## Known Limitations

- CVE accuracy depends on publicly available NVD and GitHub Advisory databases.
- Transitive dependency tracking requires a lockfile; without one, analysis is partial.
- SLSA assessment is a baseline; full provenance verification requires access to the
  signed provenance artifact (see `references/slsa-framework.md`).
- Container scanning requires local image availability or authenticated registry access.
- Typosquatting detection uses name-similarity only; manual review is recommended for
  high-risk packages.
- No sensitive project data is transmitted to external services unless explicitly configured.
