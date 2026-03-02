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
# Launch Cline (pass through all arguments)
# ============================================================================
openspec init --tools cline
echo "[INFO] Starting Cline..."
exec cline "$@"
