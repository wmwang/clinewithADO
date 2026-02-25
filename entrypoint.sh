#!/bin/bash
# =============================================================================
# Cline + Azure DevOps MCP - Container Entrypoint
# =============================================================================
# Reads environment variables and generates Cline configuration before launch.
#
# AI Provider (pick one):
#   ANTHROPIC_API_KEY     - Anthropic API key (uses claude-sonnet-4-5 by default)
#   OPENAI_API_KEY        - OpenAI API key (uses gpt-4o by default)
#   OPENROUTER_API_KEY    - OpenRouter API key
#   CLINE_PROVIDER        - Explicit provider name (requires CLINE_API_KEY + CLINE_MODEL)
#   CLINE_API_KEY         - API key when using CLINE_PROVIDER
#   CLINE_MODEL           - Model override for any provider
#
# Azure DevOps MCP:
#   ADO_ORG               - [required] Organization name (e.g. "contoso")
#   ADO_MCP_AUTH_TOKEN    - [required for headless] Personal Access Token
#   ADO_TENANT_ID         - Azure tenant ID (optional, for multi-tenant setups)
#   ADO_MCP_DOMAINS       - Comma-separated domains to enable (default: all)
#                           Values: core, work, work-items, search, test-plans,
#                                   repositories, wiki, pipelines, advanced-security
#   ADO_MCP_DISABLED      - Set to "true" to skip Azure DevOps MCP entirely
# =============================================================================

set -euo pipefail

CONFIG_DIR="${CLINE_DIR:-/home/node/.cline/data}"
SETTINGS_DIR="${CONFIG_DIR}/settings"
MCP_CONFIG="${SETTINGS_DIR}/cline_mcp_settings.json"

mkdir -p "${SETTINGS_DIR}"

# ============================================================================
# Step 1: Generate cline_mcp_settings.json via Node.js (safe JSON handling)
#
# Priority:
#   1. MCP_SETTINGS_FILE env var   — point to any pre-built JSON file
#   2. Volume-mounted config file  — user manages their own MCP list
#   3. Auto-generate from ADO_ORG  — default, ADO MCP only
#
# To add more MCP servers in the future, mount your own settings file:
#   -v ./my-mcp-settings.json:/mcp-settings.json
#   -e MCP_SETTINGS_FILE=/mcp-settings.json
# ============================================================================

export MCP_CONFIG_PATH="${MCP_CONFIG}"

# Check if the user provided a custom MCP settings file
CUSTOM_MCP_FILE="${MCP_SETTINGS_FILE:-}"

if [ -n "${CUSTOM_MCP_FILE}" ] && [ -f "${CUSTOM_MCP_FILE}" ]; then
    # Use the externally provided file directly
    cp "${CUSTOM_MCP_FILE}" "${MCP_CONFIG}"
    echo "[INFO] MCP settings loaded from: ${CUSTOM_MCP_FILE}"

elif [ -f "${MCP_CONFIG}" ] && [ -z "${ADO_ORG:-}" ]; then
    # Config already exists (e.g. from a persisted volume) and no ADO env vars
    # are set to trigger a regeneration — leave it untouched.
    echo "[INFO] Using existing MCP settings at: ${MCP_CONFIG}"

else
    # Auto-generate from environment variables (ADO MCP only)
    node -e "
const fs = require('fs');

const org        = process.env.ADO_ORG            || '';
const pat        = process.env.ADO_MCP_AUTH_TOKEN || '';
const disabled   = process.env.ADO_MCP_DISABLED === 'true' || !org;
const tenant     = process.env.ADO_TENANT_ID      || '';
const domainsRaw = process.env.ADO_MCP_DOMAINS    || '';

// Auth method: prefer explicit override, then infer from available credentials
const authMethod = process.env.ADO_AUTH_METHOD
  || (pat ? 'envvar' : 'interactive');

// CLI args for the mcp-server-azuredevops binary
const args = [org || 'YOUR_ORG', '--authentication', authMethod];
if (tenant)     args.push('--tenant', tenant);
if (domainsRaw) args.push('--domains', ...domainsRaw.split(',').map(d => d.trim()).filter(Boolean));

// Env vars passed to the MCP server child process
const env = pat ? { ADO_MCP_AUTH_TOKEN: pat } : {};

const config = {
  mcpServers: org ? {
    'azure-devops': { command: 'mcp-server-azuredevops', args, env, disabled }
  } : {}
};

