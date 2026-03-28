# Supply Chain Threats & Attack Patterns

## MITRE ATLAS Framework

MITRE ATT&CK for Language Models (ATLAS) and ATT&CK for Enterprise document supply chain attack techniques. This document maps known threats to supply chain security audit dimensions.

## Dependency-Based Attacks

### Typosquatting
**Attack**: Attacker registers package names similar to popular libraries
- `express` vs `expres`, `lodash` vs `lodas`
- Exploits typos in `npm install lodas`
- High severity due to ease and broad exposure

**Detection**:
- Perform Levenshtein distance check on dependency names
- Compare against top 1000 packages by download count
- Flag packages with <1000 weekly downloads + similar names

**Mitigation**:
- Strict dependency pinning and integrity validation
- Use `npm audit` and lockfile verification
- Private registry/proxy (Verdaccio) to whitelist approved packages

### Dependency Confusion
**Attack**: Attacker publishes malicious version on public registry with same name as private package
- Private package: `@acme/logging` (internal)
- Public package: `logging` (attacker)
- If version numbers align, public package installed instead

**Attack Flow**:
1. Reconnaissance: Identify private package names (error logs, npm errors)
2. Registration: Publish package to public registry with same or higher version
3. Installation: Developer runs `npm install` without scoped package
4. Execution: Malicious code runs in build or application

**Example**: SolarWinds-like attack but targeting dependencies

**Detection**:
- Audit package.json for inconsistent scoping (@org/name vs bare names)
- Check if any bare-named deps have corresponding public packages
- Version mismatch between lockfile and registry

**Mitigation**:
- Use scoped packages for all internal deps (@org/name)
- Configure .npmrc with registry priority: private > public
- Enforce npm audit in CI with fail on medium+ severity

### Supply Chain Poisoning (Account Takeover)
**Attack**: Attacker gains access to legitimate maintainer account, publishes malicious version
- Targets maintenance-heavy or abandoned packages
- Often single-maintainer (high bus factor)
- Example: `ua-parser-js`, `rest-client` incidents

**Attack Flow**:
1. Target selection: Popular package with low maintenance burden
2. Account compromise: Phishing, password reuse, 2FA bypass
3. Trojanization: Inject backdoor, exfil data, or install miners
4. Silent update: Publish new version (0.0.1 or normal bump)
5. Scale: Reaches millions via transitive deps

**Detection**:
- Monitor for unusual publishing patterns (frequency, timing)
- Track maintainer activity (GitHub commits vs npm publishes)
- Version release spike (multiple releases in short window)
- Check for unusual dependencies added in recent versions

**Mitigation**:
- Enforce 2FA on all npm accounts
- Use more maintainers to reduce single-point failure
- Require code review for significant changes
- Hash verification: `npm install --save-exact` + lockfile
- Use Sigstore-signed packages when available

### Abandoned/Unmaintained Packages
**Attack**: Attacker takes over abandoned package due to inactive maintainer
- Package unchanged for 2+ years
- Original maintainer ignores pull requests
- Low visibility, low maintenance burden

**Example**: `lodash` variants (lodash-es, lodash-es-new), old security fixes ignored

**Detection**:
- Track last publication date
- Monitor issue resolution time (mean time to response)
- Check open issues/PRs and age
- Calculate bus factor: commits from single developer / total commits

**Mitigation**:
- Identify replacement packages with active maintenance
- Fork and maintain locally if critical
- Request package maintenance hand-off on npm

## Build Pipeline Attacks

### Compromised Build System
**Attack**: Attacker gains access to CI/CD infrastructure, injects malware into artifacts
- Targets GitHub Actions, GitLab CI, Jenkins deployments
- Often via leaked credentials, unpatched systems
- Affects all artifacts built on compromised system

**Attack Flow**:
1. Access: Compromised credentials, leaked API key, unpatched CI system
2. Persistence: Add backdoor to build script, inject secrets accessor
3. Artifact pollution: Insert malware into compiled binaries
4. Distribution: Malicious artifacts deployed to customers

**Real Example**: CCleaner supply chain attack (2017)

**Detection**:
- Audit CI/CD logs for unauthorized access
- Git history review for unexpected commits to build scripts
- Artifact hash mismatches (expected vs observed)
- Network traffic anomalies (outbound connections from CI)

**Mitigation**:
- Least-privilege service accounts (specific permissions, no root)
- Ephemeral build environments (rebuild for each job, no persistence)
- Signed commits required for build script changes
- Network egress rules (whitelist only necessary destinations)
- Secret scanning in CI logs (prevent exposure)

### Unpinned Third-Party Actions
**Attack**: Attacker modifies third-party GitHub Action, affecting all users
- GitHub Actions auto-update on vague refs: `user/action@v1` pins to latest v1.*
- Attacker gains control of action repo (account compromise, typosquatting)
- Example: `actions/setup-node@v4` could suddenly inject backdoor if compromised

**Attack Flow**:
1. Popular action is targeted
2. Maintainer account compromised or action repository hijacked
3. Malicious code added to action
4. All workflows using unpinned action run malicious code
5. Backdoor embedded in artifacts or build environment

