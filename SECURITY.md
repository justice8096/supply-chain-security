# Security Policy

## Vulnerability Reporting

To report a security vulnerability in this repository, please do **not** open a public GitHub issue.
Instead, contact the maintainer directly via the GitHub private vulnerability reporting feature:

1. Navigate to the repository on GitHub.
2. Click **Security** → **Report a vulnerability**.
3. Provide a clear description of the issue, steps to reproduce, and potential impact.

The maintainer will acknowledge receipt within 72 hours and work toward a fix within 14 days for
critical issues, or 30 days for lower-severity findings.

## Scope

This repository contains:

- **Bash scripts** (`skills/supply-chain-auditor/scripts/*.sh`) — shell scripts that inspect local
  project files. They do not make outbound network requests; all data remains local unless the user
  explicitly passes a remote registry URL as an argument.
- **Python script** (`skills/supply-chain-auditor/scripts/generate-report.py`) — reads a local
  findings JSON file and writes a markdown report. No network access.
- **Markdown reference documents** (`skills/supply-chain-auditor/references/`) — static documentation;
  no executable content.

**Out of scope**: This repository contains no web components, no server-side services, no APIs,
and no authentication flows. Reports about theoretical risks in static markdown or about
third-party tools referenced in documentation are generally out of scope.

## Known Limitations

The following limitations represent accepted risk or design constraints — they are not
vulnerabilities, but operators should be aware of them:

### SLSA Assessment

The SLSA compliance assessment performed by `audit-ci-config.sh` and documented in
`references/slsa-framework.md` is a **baseline heuristic**. It reviews observable build
configuration files. Full provenance verification (i.e., confirming a build artifact was
produced by a specific hermetic build platform) requires access to a signed provenance
attestation and is outside the scope of what these scripts can verify automatically.
Manual verification against the SLSA specification is required for claims above L2.

### Container Scanning

`generate-sbom.sh` and the container dimension of the audit require either local image
availability (`docker pull` already performed) or authenticated access to the target
registry. The scripts cannot pull images from private registries without valid credentials
provided by the operator. No credentials are stored or transmitted by the scripts.

### Typosquatting Detection

The dependency analysis dimension performs name-similarity checks against known registry
package lists. Detection is based on string-distance heuristics only. Novel or highly
targeted typosquatting attacks that fall outside common patterns (e.g., homoglyph attacks,
deeply nested scoped packages) may not be flagged. Manual review of unfamiliar dependencies
is always recommended.

## Dependencies

The scripts in this repository require the following runtime dependencies:

| Dependency | Version | Required |
|---|---|---|
| bash | 4.0+ | Required |
| python | 3.8+ | Required |
| syft | any | Optional — used by `generate-sbom.sh` for richer SBOM output |
| cosign | any | Optional — used for artifact signing verification |

Optional tools are invoked only when present; the scripts degrade gracefully when they are
not installed and note the omission in the output report.

## Supported Versions

Only the latest release of this skill is actively maintained. Apply updates by pulling the
latest commit from the `master` branch.
