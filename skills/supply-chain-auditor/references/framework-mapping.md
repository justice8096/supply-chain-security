# Framework Compliance Mapping

This document maps supply chain audit findings to regulatory frameworks and industry standards used in security governance.

## NIST SP 800-218A: Secure Software Development Framework (SSDF)

**NIST SSDF** defines 16 secure practices across 4 domains: Prepare Organization (PO), Protect Software (PS), Produce Well-Formed Software (PO), and Respond to Vulnerabilities (RV).

### PO: Prepare Organization

**PO.1.1 - Org Governance**: Establish policies for secure development
- Audit Finding: Missing documented secure development policy
- Mapping: Check for policies covering: secure coding, code review requirements, dependency management, incident response
- Score: 0 if no policy, 1 if incomplete, 2 if comprehensive

**PO.1.2 - Org Security Training**: Developers trained in secure practices
- Audit Finding: No evidence of security training program
- Mapping: Verify training covers: secure coding, supply chain risks, credential management
- Score: Assessed through interview or training records

**PO.2.1 - Risk Management**: Identify and assess risk from external dependencies
- Audit Finding: No dependency risk assessment
- Mapping: Supply chain audit checks CVE database, maintenance status, license compatibility
- Score: 0 if no process, 1 if ad-hoc, 2 if systematic

**PO.2.2 - Risk Management Tools**: Use tools to identify risks
- Audit Finding: No automated vulnerability scanning
- Mapping: Implement: npm audit, Snyk, WhiteSource, Trivy for containers
- Score: 0 if manual, 1 if partial automation, 2 if comprehensive

**PO.3.1 - Secure Dev Environment**: Configure development environment securely
- Audit Finding: Developers with sudo/admin access, no secret segregation
- Mapping: Least privilege, MFA, secret management separation
- Score: 0 if none, 1 if partial, 2 if enforced

**PO.3.2 - Communication Security**: Protect communication channels
- Audit Finding: Unencrypted artifact repositories or insecure registries
- Mapping: Enforce HTTPS, GPG signing, repository authentication
- Score: 0 if unencrypted, 1 if encrypted, 2 if signed

### PS: Protect Software

**PS.1.1 - Code Review**: All source code reviewed before integration
- Audit Finding: No code review enforcement, direct commits to main
- Mapping: GitHub/GitLab branch protection, PR approval requirements
- Score: 0 if no review, 1 if inconsistent, 2 if all commits reviewed

**PS.1.2 - Static Analysis**: Code analysis for defects/vulnerabilities
- Audit Finding: No SAST/linting tools
- Mapping: ESLint, SonarQube, Bandit (Python), clippy (Rust)
- Score: 0 if none, 1 if basic, 2 if comprehensive with CI/CD

**PS.2.1 - Vulnerable Dependency Management**: Identify and patch known vulnerabilities
- Audit Finding: High CVSS vulnerabilities unpatched, no tracking mechanism
- Mapping: Maintain CVE inventory, track remediation timeline, automate patching
- Score: 0 if no process, 1 if reactive, 2 if proactive

**PS.2.2 - Update/Patch**: Apply updates/patches timely
- Audit Finding: Outdated dependencies (>6 months old)
- Mapping: Dependency upgrade strategy, automated patching for critical CVEs
- Score: Baseline 0-3 months, 1-6 months, 2 for continuous

**PS.3.1 - Integrity of Build**: Build from known good source with build recipe
- Audit Finding: Build not tied to specific commit, no Dockerfile/Makefile
- Mapping: Requirement for version control + build recipe in repo
- Score: 0 if ad-hoc, 1 if build recipe present, 2 if tied to VCS commit

**PS.3.2 - Build Process Integrity**: Build process logged, reproducible, and secured
- Audit Finding: No build logs, unsigned artifacts, unpinned GitHub Actions
- Mapping: Log retention, artifact signing (cosign), action pinning
- Score: 0 if none, 1 if partial, 2 if all implemented

**PS.3.3 - Secure Build Environment**: Build process isolated from untrusted code
- Audit Finding: Build runs on shared machine with user code access
- Mapping: Containerized/ephemeral build, no ambient state, isolated network
- Score: 0 if shared, 1 if containerized, 2 if hermetic

**PS.4.1 - Artifact Identification**: Artifacts uniquely identified and authenticated
- Audit Finding: Artifacts referenced by tag (:latest), not digest
- Mapping: Require artifact hash/digest, cryptographic signatures
- Score: 0 if tags, 1 if digests, 2 if signed

