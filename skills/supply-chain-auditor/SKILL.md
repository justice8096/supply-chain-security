# Supply Chain Security Auditor Skill

**Author**: Justice
**Version**: 1.0.0
**Trigger Keywords**: supply chain, SBOM, dependency audit, are my dependencies safe, license check, SLSA, software bill of materials, check my package.json, vulnerability scan, is this library safe, dependency risk, container security, image scan, supply chain risk, software provenance

## Overview

The Supply Chain Security Auditor skill helps teams identify and mitigate supply chain security risks across five critical dimensions: dependency inventory and vulnerability analysis, CI/CD pipeline security, software bill of materials (SBOM) generation, SLSA compliance assessment, and runtime container security.

Findings map to compliance frameworks including NIST SP 800-218A, EU AI Act Article 25, OpenSSF Scorecard, CISA secure development controls, ISO 42001, ENISA 2025, and SLSA v1.0.

## Audit Capabilities

### 1. Dependency Analysis

Analyze all direct and transitive dependencies for security, maintenance, and legal risks.

**Scope**:
- Package manager detection (npm, yarn, pnpm, pip, poetry, cargo, go mod, maven, gradle)
- Direct vs transitive dependency inventory
- Version pinning analysis (exact vs floating ranges)
- Known vulnerability scanning against NVD/CVE databases
- License inventory and GPL contamination detection
- License compatibility matrix (MIT + AGPL = risk)
- Maintenance status: last update date, commit frequency, open issues/PRs count
- Bus factor assessment (contributor concentration)
- Typosquatting risk (similar package names in registries)
- Abandoned/deprecated package detection
- Supply chain poisoning patterns (sudden version changes, account compromise)

**Outputs**:
- Dependency tree with version constraints
- CVE list with CVSS scores and remediation status
- License compliance report
- Maintenance health dashboard

### 2. Build Pipeline Security (CI/CD)

Audit CI/CD configurations (GitHub Actions, GitLab CI, Jenkins) for common vulnerabilities.

**Scope**:
- Third-party action/plugin trust assessment
  - Pinned vs unpinned actions (`uses: user/action@ref` vs `uses: user/action`)
  - Official vs community actions
  - Action repository health (stars, last update, vulnerability history)
- Secret management audit
  - Hardcoded secrets detection (API keys, tokens in YAML)
  - Vault/OIDC adoption vs environment variables
  - Secret logging/exposure in build logs
- Build reproducibility assessment
  - Docker layer caching strategy
  - Deterministic dependency resolution
  - Build artifact versioning
- Permissions analysis
  - GITHUB_TOKEN scope (read-only vs write)
  - Container registry push permissions
  - Secrets access (wildcard * vs explicit refs)
- Artifact signing and provenance
  - Sigstore/cosign integration
  - SLSA provenance generation
  - Binary publication with signatures

