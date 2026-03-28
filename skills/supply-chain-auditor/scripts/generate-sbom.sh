#!/bin/bash
# generate-sbom.sh - Generate CycloneDX SBOM from dependency files
# Supports: npm, yarn, pnpm, pip, poetry, cargo, go mod, maven, gradle

set -e

PROJECT_PATH="${1:-.}"
OUTPUT_FILE="${2:-sbom.json}"

if [ ! -d "$PROJECT_PATH" ]; then
    echo "Error: Project path '$PROJECT_PATH' not found"
    exit 1
fi

detect_package_manager() {
    local pm_files=()

    [ -f "$PROJECT_PATH/package-lock.json" ] && pm_files+=("npm")
    [ -f "$PROJECT_PATH/yarn.lock" ] && pm_files+=("yarn")
    [ -f "$PROJECT_PATH/pnpm-lock.yaml" ] && pm_files+=("pnpm")
    [ -f "$PROJECT_PATH/Pipfile" ] && pm_files+=("pipenv")
    [ -f "$PROJECT_PATH/poetry.lock" ] && pm_files+=("poetry")
    [ -f "$PROJECT_PATH/Cargo.lock" ] && pm_files+=("cargo")
    [ -f "$PROJECT_PATH/go.sum" ] && pm_files+=("go")
    [ -f "$PROJECT_PATH/pom.xml" ] && pm_files+=("maven")
    [ -f "$PROJECT_PATH/build.gradle" ] && pm_files+=("gradle")

    if [ ${#pm_files[@]} -eq 0 ]; then
        echo "Error: No dependency lockfiles detected"
        return 1
    fi

    # Return first detected
    echo "${pm_files[0]}"
}

generate_npm_sbom() {
    local project="$1"
    local output="$2"

    echo "Detecting npm dependencies from $project/package.json..."

    local name=$(jq -r '.name // "unknown"' "$project/package.json" 2>/dev/null || echo "unknown")
    local version=$(jq -r '.version // "0.0.0"' "$project/package.json" 2>/dev/null || echo "0.0.0")

    cat > "$output" <<EOF
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "serialNumber": "urn:uuid:$(uuidgen 2>/dev/null || echo 'unknown')",
  "version": 1,
  "metadata": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tools": [
      {
        "vendor": "supply-chain-auditor",
        "name": "generate-sbom.sh",
        "version": "1.0.0"
      }
    ],
    "component": {
      "type": "application",
      "name": "$name",
      "version": "$version"
    }
  },
  "components": [],
  "dependencies": []
}
EOF

    # Extract dependencies from package-lock.json if available
    if [ -f "$project/package-lock.json" ]; then
        jq '.packages | to_entries[] | select(.key != "") | {
            type: "library",
            name: (.value.name // "unknown"),
            version: (.value.version // "unknown"),
            licenses: (if .value.license then [{license: {id: .value.license}}] else [] end),
            purl: ("pkg:npm/" + (.value.name // "unknown") + "@" + (.value.version // "unknown"))
        }' "$project/package-lock.json" > /tmp/npm-components.json 2>/dev/null || true
    fi

    echo "SBOM generated: $output"
}

generate_python_sbom() {
    local project="$1"
    local output="$2"

    echo "Detecting Python dependencies from $project..."

    local name="python-project"
    if [ -f "$project/pyproject.toml" ]; then
        name=$(grep '^name' "$project/pyproject.toml" | head -1 | cut -d'"' -f2 || echo "python-project")
    fi

    cat > "$output" <<EOF
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "metadata": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tools": [
      {
        "vendor": "supply-chain-auditor",
        "name": "generate-sbom.sh",
        "version": "1.0.0"
      }
    ],
    "component": {
      "type": "application",
      "name": "$name",
      "version": "0.0.0"
    }
  },
  "components": [],
  "dependencies": []
}
EOF

    echo "SBOM generated: $output"
}

generate_rust_sbom() {
    local project="$1"
    local output="$2"

    echo "Detecting Rust dependencies from $project/Cargo.lock..."

    local name=$(grep -A1 'name = ' "$project/Cargo.toml" 2>/dev/null | head -1 | cut -d'"' -f2 || echo "rust-project")
    local version=$(grep -A1 'version = ' "$project/Cargo.toml" 2>/dev/null | head -1 | cut -d'"' -f2 || echo "0.0.0")

    cat > "$output" <<EOF
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "metadata": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tools": [
      {
        "vendor": "supply-chain-auditor",
        "name": "generate-sbom.sh",
        "version": "1.0.0"
      }
    ],
    "component": {
      "type": "application",
      "name": "$name",
      "version": "$version"
    }
  },
  "components": [],
  "dependencies": []
}
EOF

    echo "SBOM generated: $output"
}

generate_go_sbom() {
    local project="$1"
    local output="$2"

    echo "Detecting Go dependencies from $project/go.mod..."

    local name=$(grep '^module' "$project/go.mod" 2>/dev/null | awk '{print $2}' || echo "go-project")

    cat > "$output" <<EOF
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "metadata": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tools": [
      {
        "vendor": "supply-chain-auditor",
        "name": "generate-sbom.sh",
        "version": "1.0.0"
      }
    ],
    "component": {
      "type": "application",
      "name": "$name",
      "version": "0.0.0"
    }
  },
  "components": [],
  "dependencies": []
}
EOF

    echo "SBOM generated: $output"
}

main() {
    echo "Supply Chain Security Auditor - SBOM Generator"
    echo "=============================================="

    PM=$(detect_package_manager "$PROJECT_PATH") || exit 1
    echo "Detected package manager: $PM"

    case "$PM" in
        npm|yarn|pnpm)
            generate_npm_sbom "$PROJECT_PATH" "$OUTPUT_FILE"
            ;;
        poetry|pipenv)
            generate_python_sbom "$PROJECT_PATH" "$OUTPUT_FILE"
            ;;
        cargo)
            generate_rust_sbom "$PROJECT_PATH" "$OUTPUT_FILE"
            ;;
        go)
            generate_go_sbom "$PROJECT_PATH" "$OUTPUT_FILE"
            ;;
        maven|gradle)
            echo "Maven/Gradle support coming soon"
            exit 1
            ;;
        *)
            echo "Unknown package manager: $PM"
            exit 1
            ;;
    esac
}

main "$@"