**Detection**:
- Audit GitHub Actions workflow files for vague version refs
- Check action commit history for suspicious changes
- Monitor action release notes for unexpected updates
- Verify action source repository health

**Mitigation**:
- Pin actions to exact commit: `@a1b2c3d4e5f6` not `@v1`
- Verify action source (official vs community; star count, age)
- Use GitHub's official setup actions (setup-node, setup-python)
- Review action code changes before updating
- Host critical actions internally or fork + maintain

### Secrets in Build Logs
**Attack**: CI/CD logs accidentally expose API keys, passwords, tokens
- Build logs often public or semi-public
- Attacker searches logs for hardcoded secrets, exfiltrated data
- GitHub Actions jobs visible in run history

**Attack Flow**:
1. Developer hardcodes secret in workflow or script
2. CI/CD executes, prints secret in logs
3. Attacker searches GitHub for `GITHUB_TOKEN:` in logs
4. Attacker uses token to access repository, push code, deploy

**Detection**:
- Scan CI logs for patterns: `token=`, `password=`, `key=`, AWS key formats
- Check for secrets in git history (`git log --all -p`)
- Audit environment variable exposure

**Mitigation**:
- Never hardcode secrets; use GitHub Secrets or vault
- Mark sensitive environment variables as secret (GitHub masking)
- Review any logs before publishing
- Rotate exposed secrets immediately
- Use OIDC tokens instead of static credentials

## Runtime Supply Chain Attacks

### Malicious Container Images
**Attack**: Attacker publishes malicious Docker image or hijacks existing image
- Tags: `myapp:latest`, `python:3.9` (misspelled)
- Includes backdoor, crypto-miner, or data exfiltrator
- Runs with application privileges in production

**Attack Flow**:
1. Image creation: Attacker publishes malicious Dockerfile
2. Discovery: Similar name to legitimate image (typosquatting)
3. Deployment: Developer uses image unknowingly
4. Execution: Backdoor runs in production container

**Detection**:
- Image scanning for known vulnerabilities (Trivy, Grype)
- Base image age analysis (very old = likely abandoned)
- Image signature verification (cosign)
- Registry trust assessment (official vs user repositories)

**Mitigation**:
- Pin images by digest: `node@sha256:abcd...` not `node:latest`
- Scan images before deployment
- Use official images from Docker Library
- Sign images with cosign
- Verify signatures in deployments

### Base Image Vulnerabilities
**Attack**: Base image contains known vulnerabilities affecting all derived images
- Example: `ubuntu:18.04` with unpatched OpenSSL
- Attacker exploits OS-level vulnerability through application

**Detection**:
- Scan base images for CVEs
- Track base image age and support lifecycle
- Monitor for patch availability

**Mitigation**:
- Use distroless images (google/distroless) for reduced surface
- Pin base images by digest
- Regularly rebuild images to pick up patches
- Use minimal base: alpine, distroless > ubuntu > centos

## Threat Matrix

| Threat | Severity | Detectability | Speed | Scope |
|--------|----------|---------------|-------|-------|
| Typosquatting | High | Medium | Days | Broad |
| Dependency confusion | Critical | Low | Hours | Targeted |
| Account takeover | Critical | Medium | Hours | Broad |
| Abandoned packages | Medium | High | Weeks | Targeted |
| Compromised CI/CD | Critical | Low | Hours | Broad |
| Unpinned actions | High | High | Minutes | Broad |
| Secrets in logs | Critical | Low | Minutes | Organization |
| Malicious containers | Critical | Medium | Minutes | Deployed services |
| Base image vulns | High | High | Days | All derived images |

## Audit Priorities

### Critical Path
1. Check for hardcoded secrets in CI/CD logs
2. Verify all GitHub Actions pinned to commit hash
3. Audit base image versions for known CVEs
4. Verify lockfiles exist and are up-to-date

### High Priority
1. Identify unmaintained dependencies (>1 year)
2. Check for GPL/copyleft license violations
3. Review CI/CD permissions (GITHUB_TOKEN scope)
4. Scan for typosquatting in dependencies

### Medium Priority
1. Implement package integrity verification
2. Add SBOM generation to pipeline
3. Set up image signing (cosign)
4. Establish SLSA baseline (L1/L2)

## Response Procedures

### If Typosquatting Detected
1. Remove typosquatted package from package.json
2. Reinstall with correct name and lockfile update
3. Check git history for usage
4. Report to package registry abuse team

### If Account Compromise Suspected
1. Check package publishing history
2. Compare source code in npm vs GitHub
3. Verify integrity of recent versions
4. Consider downgrading to pre-compromise version
5. Wait for maintainer security advisory

### If Secrets Exposed in Logs
1. Identify all affected components
2. Revoke secrets immediately (tokens, API keys)
3. Rotate credentials
4. Audit usage logs for compromise
5. Implement secret scanning in CI/CD
6. Review git history for leaked secrets

### If Malicious Container Detected
1. Remove from production immediately
2. Audit logs for suspicious activity
3. Rebuild with clean base image
4. Verify image integrity via signature
5. Update container deployment policies
