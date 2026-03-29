#!/bin/bash
# audit-ci-config.sh - Audit CI/CD configuration for supply chain risks

set -euo pipefail

PROJECT_PATH="${1:-.}"
PLATFORM="${2:-auto}"

# CWE-426: Validate path - reject traversal attempts
if [[ "$PROJECT_PATH" == *".."* ]]; then
    echo "Error: Path traversal detected" >&2
    exit 1
fi

if [ ! -d "$PROJECT_PATH" ]; then
    echo "Error: Project path '$PROJECT_PATH' not found" >&2
    exit 1
fi

# Resolve to canonical path
PROJECT_PATH="$(cd "$PROJECT_PATH" 2>/dev/null && pwd)"

FINDINGS_FILE="/tmp/ci-audit-findings.json"
: > "$FINDINGS_FILE"  # Clear file

audit_github_actions() {
    local project="$1"
    local workflow_dir="$project/.github/workflows"

    if [ ! -d "$workflow_dir" ]; then
        echo "GitHub Actions: No workflows found"
        return
    fi

    echo "Auditing GitHub Actions workflows..."

    for workflow_file in "$workflow_dir"/*.yml "$workflow_dir"/*.yaml; do
        [ -e "$workflow_file" ] || continue

        local workflow_name=$(basename "$workflow_file")
        echo "  Checking: $workflow_name"

        # Check for unpinned actions
        if grep -q 'uses: .*@v[0-9]' "$workflow_file"; then
            echo "    CRITICAL: Unpinned action found (uses @v1 or @v2 instead of @commit)"
            # CWE-78/116: Use jq to safely construct JSON with proper escaping
            jq -n --arg file "$workflow_name" \
              '{"severity": "critical", "finding": "unpinned-action", "file": $file, "description": "Action version not pinned to commit hash"}' \
              >> "$FINDINGS_FILE"
        fi

        # Check for unpinned action references
        if grep -q 'uses: [^@]*$' "$workflow_file"; then
            echo "    HIGH: Action without version specified"
            # CWE-78/116: Use jq to safely construct JSON with proper escaping
            jq -n --arg file "$workflow_name" \
              '{"severity": "high", "finding": "missing-action-version", "file": $file}' \
              >> "$FINDINGS_FILE"
        fi

        # CWE-78: Add -- option terminator to grep patterns
        if grep -E -- '(GITHUB_TOKEN|API_KEY|password|secret|key)\s*=\s*['\''\"A-Za-z0-9]' "$workflow_file"; then
            echo "    CRITICAL: Potential hardcoded secret detected"
            # CWE-78/116: Use jq to safely construct JSON with proper escaping
            jq -n --arg file "$workflow_name" \
              '{"severity": "critical", "finding": "hardcoded-secret", "file": $file}' \
              >> "$FINDINGS_FILE"
        fi

        # Check for secrets exposure in logs
        if grep -q 'echo.*\${{' "$workflow_file"; then
            echo "    WARN: Environment variables printed to logs (potential secret exposure)"
        fi

        # Check for pull_request_target without restrictions
        if grep -q 'pull_request_target' "$workflow_file" && ! grep -q 'if.*pull_request.*approved' "$workflow_file"; then
            echo "    HIGH: pull_request_target without approval restriction"
            # CWE-78/116: Use jq to safely construct JSON with proper escaping
            jq -n --arg file "$workflow_name" \
              '{"severity": "high", "finding": "dangerous-workflow", "file": $file, "description": "pull_request_target can execute untrusted code"}' \
              >> "$FINDINGS_FILE"
        fi

        # Check for excessive permissions
        # CWE-697: GitHub Actions uses write-all (not "write: all") for permissions
        if grep -A5 'permissions:' "$workflow_file" | grep -qE 'write-all$|permissions:\s+write-all'; then
            echo "    HIGH: Excessive write permissions granted"
            # CWE-78/116: Use jq to safely construct JSON with proper escaping
            jq -n --arg file "$workflow_name" \
              '{"severity": "high", "finding": "excessive-permissions", "file": $file}' \
              >> "$FINDINGS_FILE"
        fi

        # Check for secrets() access
        if grep -q 'secrets\.\*' "$workflow_file"; then
            echo "    MEDIUM: Accessing all secrets with wildcard"
            # CWE-78/116: Use jq to safely construct JSON with proper escaping
            jq -n --arg file "$workflow_name" \
              '{"severity": "medium", "finding": "wildcard-secrets", "file": $file}' \
              >> "$FINDINGS_FILE"
        fi
    done
}

audit_gitlab_ci() {
    local project="$1"
    local ci_file="$project/.gitlab-ci.yml"

    if [ ! -f "$ci_file" ]; then
        echo "GitLab CI: No .gitlab-ci.yml found"
        return
    fi

    echo "Auditing GitLab CI configuration..."

    # CWE-78: Add -- option terminator to grep patterns
    if grep -E -- '(token|key|secret|password):\s*['\''\"A-Za-z0-9]' "$ci_file"; then
        echo "  CRITICAL: Hardcoded secret detected in .gitlab-ci.yml"
        echo "{\"severity\": \"critical\", \"finding\": \"hardcoded-secret\", \"file\": \".gitlab-ci.yml\"}" >> "$FINDINGS_FILE"
    fi

    # Check for docker image pinning
    if grep -E '^[[:space:]]*image:[[:space:]]*[^@]*:[^@]*$' "$ci_file" | grep -v '@'; then
        echo "  WARN: Docker images not pinned by digest"
    fi

    # Check for allow_failure on security tasks
    if grep -B2 'security\|scan\|audit' "$ci_file" | grep -q 'allow_failure: true'; then
        echo "  MEDIUM: Security job allows failure"
        echo "{\"severity\": \"medium\", \"finding\": \"security-job-allow-failure\", \"file\": \".gitlab-ci.yml\"}" >> "$FINDINGS_FILE"
    fi
}

audit_jenkins() {
    local project="$1"
    local jenkins_files=()

    for jf in "$project/Jenkinsfile" "$project/jenkinsfile" "$project/Jenkinsfile.groovy"; do
        [ -f "$jf" ] && jenkins_files+=("$jf")
    done

    if [ ${#jenkins_files[@]} -eq 0 ]; then
        echo "Jenkins: No Jenkinsfile found"
        return
    fi

    echo "Auditing Jenkinsfile(s)..."

    for jfile in "${jenkins_files[@]}"; do
        echo "  Checking: $(basename "$jfile")"

        # CWE-78: Add -- option terminator to grep patterns
        if grep -E -- "(password|token|key)\s*=" "$jfile" | grep -v -- 'credentials'; then
            echo "    CRITICAL: Credentials possibly hardcoded"
            echo "{\"severity\": \"critical\", \"finding\": \"hardcoded-credentials\", \"file\": \"$(basename "$jfile")\"}" >> "$FINDINGS_FILE"
        fi

        # Check for shell execution without escaping
        if grep -q 'sh.*\$' "$jfile" && ! grep -q 'set -e'; then
            echo "    MEDIUM: Shell commands without strict error handling"
        fi
    done
}

audit_docker() {
    local project="$1"

    if [ ! -f "$project/Dockerfile" ]; then
        return
    fi

    echo "Auditing Dockerfile..."

    # Check for :latest tag
    if grep -q 'FROM.*:latest' "$project/Dockerfile"; then
        echo "  CRITICAL: Base image uses :latest tag (not reproducible)"
        echo "{\"severity\": \"critical\", \"finding\": \"latest-tag\", \"file\": \"Dockerfile\", \"description\": \"Base image should be pinned by digest\"}" >> "$FINDINGS_FILE"
    fi

    # Check for digest pinning
    if ! grep 'FROM' "$project/Dockerfile" | grep -q '@sha256'; then
        echo "  HIGH: Base image not pinned by digest (only by tag)"
        echo "{\"severity\": \"high\", \"finding\": \"base-image-tag-not-digest\", \"file\": \"Dockerfile\"}" >> "$FINDINGS_FILE"
    fi

    # Check for RUN with || true (ignoring errors)
    if grep -q 'RUN.*||.*true' "$project/Dockerfile"; then
        echo "  MEDIUM: RUN command ignores errors with || true"
    fi

    # Check for unused layers
    if grep -q 'COPY.*\*' "$project/Dockerfile"; then
        echo "  INFO: Broad COPY pattern detected (may include unnecessary files)"
    fi
}

generate_summary() {
    echo ""
    echo "CI/CD Audit Summary"
    echo "=================="

    # CWE-20: wc -l outputs leading spaces on macOS; use grep -c for portability
    local total_findings
    total_findings=$(grep -c '' "$FINDINGS_FILE" 2>/dev/null || echo 0)
    if [ "$total_findings" -eq 0 ]; then
        echo "No findings detected"
        return 0
    fi

    local critical=$(grep -c '"critical"' "$FINDINGS_FILE" || true)
    local high=$(grep -c '"high"' "$FINDINGS_FILE" || true)
    local medium=$(grep -c '"medium"' "$FINDINGS_FILE" || true)

    echo "Total Findings: $total_findings"
    echo "  Critical: $critical"
    echo "  High: $high"
    echo "  Medium: $medium"

    if [ "$critical" -gt 0 ]; then
        echo ""
        echo "CRITICAL FINDINGS - Immediate action required:"
        grep '"critical"' "$FINDINGS_FILE" | jq '.description // .finding'
    fi

    return 0
}

main() {
    echo "Supply Chain Security Auditor - CI/CD Configuration Audit"
    echo "========================================================"
    echo ""

    if [ "$PLATFORM" = "auto" ] || [ "$PLATFORM" = "github" ]; then
        audit_github_actions "$PROJECT_PATH"
    fi

    if [ "$PLATFORM" = "auto" ] || [ "$PLATFORM" = "gitlab" ]; then
        audit_gitlab_ci "$PROJECT_PATH"
    fi

    if [ "$PLATFORM" = "auto" ] || [ "$PLATFORM" = "jenkins" ]; then
        audit_jenkins "$PROJECT_PATH"
    fi

    if [ "$PLATFORM" = "auto" ] || [ "$PLATFORM" = "docker" ]; then
        audit_docker "$PROJECT_PATH"
    fi

    generate_summary

    rm -f "$FINDINGS_FILE"
}

main "$@"