### RV: Respond to Vulnerabilities

**RV.1.1 - Coordinated Disclosure**: Establish process for vulnerability disclosure
- Audit Finding: No security.txt or vulnerability disclosure policy
- Mapping: Document responsible disclosure process, incident response plan
- Score: 0 if none, 1 if informal, 2 if documented

**RV.1.2 - Vulnerability Response**: Respond to vulnerabilities in timely manner
- Audit Finding: No SLA for vulnerability remediation
- Mapping: Critical CVEs patched <30 days, high <90 days
- Score: Assessed through incident history

**RV.2.1 - Tracking Vulnerabilities**: Maintain vulnerability tracking system
- Audit Finding: CVEs discovered but not tracked in issue system
- Mapping: Use GitHub Issues, Jira, or dedicated tracker
- Score: 0 if none, 1 if ad-hoc, 2 if systematic

**RV.2.2 - Incident Management**: Create incident response plan
- Audit Finding: No documented incident response procedure
- Mapping: IR playbook including: detection, analysis, containment, recovery
- Score: 0 if none, 1 if basic, 2 if comprehensive

## EU AI Act Article 25: Technical Documentation & Governance

**Applies to**: AI systems as defined by EU AI Act (risk-based approach)

**Key Requirements**:
- Technical documentation of AI system design, data, model training
- SBOM and bill of materials for data
- Conformity assessment procedures
- Risk management system
- Quality assurance procedures

### Audit Mapping

| Finding | EU AI Act 25 Relevance | Mitigation |
|---------|----------------------|-----------|
| No SBOM | Required technical documentation | Generate SBOM (CycloneDX) |
| Unvetted dependencies | Quality assurance gap | Vulnerability scan, license audit |
| GPL in proprietary | License compliance issue | Identify and replace |
| Outdated base image | Risk management gap | Update to current with security patches |
| No artifact signing | Integrity/authenticity gap | Implement cosign/Sigstore signing |
| Build secrets in logs | Security governance gap | Secret management, log masking |

**AI-Specific Risks** (if applicable):
- Training data transparency: Document data sources, provenance
- Model integrity: Verify model weights from trusted sources
- Supplier assessment: Evaluate AI service providers (OpenAI, Google Cloud AI)

## OpenSSF Scorecard

**OpenSSF Scorecard** evaluates open source project security across 17 dimensions, each 0-10.

### Mapping to Supply Chain Audit

**1. Branch Protection** (GitHub only)
- Audit Check: Branch protection rules enforced
- Finding: No PR review requirement
- Score Impact: Reduce by 2-3 points

**2. CII-Best-Practices Badge**
- Audit Check: Project follows CII best practices
- Finding: No CII badge or practices
- Score Impact: Reduce by 1-2 points

**3. Code Review**
- Audit Check: Code review enforced
- Finding: Commits bypass review
- Score Impact: Critical; reduce by 3-4 points

**4. Dangerous Workflow**
- Audit Check: GitHub Actions don't request secrets
- Finding: Workflow uses `pull_request_target` without review
- Score Impact: Reduce by 3-5 points

**5. Dependency Update Tool**
- Audit Check: Dependabot or Renovate enabled
- Finding: Manual dependency updates only
- Score Impact: Reduce by 2 points

**6. Security Policy**
- Audit Check: SECURITY.md file exists
- Finding: No security policy
- Score Impact: Reduce by 2 points

**7. Signed Releases**
- Audit Check: Release artifacts signed
- Finding: Releases not signed
- Score Impact: Reduce by 2-3 points

**8. Token Permissions**
- Audit Check: GitHub Actions use minimal permissions
- Finding: All workflows have full `write` permissions
- Score Impact: Reduce by 2-3 points

**9. Vulnerability Disclosure**
- Audit Check: Security advisory process documented
- Finding: No responsible disclosure process
- Score Impact: Reduce by 1-2 points

### Overall Score Formula
- Scorecard = (sum of 17 dimensions / 17) * 10
- Target: 7.0+ for secure open source
- Critical: No dimension should be 0 (critical gap)

## CISA Secure Software Development (8 Practices)

**CISA emphasizes** 8 critical practices for federal software acquisition.

### Mapping

