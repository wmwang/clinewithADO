#!/bin/bash
# =============================================================================
# Cline - Container Entrypoint
# =============================================================================
# Reads environment variables and configures Cline before launch.
#
# AI Provider (OpenAI-compatible):
#   OPENAI_API_KEY    - [required] API key
#   OPENAI_BASE_URL   - [optional] Custom endpoint (Azure OpenAI, Ollama, vLLM, etc.)
#   CLINE_MODEL       - [optional] Model override (default: gpt-4o)
# =============================================================================

set -euo pipefail

# CLINE_DIR is the root Cline uses; it internally appends "data/settings/" to it.
CONFIG_DIR="${CLINE_DIR:-/home/node/.cline}"
SETTINGS_DIR="${CONFIG_DIR}/data/settings"
MCP_CONFIG="${SETTINGS_DIR}/cline_mcp_settings.json"

mkdir -p "${SETTINGS_DIR}"

# Write empty MCP settings (no MCP servers configured)
if [ ! -f "${MCP_CONFIG}" ]; then
    echo '{"mcpServers":{}}' > "${MCP_CONFIG}"
fi

# ============================================================================
# Configure AI provider via cline auth (OpenAI-compatible only)
# ============================================================================

if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "[ERROR] OPENAI_API_KEY is required."
    exit 1
fi

_model="${CLINE_MODEL:-gpt-4o}"
_extra_args=()
[ -n "${OPENAI_BASE_URL:-}" ] && _extra_args+=(--base-url "${OPENAI_BASE_URL}")

echo "[INFO] AI provider: openai / ${_model}${OPENAI_BASE_URL:+  (base_url=${OPENAI_BASE_URL})}"
cline auth -p openai -k "${OPENAI_API_KEY}" -m "${_model}" "${_extra_args[@]}"

# ============================================================================
# Configure Azure DevOps (optional)
# ============================================================================
# If ADO_PAT is set, pre-configure az devops defaults so that both
# the az CLI (azure-devops extension) and the Python SDK work without
# extra auth setup inside the container.
#
#   az CLI  : reads AZURE_DEVOPS_EXT_PAT automatically for every az devops call
#   Python  : access ADO_ORG / ADO_PAT / ADO_PROJECT via os.environ as usual
#
if [ -n "${ADO_PAT:-}" ]; then
    if [ -z "${ADO_ORG:-}" ]; then
        echo "[ERROR] ADO_ORG is required when ADO_PAT is set."
        exit 1
    fi
    export AZURE_DEVOPS_EXT_PAT="${ADO_PAT}"
    _az_defaults=("organization=https://dev.azure.com/${ADO_ORG}")
    [ -n "${ADO_PROJECT:-}" ] && _az_defaults+=("project=${ADO_PROJECT}")
    az devops configure --defaults "${_az_defaults[@]}"
    echo "[INFO] Azure DevOps: org=${ADO_ORG}${ADO_PROJECT:+, project=${ADO_PROJECT}}"
fi

# ============================================================================
# Launch Cline (pass through all arguments)
# ============================================================================
openspec init --tools cline
echo "[INFO] Starting Cline..."
exec cline "$@"
