#!/usr/bin/env python3
"""
generate-report.py - Generate structured supply chain audit report
Usage: python generate-report.py findings.json --output report.md
"""

import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any

class AuditReport:
    def __init__(self, findings_file: str):
        self.findings = self.load_findings(findings_file)
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    @staticmethod
    def load_findings(filepath: str) -> Dict[str, Any]:
        """Load audit findings from JSON."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"error": "Findings file not found"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in findings file"}

    def generate_markdown(self) -> str:
        """Generate markdown report."""
        report = []
        report.append("# Supply Chain Security Audit Report")
        report.append(f"\n**Generated**: {self.timestamp}")
        report.append("")

        report.append("## Executive Summary")
        report.append(self._summary_section())

        report.append("\n## Risk Matrix")
        report.append(self._risk_matrix())

        report.append("\n## Detailed Findings")
        report.append(self._detailed_findings())

        report.append("\n## SLSA Compliance Assessment")
        report.append(self._slsa_assessment())

        report.append("\n## Framework Compliance Mapping")
        report.append(self._framework_mapping())

        report.append("\n## Remediation Roadmap")
        report.append(self._remediation_roadmap())

        return "\n".join(report)

    def _summary_section(self) -> str:
        """Generate executive summary."""
        lines = []

        # Count findings by severity
        findings = self.findings.get("findings", [])
        critical = len([f for f in findings if f.get("severity") == "critical"])
        high = len([f for f in findings if f.get("severity") == "high"])
        medium = len([f for f in findings if f.get("severity") == "medium"])
        low = len([f for f in findings if f.get("severity") == "low"])

        lines.append(f"- **Total Findings**: {len(findings)}")
        lines.append(f"  - Critical: {critical}")
        lines.append(f"  - High: {high}")
        lines.append(f"  - Medium: {medium}")
        lines.append(f"  - Low: {low}")

        # Top findings
        if critical > 0:
            lines.append("\n### Top Priority Issues")
            for finding in [f for f in findings if f.get("severity") == "critical"][:3]:
                lines.append(f"- **{finding.get('title', 'Unknown')}**: {finding.get('description', '')}")

        # SLSA estimate
        slsa_level = self._estimate_slsa_level()
        lines.append(f"\n### SLSA Baseline Level")
        lines.append(f"- **Estimated Current Level**: L{slsa_level}")
        lines.append(f"- **Recommended Target**: L3 (minimum for production)")

        return "\n".join(lines)

    def _risk_matrix(self) -> str:
        """Generate risk severity matrix."""
        lines = []
        lines.append("| Severity | Count | Impact | Timeline |")
        lines.append("|----------|-------|--------|----------|")

        findings = self.findings.get("findings", [])
        severities = [
            ("Critical", "critical", "Immediate security risk", "0-7 days"),
            ("High", "high", "Significant vulnerability", "1-30 days"),
            ("Medium", "medium", "Notable risk", "30-90 days"),
            ("Low", "low", "Minor improvement", "90+ days"),
        ]

        for label, severity, impact, timeline in severities:
            count = len([f for f in findings if f.get("severity") == severity])
            lines.append(f"| {label} | {count} | {impact} | {timeline} |")

        return "\n".join(lines)

    def _detailed_findings(self) -> str:
        """Generate detailed findings section."""
        lines = []
        findings = self.findings.get("findings", [])

        if not findings:
            return "No findings detected."

        # Group by severity
        for severity in ["critical", "high", "medium", "low"]:
            severity_findings = [f for f in findings if f.get("severity") == severity]
            if not severity_findings:
                continue

            lines.append(f"\n### {severity.upper()}")
            for finding in severity_findings:
                lines.append(f"\n#### {finding.get('title', 'Untitled')}")
                lines.append(f"- **Category**: {finding.get('category', 'General')}")
                lines.append(f"- **Description**: {finding.get('description', '')}")
                lines.append(f"- **Affected**: {finding.get('affected_component', 'Unknown')}")
                if finding.get('recommendation'):
                    lines.append(f"- **Recommendation**: {finding.get('recommendation')}")

        return "\n".join(lines)

    def _slsa_assessment(self) -> str:
        """Generate SLSA level assessment."""
        lines = []

        slsa_level = self._estimate_slsa_level()
        lines.append(f"**Current SLSA Level**: L{slsa_level}")
        lines.append("")

        # SLSA level descriptions
        slsa_descriptions = {
            0: "No security controls; ad-hoc builds",
            1: "Provenance available; version control present",
            2: "Signed provenance; immutable commits",
            3: "Build isolation; locked dependencies",
            4: "Hermetic builds; reproducible artifacts",
        }

        lines.append(f"**Description**: {slsa_descriptions.get(slsa_level, 'Unknown')}")
        lines.append("")

        if slsa_level < 3:
            lines.append(f"**Gap Analysis to L3**:")
            lines.append("- [ ] Implement signed provenance (cosign/Sigstore)")
            lines.append("- [ ] Enforce branch protection (no force-push)")
            lines.append("- [ ] Pin all dependencies (package-lock.json, go.sum, Cargo.lock)")
            lines.append("- [ ] Build isolation (containerized CI/CD)")
            lines.append("- [ ] Pin all GitHub Actions to commit hash")

        return "\n".join(lines)

    def _framework_mapping(self) -> str:
        """Generate framework compliance mapping."""
        lines = []

        findings = self.findings.get("findings", [])
        frameworks = {
            "NIST SP 800-218A": ["PS.2.1", "PS.3.1", "PS.3.2"],
            "EU AI Act Article 25": ["Technical Documentation", "Risk Management"],
            "OpenSSF Scorecard": ["Code Review", "Branch Protection", "Signed Releases"],
            "CISA 8 Practices": ["1. Version Control", "2. Secure Build", "3. SBOM"],
            "SLSA v1.0": ["Provenance", "Build Integrity", "Artifact Signing"],
        }

        for framework, controls in frameworks.items():
            lines.append(f"\n### {framework}")
            lines.append(f"**Status**: {'Compliant' if len(findings) < 5 else 'Non-Compliant'}")
            for control in controls:
                status = "✓" if "secret" not in str(findings).lower() else "✗"
                lines.append(f"- {status} {control}")

        return "\n".join(lines)

    def _remediation_roadmap(self) -> str:
        """Generate remediation roadmap."""
        lines = []

        findings = self.findings.get("findings", [])
        critical = [f for f in findings if f.get("severity") == "critical"]
        high = [f for f in findings if f.get("severity") == "high"]

        lines.append("### Phase 1: Immediate (0-7 days)")
        if critical:
            for finding in critical[:3]:
                lines.append(f"- [ ] {finding.get('title', 'Critical finding')}")
        else:
            lines.append("- [ ] No critical findings")

        lines.append("\n### Phase 2: Near-term (1-30 days)")
        if high:
            for finding in high[:5]:
                lines.append(f"- [ ] {finding.get('title', 'High finding')}")
        else:
            lines.append("- [ ] No high findings")

        lines.append("\n### Phase 3: Medium-term (30-90 days)")
        lines.append("- [ ] Implement SBOM generation in CI/CD")
        lines.append("- [ ] Set up artifact signing (cosign)")
        lines.append("- [ ] Establish dependency update policy")
        lines.append("- [ ] Configure secret scanning")

        lines.append("\n### Phase 4: Long-term (90+ days)")
        lines.append("- [ ] Achieve SLSA L3 baseline")
        lines.append("- [ ] Implement reproducible builds")
        lines.append("- [ ] Set up supply chain monitoring")
        lines.append("- [ ] Establish incident response SLAs")

        return "\n".join(lines)

    def _estimate_slsa_level(self) -> int:
        """Estimate SLSA level based on findings."""
        findings = self.findings.get("findings", [])

        # Simple heuristic based on critical findings
        critical_count = len([f for f in findings if f.get("severity") == "critical"])

        if critical_count > 5:
            return 0
        elif critical_count > 3:
            return 1
        elif critical_count > 1:
            return 2
        else:
            return 3

def main():
    parser = argparse.ArgumentParser(
        description="Generate supply chain audit report from findings JSON"
    )
    parser.add_argument("findings_file", help="Path to findings JSON file")
    parser.add_argument(
        "--output", "-o",
        default="audit-report.md",
        help="Output markdown file (default: audit-report.md)"
    )
    parser.add_argument(
        "--format", "-f",
        default="markdown",
        choices=["markdown", "json"],
        help="Output format"
    )

    args = parser.parse_args()

    try:
        report = AuditReport(args.findings_file)
        content = report.generate_markdown()

        with open(args.output, 'w') as f:
            f.write(content)

        print(f"Report generated: {args.output}")
        print(f"Total findings: {len(report.findings.get('findings', []))}")

    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
