#!/bin/bash

# ==============================================================================
# Minerva Daemon Installer
# Run this once after cloning the repository to a new machine.
# ==============================================================================

# Get the absolute path to the Minerva vault root
VAULT_PATH=$(cd "$(dirname "$0")/.." && pwd)
PLIST_NAME="com.minerva.agent.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Deploying Minerva daemon for vault at: $VAULT_PATH"

# Make the watcher script executable
chmod +x "$VAULT_PATH/scripts/mac_watcher.sh"

# Inject the absolute path into the template and save to the macOS LaunchAgents folder
sed "s|{{VAULT_PATH}}|$VAULT_PATH|g" "$VAULT_PATH/scripts/com.minerva.agent.plist.template" > "$PLIST_DEST"

# Unload the old daemon if it exists, then load the new one
launchctl unload "$PLIST_DEST" 2>/dev/null
launchctl load "$PLIST_DEST"

echo "Daemon successfully installed and loaded."
launchctl list | grep com.minerva.agent