| CISA Practice | Audit Dimension | Finding Type |
|---------------|-----------------|--------------|
| 1. Use version control | VCS (Git) in place | No version control = Critical |
| 2. Protect build system | Secure CI/CD | Unpinned actions, exposed secrets = Critical |
| 3. Provide SBOM | Component transparency | Missing SBOM = High |
| 4. Sign software artifacts | Integrity assurance | Unsigned binaries/images = High |
| 5. Binary analysis | Artifact verification | No scanning = Medium |
| 6. Security practices scoring | Code review, testing | OpenSSF Scorecard integration |
| 7. Incident response plan | Vulnerability management | Missing plan = High |
| 8. Personnel security | Access controls | No MFA on npm account = High |

## ISO 42001: AI Management System

**Applies to**: Organizations developing, deploying, or using AI systems

**Key Clauses**:
- 4.2: Understanding context (supply chain risks for AI)
- 5.1: Leadership commitment to secure AI
- 6.1: Risk assessment (supply chain attacks on AI models)
- 8.1: Operational planning (secure AI deployment)
- 8.2: Change management (versioning AI models)

### Audit Relevance

| ISO Clause | Supply Chain Aspect | Audit Check |
|------------|-------------------|-------------|
| 6.1 Risk Assessment | Dependency vulnerabilities | CVE scan, license audit |
| 8.2 Change Management | Model version control | Model card, artifact versioning |
| 8.3 Competence | Security training | Developer security training |
| 8.4 Communication | Incident reporting | IR process documentation |
| 8.6 Supplier Management | Third-party risk | Vendor security assessment |

## ENISA 2025: Strengthen Supply Chain Security

**ENISA 2025 Recommendations**:
1. Enhance software supply chain security
2. Increase transparency and traceability
3. Strengthen vendor security
4. Implement security testing
5. Develop incident response capabilities

### Audit Coverage

- **Transparency**: SBOM generation, VEX statements
- **Traceability**: Build provenance, artifact signatures, commit history
- **Testing**: Automated vulnerability scanning, security testing in CI/CD
- **Vendor Assessment**: Dependency health, maintainer track record
- **Incident Response**: Coordinated disclosure, remediation SLAs

## SLSA v1.0: Supply Chain Levels for Software Artifacts

See `slsa-framework.md` for detailed SLSA mapping.

### Quick Reference

| SLSA Level | Framework Alignment | Audit Score |
|-----------|-------------------|-------------|
| L0 | Baseline, no requirements | <3/10 |
| L1 | Provenance available, VCS, recipe | 3-5/10 |
| L2 | Signed provenance, immutable source | 5-7/10 |
| L3 | Build isolation, pinned deps | 7-8/10 |
| L4 | Hermetic, reproducible, key separation | 8-10/10 |

## Compliance Scoring Model

### Overall Score Calculation

```
Supply Chain Security Score =
  (Dependency Management: 0-25 points) +
  (Build Pipeline: 0-25 points) +
  (SBOM & Transparency: 0-15 points) +
  (SLSA Compliance: 0-20 points) +
  (Incident Response: 0-15 points)

Total: 0-100 points
Target: 70+ for production ready
```

### Mapping to Risk Level

| Score | Risk Level | Action |
|-------|-----------|--------|
| 80-100 | Low | Monitor continuously |
| 60-79 | Medium | Address high-severity findings in 90 days |
| 40-59 | High | Address critical findings in 30 days |
| <40 | Critical | Pause deployments, remediate immediately |

## Example Audit Report Output

```
Finding: GPL-3.0 dependency in MIT project (license/express)
NIST 800-218A: PS.1.2 (Static Analysis) - License compatibility
EU AI Act 25: Technical documentation gap (unlicensed AI use)
OpenSSF: License compliance aspect (not scored)
CISA: Practice 3 (SBOM accuracy) - Missing license data
SLSA: Documentation gap
Severity: High
Recommended Action: Replace with MIT/Apache-2.0 alternative or add exception
Timeline: 60 days
```

---

**References**:
- NIST SP 800-218A: https://csrc.nist.gov/publications/detail/sp/800-218
- EU AI Act: https://eur-lex.europa.eu/eli/reg/2023/1230
- OpenSSF Scorecard: https://securityscorecards.dev
- CISA: https://www.cisa.gov/secure-software-development-framework
- ISO 42001: https://www.iso.org/standard/81230.html
- ENISA 2025: https://www.enisa.europa.eu
- SLSA: https://slsa.dev