fs.writeFileSync(process.env.MCP_CONFIG_PATH, JSON.stringify(config, null, 2) + '\n', 'utf8');
"
fi

# Status output
if [ -z "${ADO_ORG:-}" ]; then
    echo "[WARN] ADO_ORG not set — Azure DevOps MCP will be skipped."
    echo "[WARN] To enable: -e ADO_ORG=<your-org> -e ADO_MCP_AUTH_TOKEN=<PAT>"
else
    _auth_method="${ADO_AUTH_METHOD:-$([ -n "${ADO_MCP_AUTH_TOKEN:-}" ] && echo 'envvar' || echo 'interactive')}"
    echo "[INFO] Azure DevOps MCP: org=${ADO_ORG}  auth=${_auth_method}"
    if [ -z "${ADO_MCP_AUTH_TOKEN:-}" ]; then
        echo "[WARN] ADO_MCP_AUTH_TOKEN not set — browser auth will be attempted (fails in headless Docker)."
        echo "[WARN] For Docker/CI: set ADO_MCP_AUTH_TOKEN to a Personal Access Token."
    fi
fi

# ============================================================================
# Step 2: Configure AI provider via cline auth
#
# OpenAI-compatible (Azure OpenAI, Ollama, LM Studio, vLLM, etc.):
#   OPENAI_API_KEY + OPENAI_BASE_URL + CLINE_MODEL
#
# Fully custom provider:
#   CLINE_PROVIDER + CLINE_API_KEY + CLINE_MODEL (+ CLINE_BASE_URL optional)
# ============================================================================

_configure_provider() {
    local provider="$1" key="$2" model="$3" base_url="${4:-}"
    local extra_args=()
    [ -n "${base_url}" ] && extra_args+=(--base-url "${base_url}")
    echo "[INFO] AI provider: ${provider} / ${model}${base_url:+  (base_url=${base_url})}"
    cline auth -p "${provider}" -k "${key}" -m "${model}" "${extra_args[@]}"
}

if [ -n "${CLINE_PROVIDER:-}" ] && [ -n "${CLINE_API_KEY:-}" ]; then
    # Fully explicit — caller controls everything
    _configure_provider "${CLINE_PROVIDER}" "${CLINE_API_KEY}" "${CLINE_MODEL:-claude-sonnet-4-5-20250929}" "${CLINE_BASE_URL:-}"

elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    _configure_provider "anthropic" "${ANTHROPIC_API_KEY}" "${CLINE_MODEL:-claude-sonnet-4-5-20250929}"

elif [ -n "${OPENAI_API_KEY:-}" ] && [ -n "${OPENAI_BASE_URL:-}" ]; then
    # OpenAI-compatible with custom endpoint:
    # Azure OpenAI  → OPENAI_BASE_URL=https://<resource>.openai.azure.com/openai/deployments/<deploy>
    # Ollama        → OPENAI_BASE_URL=http://host.docker.internal:11434/v1
    # LM Studio     → OPENAI_BASE_URL=http://host.docker.internal:1234/v1
    # vLLM / other  → OPENAI_BASE_URL=http://your-server/v1
    _configure_provider "openai" "${OPENAI_API_KEY}" "${CLINE_MODEL:-gpt-4o}" "${OPENAI_BASE_URL}"

elif [ -n "${OPENAI_API_KEY:-}" ]; then
    _configure_provider "openai" "${OPENAI_API_KEY}" "${CLINE_MODEL:-gpt-4o}"

elif [ -n "${OPENROUTER_API_KEY:-}" ]; then
    _configure_provider "openrouter" "${OPENROUTER_API_KEY}" "${CLINE_MODEL:-anthropic/claude-sonnet-4-5}"

else
    echo "[WARN] No AI provider API key detected. Cline may not work without one."
    echo "[WARN]   ANTHROPIC_API_KEY                          — Claude (Anthropic)"
    echo "[WARN]   OPENAI_API_KEY                             — OpenAI (standard)"
    echo "[WARN]   OPENAI_API_KEY + OPENAI_BASE_URL           — OpenAI-compatible (Azure OpenAI / Ollama / LM Studio / vLLM)"
    echo "[WARN]   OPENROUTER_API_KEY                         — OpenRouter"
    echo "[WARN]   CLINE_PROVIDER + CLINE_API_KEY + CLINE_MODEL (+ CLINE_BASE_URL) — fully custom"
fi

# ============================================================================
# Step 3: Launch Cline (pass through all arguments)
# ============================================================================

echo "[INFO] Starting Cline..."
exec cline "$@"
