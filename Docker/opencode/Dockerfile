# =============================================================================
# OpenCode CLI - OpenAI-compatible provider
# =============================================================================
# Packages:
#   - opencode : https://github.com/anomalyco/opencode
# =============================================================================

ARG NODE_VERSION=22
ARG OPENCODE_VERSION=latest

FROM node:${NODE_VERSION}-slim

ARG OPENCODE_VERSION

LABEL org.opencontainers.image.title="opencode" \
    org.opencontainers.image.description="OpenCode AI Agent CLI" \
    org.opencontainers.image.source="https://github.com/anomalyco/opencode" \
    opencode.version="${OPENCODE_VERSION}"

# Install system dependencies + Java, Python, and Azure CLI
# node:22-slim is Debian Bookworm — hardcode the dist name to avoid lsb-release dep.
RUN apt-get update && apt-get install -y \
    git \
    ca-certificates \
    curl \
    gnupg \
    python3 \
    python3-pip \
    python3-venv \
    default-jdk \
    maven \
    build-essential \
    make \
    jq \
    && curl -sLS https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && echo "deb [arch=$(dpkg --print-architecture)] https://packages.microsoft.com/repos/azure-cli/ bookworm main" \
    > /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update && apt-get install -y azure-cli \
    && rm -rf /var/lib/apt/lists/*

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

# Install OpenCode CLI globally
RUN npm install -g \
    "oh-my-opencode@${OPENCODE_VERSION}" \
    "@fission-ai/openspec@latest" \
    && npm cache clean --force

# node:slim already ships with a "node" user at UID/GID 1000 — reuse it.
# OPENCODE_DIR is the root that opencode config is stored.
ENV OPENCODE_DIR=/home/node/.opencode \
    TERM=xterm-256color

# Pre-create OpenCode config directories owned by the node user
RUN mkdir -p /home/node/.opencode \
    && chown -R node:node /home/node/.opencode

# Mount your project files here
WORKDIR /workspace
RUN chown node:node /workspace

# Copy entrypoint script as root, then switch to node user at runtime
COPY --chown=root:root entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER node

# Default: interactive OpenCode session
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD []
