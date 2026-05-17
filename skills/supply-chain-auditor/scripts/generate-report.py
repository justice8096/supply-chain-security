#!/usr/bin/env python3
"""
generate-report.py - Generate structured supply chain audit report
Usage: python generate-report.py findings.json --output report.md
"""

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


# Hard-coded framework versions — single source of truth in the codebase, bumped
# when the skill version bumps. Audits emitted by this version of the script
# certify against THESE framework versions and no others. See CHANGELOG.md for
# what changed when bumping.
FRAMEWORK_VERSIONS = (
    "NIST SP 800-218A (2024-02), "
    "EU AI Act Art. 25 (Reg. (EU) 2024/1689), "
    "OpenSSF Scorecard v5.0 (2024-10), "
    "CISA SSDF Attestation Form (2024-03), "
    "ISO/IEC 42001:2023, "
    "ENISA NIS2 Technical Implementation Guidance (2024), "
    "SLSA v1.0 (2023-04)"
)
SOURCES_CURRENT_AS_OF_DEFAULT = "2026-05"
CHANGELOG_URL = "https://github.com/justice8096/supply-chain-security/blob/master/CHANGELOG.md"


def _git(args: list, cwd: Optional[str] = None) -> Optional[str]:
    """Run a git command and return stripped stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip() or None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def _detect_skill_version() -> str:
    """Read version from .claude-plugin/plugin.json relative to this script."""
    script_dir = Path(__file__).resolve().parent  # .../skills/supply-chain-auditor/scripts/
    # Walk up looking for .claude-plugin/plugin.json
    for parent in [script_dir.parent.parent.parent, script_dir.parent.parent, script_dir.parent]:
        plugin_json = parent / ".claude-plugin" / "plugin.json"
        if plugin_json.exists():
            try:
                with open(plugin_json, encoding="utf-8") as f:
                    return json.load(f).get("version", "unknown")
            except (json.JSONDecodeError, OSError):
                continue
    return "unknown"


def _detect_skill_commit() -> str:
    """git rev-parse --short HEAD inside the skill repo (script's own repo)."""
    script_dir = str(Path(__file__).resolve().parent)
    return _git(["rev-parse", "--short", "HEAD"], cwd=script_dir) or "unknown"


def _detect_target_repo(cwd: str) -> str:
    """Repo name from remote.origin.url, falling back to cwd basename."""
    url = _git(["config", "--get", "remote.origin.url"], cwd=cwd)
    if url:
        # Strip .git suffix, take last path segment
        name = url.rstrip("/").rsplit("/", 1)[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name
    return Path(cwd).name


def _detect_target_commit(cwd: str) -> str:
    return _git(["rev-parse", "--short", "HEAD"], cwd=cwd) or "unknown"


def _detect_target_branch(cwd: str) -> str:
    return _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd) or "unknown"


class AuditReport:
    def __init__(
        self,
        findings_file: str,
        skill_version: Optional[str] = None,
        skill_commit: Optional[str] = None,
        target_repo: Optional[str] = None,
        target_commit: Optional[str] = None,
        target_branch: Optional[str] = None,
        sources_current_as_of: Optional[str] = None,
    ):
        self.findings = self.load_findings(findings_file)
        self.timestamp = datetime.now(timezone.utc).isoformat()

        # Skill identity — detected from this script's repo unless overridden.
        self.skill_version = skill_version or _detect_skill_version()
        self.skill_commit = skill_commit or _detect_skill_commit()

        # Target project identity — detected from cwd unless overridden.
        cwd = os.getcwd()
        self.target_repo = target_repo or _detect_target_repo(cwd)
        self.target_commit = target_commit or _detect_target_commit(cwd)
        self.target_branch = target_branch or _detect_target_branch(cwd)

        # Source currency — caller can override (e.g. for re-audits citing a frozen date).
        self.sources_current_as_of = sources_current_as_of or SOURCES_CURRENT_AS_OF_DEFAULT

    @staticmethod
    def load_findings(filepath: str) -> Dict[str, Any]:
        """Load audit findings from JSON."""
        # CWE-703: Proper error handling - exit on failure instead of returning error dict
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                print(f"Error: Findings file must contain a JSON object, got {type(data).__name__}", file=sys.stderr)
                sys.exit(1)
            return data
        except FileNotFoundError:
            print(f"Error: Findings file not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in findings file: {e}", file=sys.stderr)
            sys.exit(1)

    def generate_markdown(self) -> str:
        """Generate markdown report."""
        report = []
        report.append("# Supply Chain Security Audit Report")
        report.append("")
        report.append(self._provenance_block())
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

    def _provenance_block(self) -> str:
        """Generate the required Provenance Block per the Skill Versioning and
        Addendum Framework. Every supply-chain-audit.md report must start with
        this — it's the linchpin that lets prior audits be identified for
        addendum filings when framework versions change."""
        lines = []
        lines.append("## Provenance Block")
        lines.append("")
        lines.append(f"- **Generated**: {self.timestamp}")
        lines.append(f"- **Generated by**: supply-chain-security v{self.skill_version} (`{self.skill_commit}`)")
        lines.append(
            f"- **Target project**: {self.target_repo} @ `{self.target_commit}` "
            f"on branch `{self.target_branch}`"
        )
        lines.append(
            f"- **Sources current as of**: {self.sources_current_as_of} "
            f"(except where individual findings note otherwise)"
        )
        lines.append(f"- **Framework versions**: {FRAMEWORK_VERSIONS}")
        lines.append(f"- **Skill changelog**: {CHANGELOG_URL}")
        return "\n".join(lines)

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
        lines.append("\n### SLSA Baseline Level")
        lines.append(f"- **Estimated Current Level**: L{slsa_level}")
        lines.append("- **Recommended Target**: L3 (minimum for production)")

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
            lines.append("**Gap Analysis to L3**:")
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
        description="Generate supply chain audit report from findings JSON. "
        "Emits a Provenance Block at the top of every report per the Skill "
        "Versioning and Addendum Framework."
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
    # Provenance Block inputs — all optional, auto-detected from git/plugin.json
    # if not provided. Required for legal-grade audit reproducibility.
    parser.add_argument(
        "--skill-version",
        help="Override detected skill version (default: read .claude-plugin/plugin.json)"
    )
    parser.add_argument(
        "--skill-commit",
        help="Override detected skill commit (default: git rev-parse on skill repo)"
    )
    parser.add_argument(
        "--target-repo",
        help="Target project repo name (default: detected from cwd git remote/basename)"
    )
    parser.add_argument(
        "--target-commit",
        help="Target project commit (default: cwd git rev-parse --short HEAD)"
    )
    parser.add_argument(
        "--target-branch",
        help="Target project branch (default: cwd git current branch)"
    )
    parser.add_argument(
        "--sources-current-as-of",
        help="Override sources-current-as-of date (YYYY-MM); default: " + SOURCES_CURRENT_AS_OF_DEFAULT
    )

    args = parser.parse_args()

    try:
        report = AuditReport(
            args.findings_file,
            skill_version=args.skill_version,
            skill_commit=args.skill_commit,
            target_repo=args.target_repo,
            target_commit=args.target_commit,
            target_branch=args.target_branch,
            sources_current_as_of=args.sources_current_as_of,
        )
        content = report.generate_markdown()

        # Force utf-8 — report content may contain checkmarks, em-dashes, and other non-ASCII.
        # Without this, Python on Windows uses cp1252 by default and raises UnicodeEncodeError.
        with open(args.output, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

        print(f"Report generated: {args.output}")
        print(f"Total findings: {len(report.findings.get('findings', []))}")

    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