**Supported Platforms**:
- GitHub Actions (.github/workflows/*.yml)
- GitLab CI (.gitlab-ci.yml)
- Jenkins (Jenkinsfile, pipeline configuration)

**Outputs**:
- Risk matrix (critical, high, medium, low)
- Remediation roadmap
- SLSA level baseline

### 3. Software Bill of Materials (SBOM)

Generate standardized component inventories for software transparency and vulnerability tracking.

**Formats**:
- **CycloneDX**: JSON/XML format for component and dependency metadata
  - Component type (library, framework, application, container, OS)
  - License SPDX identifier
  - Component version and purl (package URL)
  - Known vulnerabilities and VEX statements
- **SPDX**: Human-readable JSON/YAML format with license expressions
  - File-level license metadata
  - Creator and generated timestamp
  - Relationship graph (contains, depends_on)

**Features**:
- VEX (Vulnerability Exploitability eXchange) statements
  - Vulnerability status: affected, unaffected, unknown
  - Justification for unaffected status
  - Impact assessment (component exploitable in context?)
- Transitive dependency flattening
- License expression parsing (MIT OR Apache-2.0)
- Component metadata enrichment (source repository, download URL)

**Generation Methods**:
- package.json/package-lock.json -> npm-based SBOM
- requirements.txt/Poetry.lock -> Python SBOM
- Cargo.toml/Cargo.lock -> Rust SBOM
- go.mod/go.sum -> Go SBOM
- pom.xml/settings.xml -> Maven SBOM

### 4. SLSA Compliance Assessment

Determine current SLSA (Supply chain Levels for Software Artifacts) maturity and path to higher levels.

**SLSA Levels** (v1.0):
- **L0**: No requirements; baseline
- **L1**: Provenance available; version control; build recipe available
- **L2**: Provenance signed; no repository modification during build; build logs retained
- **L3**: Build script isolation; immutable version control; retention of source and build logs
- **L4**: Provenance hermetically sealed; all dependencies pinned; reproducible builds; cryptographic identity binding

**Assessment Includes**:
- Current level determination based on build practices
- Gap analysis: specific controls needed for next level
- Provenance verification (Sigstore OIDC integration)
- Build reproducibility testing
- Source isolation audit

### 5. Runtime Supply Chain

Audit container images and OCI artifacts for supply chain risks.

**Container Analysis**:
- Base image vulnerability scanning
- Base image age and end-of-life status
- Layer inspection (component inventory)
- Image signing verification (cosign, notation)
- Registry trust (Notary, content addressable)
- Known malware patterns (using YARA/Trivy)

**Scope**:
- Dockerfile and image build best practices
- Multi-stage build assessment
- Base image pinning (digest vs tag)
- Image tag semantics (:latest anti-pattern)
- Distroless/minimal image adoption

## Reference Materials

- **sbom-guide.md**: SBOM generation, CycloneDX vs SPDX comparison
- **slsa-framework.md**: SLSA v1.0 levels, requirements, implementation guide
- **supply-chain-threats.md**: MITRE ATLAS attacks, dependency confusion, typosquatting, account compromise
- **framework-mapping.md**: Findings mapped to NIST 800-218A, EU AI Act, OpenSSF, CISA, ISO 42001, ENISA, SLSA

## Framework Mapping

All findings are categorized by compliance framework:

**NIST SP 800-218A (SSDF)**:
- PO (Prepare Organization)
- PS (Protect Software)
- PO.1.1: Organization document governance
- PS.2.1: Vulnerable dependencies tracked
- PS.3.1: Build from known good source
- PS.3.2: Parameterized build with traceability

**EU AI Act Article 25**: Technical documentation, risk management, transparency logs

**OpenSSF Scorecard**: Security practices scoring (20 metrics)

**CISA Secure Software Development**: 8 critical controls for secure development

**ISO 42001**: AI management system, design controls, risk assessment

**ENISA 2025**: Supply chain risk assessment, vendor security, incident response

**SLSA v1.0**: Provenance, source integrity, build integrity, packaging integrity

## Typical Audit Workflow

1. **Intake**: Provide package manifest or GitHub/GitLab repository URL
2. **Detection**: Identify package manager, build system, container setup
3. **Analysis**: Run dependency, CI/CD, and container audits in parallel
4. **SBOM Generation**: Create CycloneDX SBOM with VEX statements
5. **Assessment**: Determine SLSA level, framework compliance gaps
6. **Report**: Executive summary, risk matrix, remediation roadmap, framework mapping
7. **Prioritization**: High/critical findings first, quick wins second

## Scripts

### generate-sbom.sh
Generates CycloneDX JSON SBOM from dependency files (package.json, requirements.txt, Cargo.toml, go.mod).

Usage: `./generate-sbom.sh <project-path> [output-file.json]`

### check-lockfiles.sh
Verifies lockfile presence and integrity, detects mismatches with manifest files.

Usage: `./check-lockfiles.sh <project-path>`

### audit-ci-config.sh
Parses GitHub Actions, GitLab CI, or Jenkinsfile for unpinned actions, hardcoded secrets, excessive permissions.

Usage: `./audit-ci-config.sh <project-path> [platform]`

### generate-report.py
Transforms audit findings JSON into markdown report with risk matrix, SLSA assessment, framework compliance table.

Usage: `python generate-report.py findings.json --output report.md`

## Common Findings

**Critical**:
- Hardcoded secrets in CI configuration
- Unpinned GitHub Actions (security risk)
- GPL dependency in proprietary/MIT project (license violation)
- Base image :latest tag in Dockerfile (reproducibility risk)
- No lockfile (non-deterministic builds)

**High**:
- Transitive dependency with known CVE (CVSS 7.0+)
- Build runs with excessive permissions (full token write access)
- Unmaintained dependencies (>1 year without updates)
- Missing SBOM/provenance

**Medium**:
- Floating version constraints (^1.0.0)
- No artifact signing
- Container image from untrusted registry
- Bus factor assessment (single maintainer)

**Low**:
- Non-standard license (less common)
- Older base image (but actively maintained)
- Missing VEX statements

## Output Formats

- **Executive Summary**: Risk overview, top 3 findings, SLSA level, compliance status
- **Risk Matrix**: Severity vs likelihood, affected components
- **SBOM**: CycloneDX JSON with VEX statements
- **Roadmap**: Prioritized remediations with estimated effort
- **Framework Mapping Table**: Finding -> NIST 800-218A + EU AI Act + OpenSSF + CISA + ISO 42001 + ENISA
- **SLSA Path**: Current level + gap analysis to next level

## Limitations

- Accuracy depends on publicly available vulnerability databases (NVD, GitHub Advisory)
- Transitive dependency tracking limited to available lockfiles
- SLSA assessment is baseline; detailed provenance verification requires artifact access
- Container scanning requires image registry access or local image availability
- Typosquatting detection limited to registry name similarity; manual review recommended

## Privacy & Security

- All analysis performed locally on provided files
- No sensitive data transmitted to external services unless explicitly configured
- Vulnerability data sourced from public NVD/CVE databases
- No dependency on proprietary vulnerability feeds (configurable)

## Future Enhancements

- Automated remediation suggestions with PR generation
- Real-time monitoring and periodic rescans
- Integration with Sigstore PKI for provenance verification
- SLSA provenance statement validation
- Custom policy as code (Rego/CEL-based)
- Supply chain risk heat mapping across organizations
