<!-- SPDX-License-Identifier: MIT -->

# Changelog

All notable changes to this skill are tracked here. Per the [Skill Versioning and Addendum Framework](https://github.com/justice8096/SecondBrainData/blob/main/SoftwarePractices/Skill-Versioning-and-Addendum-Framework.md), every change is classified by driver so downstream audit-artifact consumers can assess whether prior outputs need addendum filings.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with **change-driver tags** appended per entry:

- `[authority]` — underlying regulation, standard, or evidence base changed
- `[defect]` — typo, broken citation, misspelled term, wrong CFR number, factual error
- `[structural]` — section restructure, new locale, new lifespan layer, new domain, new severity scale
- `[voice]` — wording refinement, tone adjustment, ambiguity fix, accessibility improvement

All four drivers affect admissibility / persuasive weight of downstream artifacts. Every change is tracked equally.

## [Unreleased]

## [1.1.0] — 2026-05-17

Skill Versioning and Addendum Framework integration. Aligns supply-chain-security with the framework piloted in dyscalculia-support-skill v1.3.0–v1.3.2 and applied across the five sibling skill repos (dyslexia v1.3.0, LLMComplianceSkill v1.2.0, ai-compliance-extractors v1.1.0, post-commit-audit v1.2.0).

This is a documentation/governance release — no behavior changes to the audit dimensions, scripts, or report generation.

### Added `[structural]`
- `CHANGELOG.md` (this file) adopting the four-driver classification with retroactive entries for v1.0.0 and v1.0.1.
- **Audit-Artifact Provenance Block** required at the top of every generated `supply-chain-audit.md` report. Provenance Block captures: skill version, commit hash, generation date, target-project repo + commit, sources-current-as-of, framework versions, changelog URL. This is the linchpin of the addendum-filing workflow — prior audits stay identifiable when frameworks/standards update.

### Added `[authority]`
- Inline "*Sources current as of 2026-05*" markers + authority-version pin block in `skills/supply-chain-auditor/SKILL.md`. Pins all seven referenced frameworks: NIST SP 800-218A (Secure Software Development Framework, 2024-02), EU AI Act (Regulation (EU) 2024/1689) Article 25 (cybersecurity requirements for high-risk AI systems), OpenSSF Scorecard v5.0 (2024-10), CISA Secure Software Development Attestation Form (2024-03), ISO/IEC 42001:2023, ENISA NIS2 Technical Implementation Guidance (2024), SLSA v1.0 (2023-04).

### Process notes
- `.claude-plugin/plugin.json` version 1.0.1 → 1.1.0.
- License remains MIT (consistent with LICENSE file and plugin.json — no migration needed).
- The skill itself outputs `supply-chain-audit.md` under `{PROJECT_ROOT}/audits/` when invoked via post-commit-audit v1.1.0+ (which handles target-project routing). When invoked directly, current default cwd resolution applies.

## [1.0.1] — 2026-03-29 (retroactively documented)

### Fixed `[defect]`
- Resolved SC2155/SC2016 ShellCheck warnings in the supply-chain audit scripts: variable declarations separated from assignments, single-quote escaping corrected (commit `5cbc47f`).

## [1.0.0] — 2026-03-29 (retroactively documented)

### Added `[structural]`
- Initial release of supply-chain-security skill. Five audit dimensions: Dependency Analysis (transitive depth, vulnerability scanning, pinning posture), CI/CD Pipeline Security (secret handling, action pinning, permissions least-privilege), SBOM Generation (CycloneDX 1.4+ / SPDX 2.3, VEX statements), SLSA Compliance Assessment (L0-L4 mapping), Container and Runtime Supply Chain (image provenance, signature verification, runtime hardening).
- Framework mapping to NIST SP 800-218A, EU AI Act Article 25, OpenSSF Scorecard, CISA secure development controls, ISO 42001, ENISA 2025, SLSA v1.0.
- Self-audit artifacts in `audits/` (SAST/DAST scan, supply-chain audit, CWE mapping, LLM compliance report, contribution analysis, AUDIT_SUMMARY.txt, POST-REMEDIATION-INDEX.md).

---

## Change-driver workflow

When making a change:

1. **Classify the driver** — one of `[authority]`, `[defect]`, `[structural]`, `[voice]`.
2. **Cite the trigger** — for `[authority]`: name the framework version that changed (e.g., NIST SP 800-218A v1.2). For `[defect]`: describe what was wrong. For `[structural]`/`[voice]`: explain why.
3. **Estimate addendum burden** — would any prior generated `supply-chain-audit.md` need addendum filings as a result of this change? If yes, flag it; consumers (legal, compliance, security teams + the post-commit-audit orchestrator) rely on skill versioning to decide whether to refresh audits.

## Audit-artifact provenance

Every generated `supply-chain-audit.md` must begin with a provenance block of the form:

```
Generated YYYY-MM-DD by supply-chain-security vX.Y.Z (<skill-git-short-hash>)
Target project: <repo-name> @ <commit-short-hash> on branch <branch-name>
Sources current as of YYYY-MM except where individual sections note otherwise.
Framework versions: NIST SP 800-218A 2024-02, EU AI Act Art. 25, OpenSSF Scorecard v5.0,
                    CISA SSDF Attestation 2024-03, ISO/IEC 42001:2023, ENISA NIS2 2024,
                    SLSA v1.0
Skill changelog: https://github.com/justice8096/supply-chain-security/blob/master/CHANGELOG.md
```

## Related framework documentation

- [Skill Versioning and Addendum Framework](https://github.com/justice8096/SecondBrainData/blob/main/SoftwarePractices/Skill-Versioning-and-Addendum-Framework.md) — the cross-skill engineering principle this CHANGELOG implements.
- [Master Task List entry 17](https://github.com/justice8096/SecondBrainData) — rollout completed: this is the 6th of 8 in-scope skills (sast-dast-scanner and cwe-mapper round out the remaining queue).
- [Orchestrator: post-commit-audit](https://github.com/justice8096/post-commit-audit) — calls this skill as one of three Phase-1 scanners.
- [Sister skills already on framework](https://github.com): [dyscalculia-support-skill](https://github.com/justice8096/dyscalculia-support-skill), [dyslexia-support-skill](https://github.com/justice8096/dyslexia-support-skill), [LLMComplianceSkill](https://github.com/justice8096/LLMComplianceSkill), [ai-compliance-extractors](https://github.com/justice8096/ai-compliance-extractors), [post-commit-audit](https://github.com/justice8096/post-commit-audit).
