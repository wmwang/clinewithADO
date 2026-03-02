# =============================================================================
# Cline CLI + Azure DevOps MCP Server
# =============================================================================
# Packages:
#   - cline        : https://github.com/cline/cline
#   - @azure-devops/mcp : https://github.com/microsoft/azure-devops-mcp
#
# Security note: cline v2.3.0 was a compromised supply-chain release (2026-02-17).
# Always pin to a known-safe version. Versions ≥ 2.4.0 include OIDC provenance.
# =============================================================================

ARG NODE_VERSION=22
ARG CLINE_VERSION=2.5.0
ARG ADO_MCP_VERSION=2.4.0

FROM node:${NODE_VERSION}-slim

ARG CLINE_VERSION
ARG ADO_MCP_VERSION

LABEL org.opencontainers.image.title="cline-ado" \
      org.opencontainers.image.description="Cline CLI with Azure DevOps MCP Server" \
      org.opencontainers.image.source="https://github.com/cline/cline" \
      cline.version="${CLINE_VERSION}" \
      ado-mcp.version="${ADO_MCP_VERSION}"

# Install system dependencies + Azure CLI (Microsoft official Debian repo)
# node:22-slim is Debian Bookworm — hardcode the dist name to avoid lsb-release dep.
RUN apt-get update && apt-get install -y \
    git \
    ca-certificates \
    curl \
    gnupg \
    python3 \
    python3-pip \
    && curl -sLS https://packages.microsoft.com/keys/microsoft.asc \
       | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && echo "deb [arch=$(dpkg --print-architecture)] https://packages.microsoft.com/repos/azure-cli/ bookworm main" \
       > /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update && apt-get install -y azure-cli \
    && rm -rf /var/lib/apt/lists/*

# Install cline CLI and Azure DevOps MCP globally.
# Both are pre-installed so MCP launches instantly without npx download.
# global-agent is a safety net for any HTTP calls outside typed-rest-client.
RUN npm install -g \
    "cline@${CLINE_VERSION}" \
    "@azure-devops/mcp@${ADO_MCP_VERSION}" \
    global-agent \
    "@fission-ai/openspec@latest" \
    && npm cache clean --force

# Install Azure DevOps Python SDK
# https://pypi.org/project/azure-devops/
# --break-system-packages is safe inside a container (Debian Bookworm PEP 668)
RUN pip3 install --no-cache-dir --break-system-packages azure-devops

# Use a global extension directory so all users (root at build-time, node at
# runtime) share the same install. Without this, az installs to /root/.azure
# and the non-root node user can't find it, triggering a runtime download.
ENV AZURE_EXTENSION_DIR=/opt/azure-extensions

# Install the Azure DevOps extension for az CLI.
# Pre-installed here so it's available immediately without runtime downloads.
RUN az extension add --name azure-devops --yes

# Patch @azure-devops/mcp: replace `undefined` IRequestOptions with a runtime
# proxy reader so typed-rest-client forwards requests through HTTPS_PROXY.
# See: https://github.com/microsoft/azure-devops-mcp/blob/main/src/index.ts
COPY patch-ado-mcp.js /tmp/patch-ado-mcp.js
RUN NODE_PATH=$(npm root -g) node /tmp/patch-ado-mcp.js && rm /tmp/patch-ado-mcp.js

# node:slim already ships with a "node" user at UID/GID 1000 — reuse it.
# CLINE_DIR is the root that Cline appends "data/settings/" to internally.
ENV CLINE_DIR=/home/node/.cline \
    TERM=xterm-256color

# Pre-create Cline config directories owned by the node user
RUN mkdir -p /home/node/.cline/data/settings \
    && chown -R node:node /home/node/.cline

# Mount your project files here
WORKDIR /workspace
RUN chown node:node /workspace

# Copy entrypoint script as root, then switch to node user at runtime
COPY --chown=root:root entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER node

# Default: interactive Cline session
# Override with: docker run ... image -y "your task description"
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD []
