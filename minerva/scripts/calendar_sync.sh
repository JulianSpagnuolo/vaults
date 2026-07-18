#!/bin/bash

# ==============================================================================
# Minerva Calendar Sync (Portable)
# Fetches today's meetings from macOS Calendar and generates event stubs.
# ==============================================================================

# Dynamically determine the vault path
VAULT_PATH=$(cd "$(dirname "$0")/.." && pwd)
TEMPLATE_FILE="$VAULT_PATH/_templates/event.md"
TARGET_DIR="$VAULT_PATH/raw_sources"
TODAY=$(date '+%Y-%m-%d')

echo "Syncing calendar for $TODAY..."

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: event.md template not found at $TEMPLATE_FILE"
    exit 1
fi

# Fetch today's events using macOS JXA (JavaScript for Automation)
# This queries the native Calendar.app without needing third-party packages.
EVENTS=$(osascript -l JavaScript -e "
    const app = Application('Calendar');
    const today = new Date();
    today.setHours(0,0,0,0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    let eventTitles = [];
    app.calendars().forEach(c => {
        try {
            let evts = c.events.whose({ startDate: { '>=': today, '<': tomorrow } })();
            evts.forEach(e => {
                if (e.summary()) {
                    eventTitles.push(e.summary());
                }
            });
        } catch(err) {} // Ignore calendars without permission or events
    });
    // Return unique events joined by newlines
    [...new Set(eventTitles)].join('\n');
")

# If no events, exit gracefully
if [ -z "$EVENTS" ]; then
    echo "No events found for today."
    exit 0
fi

# Generate stubs
echo "$EVENTS" | while IFS= read -r MEETING_TITLE; do
    # Skip empty lines
    [ -z "$MEETING_TITLE" ] && continue
    
    # Sanitize the meeting title for the filesystem (remove slashes, colons, etc.)
    SAFE_TITLE=$(echo "$MEETING_TITLE" | sed -e 's/[^A-Za-z0-9 _-]/_/g' -e 's/ /_/g')
    
    FILE_NAME="${TODAY}_${SAFE_TITLE}.md"
    FILE_PATH="$TARGET_DIR/$FILE_NAME"
    
    if [ -f "$FILE_PATH" ]; then
        echo "Stub already exists: $FILE_NAME (Skipping)"
    else
        # Copy the template and inject the title/date
        sed -e "s/\[YYYY-MM-DD\]/$TODAY/g" \
            -e "s/\[Clear Title\]/$MEETING_TITLE/g" \
            "$TEMPLATE_FILE" > "$FILE_PATH"
        
        echo "Created stub: $FILE_NAME"
    fi
done

echo "Calendar sync complete."