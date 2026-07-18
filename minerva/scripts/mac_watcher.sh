#!/bin/bash

# ==============================================================================
# Minerva Background Watcher (Portable)
# ==============================================================================

# Dynamically determine the absolute path to the Minerva vault root
# Assumes this script is located in Minerva/scripts/
MINERVA_DIR=$(cd "$(dirname "$0")/.." && pwd)
HEPHAESTUS_DIR="$MINERVA_DIR/../Hephaestus" # Adjust if Hephaestus is tracked elsewhere
LOG_FILE="/tmp/minerva_agent.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] macOS WatchPaths triggered script execution." >> "$LOG_FILE"

# Find approved memos
APPROVED_FILES=$(grep -rl "^status: approved$" "$MINERVA_DIR/manager_review/")

if [ -n "$APPROVED_FILES" ]; then
    for file in $APPROVED_FILES; do
        echo "[$(date)] Found approved memo: $file. Triggering handoff..." >> "$LOG_FILE"
        python3 "$MINERVA_DIR/scripts/agent.py" --mode handoff --source "$file" --target "$HEPHAESTUS_DIR/_Inbox"
    done
fi

echo "[$(date)] Triggering knowledge ingestion sweep..." >> "$LOG_FILE"
python3 "$MINERVA_DIR/scripts/agent.py" --mode ingest --source "$MINERVA_DIR/raw_sources" --vault "$MINERVA_DIR"

echo "[$(date)] Run complete." >> "$LOG_FILE"