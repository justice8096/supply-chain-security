# SBOM Generation Guide

## Overview

A Software Bill of Materials (SBOM) is a formal, machine-readable inventory of software components, their versions, licenses, and known vulnerabilities. SBOMs enable organizations to understand software composition, track vulnerabilities throughout supply chains, and demonstrate transparency to customers and regulators.

## Standards

### CycloneDX

**Format**: JSON, XML
**Adoption**: Enterprise, industry-led (Cyclone DX project)
**Best for**: Component-centric inventory with vulnerability data

**Structure**:
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "metadata": {
    "timestamp": "2025-03-28T00:00:00Z",
    "tools": [{"vendor": "acme", "name": "generator", "version": "1.0"}]
  },
  "components": [
    {
      "type": "library",
      "name": "lodash",
      "version": "4.17.21",
      "licenses": [{"license": {"id": "MIT"}}],
      "purl": "pkg:npm/lodash@4.17.21",
      "externalReferences": [
        {
          "type": "vulnerability",
          "url": "https://nvd.nist.gov/vuln/detail/CVE-2021-23337"
        }
      ]
    }
  ],
  "vulnerabilities": [
    {
      "ref": "pkg:npm/lodash@4.17.21",
      "id": "CVE-2021-23337",
      "source": {"name": "NVD"},
      "ratings": [{"score": 5.3}],
      "status": "affected"
    }
  ],
  "services": []
}
```

**Strengths**:
- VEX (Vulnerability Exploitability eXchange) support
- Rich metadata (checksum, copyright, pURL)
- Dependency relationship graph
- Industry adoption (Microsoft, Google, NTIA)

**VEX Integration**:
```json
"vulnerabilities": [
  {
    "ref": "pkg:npm/lodash@4.17.21",
    "id": "CVE-2021-23337",
    "status": "unaffected",
    "justification": "component_not_present",
    "timestamp": "2025-03-28T00:00:00Z"
  }
]
```

### SPDX

**Format**: JSON, YAML, RDF, Tag-Value
**Adoption**: Standards body (Linux Foundation)
**Best for**: License compliance and legal workflows

**Structure**:
```json
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "my-project",
  "documentNamespace": "https://acme.com/sbom/my-project-v1.0",
  "creationInfo": {
    "created": "2025-03-28T00:00:00Z",
    "creators": ["Tool: syft-0.60.0"]
  },
  "packages": [
    {
      "SPDXID": "SPDXRef-Package-lodash",
      "name": "lodash",
      "versionInfo": "4.17.21",
      "downloadLocation": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
      "licenseConcluded": "MIT",
      "licenseDeclared": "MIT",
      "copyrightText": "Copyright JS Foundation and other contributors"
    }
  ],
  "relationships": [
    {
      "spdxElementId": "SPDXRef-DOCUMENT",
      "relationshipType": "DESCRIBES",
      "relatedSpdxElement": "SPDXRef-Package-my-project"
    }
  ]
}
```

**Strengths**:
- Legal workflow optimized
- File-level license tracking
- Clear creator/contributor metadata
- Formal standard (ISO/IEC 5962)

## Generation Tools

### Language-Specific

**Node.js**:
- `npm sbom` (npm 7.24+): Built-in CycloneDX generation
- `syft`: Universal SBOM generator, produces CycloneDX/SPDX
- `cyclonedx-npm`: Explicit CycloneDX generation

**Python**:
- `pip-licenses`: Simple license reporting
- `poetry show`: Dependency tree
- `pip-audit`: Vulnerability scanning with SBOM option
- `syft`: CycloneDX/SPDX with venv support

**Rust**:
- `cargo-sbom`: Generates CycloneDX from Cargo.lock
- `cargo-tree`: Dependency tree visualization
- `syft`: Scans Cargo.lock files

**Go**:
- `go list -json`: JSON dependency output
- `syft`: Go module scanning
- `cyclonedx-go`: CycloneDX generation

**Docker/Containers**:
- `syft`: Image scanning (Docker, OCI, registry)
- `trivy`: Image vulnerability scanning + SBOM
- `grype`: Vulnerability scanner with SBOM output

### Universal

**syft** (Anchore):
```bash
syft <image|dir|file> -o cyclonedx-json
syft <image|dir|file> -o spdx-json
```

Supports: docker images, directories, files, registries, archives

**trivy** (Aqua):
```bash
trivy image <image> --format cyclonedx
trivy fs <path> --format spdx
```

Focus: Security scanning with SBOM output

## Generation Best Practices

### Lockfile Approach (Recommended)
- Always use lockfiles for SBOM generation: package-lock.json, Cargo.lock, go.sum, poetry.lock
- Lockfiles provide exact versions; package files provide ranges
- SBOM generated from lockfile reflects actual build artifact

### Metadata Completeness
- Include `metadata.timestamp` (when SBOM created)
- Capture tool information: `metadata.tools[*].name`, `version`
- Document component relationships (contains, depends_on)
- Add external references for CVE tracking

### License Compliance
- Use SPDX identifiers: MIT, Apache-2.0, GPL-3.0-only, AGPL-3.0-or-later
- Flag license mismatches: declare vs concluded
- License expressions: MIT OR Apache-2.0, Apache-2.0 WITH LLVM-exception
- Identify GPL variants (strong copyleft vs weak)

### VEX Statements
- Mark known CVEs as affected/unaffected
- Justify unaffected: component_not_present, component_not_affected, vulnerability_not_present, vulnerable_code_not_present, vulnerable_code_not_in_execute_path, vulnerable_code_not_in_control_flow, vulnerable_code_cannot_be_controlled_by_adversary
- Use timestamps for tracking remediation progress

### Transitive Dependencies
- Flatten tree or maintain structure depending on use case
- Flat: simpler compliance scanning; tree: better understanding
- Include depth metadata for risk assessment

## Vulnerability Tracking

### VEX Workflow

1. **Initial SBOM**: All components listed, CVE status unknown
2. **Vulnerability Scan**: NVD/CVE database cross-reference
3. **VEX Statements**: Component owners mark status
   - `affected`: Component contains vulnerable code
   - `unaffected`: Does not contain, not exploitable, in unused code path
   - `under_investigation`: Status unknown
4. **Remediation**: Update version, add to policy exceptions

### Example VEX Statement
```json
{
  "ref": "pkg:npm/lodash@4.17.21",
  "id": "CVE-2021-23337",
  "status": "unaffected",
  "justification": "vulnerable_code_not_in_execute_path",
  "response": ["can_not_fix", "will_not_fix"],
  "timestamp": "2025-03-28T10:00:00Z",
  "detail": "Lodash used only for utility functions; vulnerable templateSettings not used in our code"
}
```

## Integration Points

### Build Pipeline
- Generate SBOM during CI/CD build
- Store SBOM as build artifact
- Attach SBOM to container image (OCI mediaType)
- Sign SBOM with Sigstore/cosign

### Artifact Repositories
- Maven Central: Publish with artifact
- npm registry: Include in package.json
- Container registries: Attach as separate artifact

### Compliance & Audit
- Automated license compliance checks
- Vulnerability tracking and remediation SLAs
- Export to compliance systems (Jira, ServiceNow)
- Dependency drift detection (version changes)

### Supply Chain Security
- Provenance verification (SLSA requirements)
- VEX consumption for risk assessment
- Incident response (quickly identify impacted components)

## Common Pitfalls

1. **Missing Lockfiles**: SBOM from package.json only shows ranges, not actual versions
2. **Incomplete Transitive Deps**: Only direct deps visible if lockfile not scanned
3. **License Data Gaps**: Inconsistent license field population
4. **No VEX Statements**: Can't distinguish affected vs unaffected CVEs
5. **Version Inflation**: Multiple entries for same component with different versions (monorepo)
6. **Stale SBOMs**: Generated once; doesn't track runtime dependency resolution
7. **Format Mismatch**: CycloneDX for scanning, SPDX for legal; conversion loses data

## Validation

```bash
# CycloneDX schema validation
npm install -g @cyclonedx/cyclonedx-npm
cyclonedx-npm --validate

# SPDX validation (online)
# https://sbom.example/validate
```

## Tools Comparison

| Tool | Format | Language | Speed | Accuracy |
|------|--------|----------|-------|----------|
| npm sbom | CycloneDX | Node | Fast | High |
| syft | Both | Universal | Fast | High |
| trivy | Both | Container | Fast | High |
| spdx-npm | SPDX | Node | Medium | High |
| pip-licenses | Text | Python | Very fast | Medium |

## Regulatory Requirements

- **NTIA Minimum Elements**: Name, version, supplier, unique identifier, dependency relationships
- **EU Cyber Act**: SBOM required for critical infrastructure software
- **Executive Order 14028**: SBOM in acquisition contracts
- **CISA Binding Operational Directive**: SBOMs for federal software
