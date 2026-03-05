#!/bin/bash
set -a

# =============================================================================
# OpenCode Docker Entrypoint
# =============================================================================
# Purpose: Handles ADO PAT authentication for az CLI in a headless way
#          before launching the primary opencode process.
# =============================================================================

# 1. Setup Azure CLI Auth via PAT (if provided)
if [ -n "$ADO_PAT" ] && [ -n "$ADO_ORG" ]; then
    echo "🔑 Configuring Azure CLI with ADO PAT..."
    
    # Store the URL for easy access inside tasks
    export ADO_ORG_URL="https://dev.azure.com/${ADO_ORG}"
    
    # Log into Azure DevOps via az CLI using the PAT via stdin
    echo "$ADO_PAT" | az devops login --organization "$ADO_ORG_URL"
    
    # Set default organization
    az devops configure --defaults organization="$ADO_ORG_URL"
    
    # Set default project if provided
    if [ -n "$ADO_PROJECT" ]; then
        az devops configure --defaults project="$ADO_PROJECT"
        echo "✅ Configured default project: $ADO_PROJECT"
    fi
    
    echo "✅ Authenticaton successful for organization: $ADO_ORG"
else
    echo "ℹ️  No ADO_PAT provided. Azure DevOps integration is disabled or requires manual login."
fi

# 2. Hand over execution to OpenCode
# If user passed arguments (e.g. `docker run ... run "fix the bug"`), 
# $@ will contain that array and `exec opencode` will run it.
# If no arguments were passed, $@ is empty and it will just start the TUI.
echo "🚀 Starting OpenCode..."
exec oh-my-opencode "$@"
