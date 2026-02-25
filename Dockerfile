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

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install cline CLI and Azure DevOps MCP globally.
# Both are pre-installed so MCP launches instantly without npx download.
RUN npm install -g \
    "cline@${CLINE_VERSION}" \
    "@azure-devops/mcp@${ADO_MCP_VERSION}" \
    && npm cache clean --force

# node:slim already ships with a "node" user at UID/GID 1000 — reuse it.
# Default config directory (overridable via CLINE_DIR env var)
ENV CLINE_DIR=/home/node/.cline/data \
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
