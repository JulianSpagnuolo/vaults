# Minerva Automation Scripts

This directory contains the background automation, file-watching, and execution scripts required to run the Minerva agent locally on macOS. The system relies on native macOS tools (`launchd`, JXA) and the Python standard library, ensuring zero heavy third-party dependencies.

## Script Overview

| Script / File | Purpose | Trigger / Context |
|---|---|---|
| `install_daemon.sh` | Dynamically resolves the local repository path, compiles the `.plist` template, and registers the agent with macOS `launchd`. | Run once manually upon cloning the repository. |
| `com.minerva.agent.plist.template` | XML blueprint for the background daemon. Defines the watch paths (`raw_sources/`, `manager_review/`). | Consumed by `install_daemon.sh`. |
| `mac_watcher.sh` | The bridge bash script executed by macOS when watched files change. It locates relevant files and passes them to the Python agent. | Triggered automatically by macOS `launchd`. |
| `agent.py` | The core Python intelligence. Parses OKF formats, handles cross-vault task routing (`handoff`), and extracts private accomplishments (`ingest`). | Executed by `mac_watcher.sh`. |
| `calendar_sync.sh` | Queries the native macOS Calendar app via JXA and generates daily `event.md` stubs in `raw_sources/`. | Run manually, or scheduled via cron/Calendar automations. |

---

## Initial Setup & Installation

Follow these steps when setting up the Minerva vault on a new machine.

### 1. Grant Calendar Permissions
Before automating the calendar sync, macOS must grant Terminal access to your Calendar.
1. Open your terminal app (Terminal, iTerm, etc.).
2. Run the script manually:
   ```bash
   chmod +x scripts/calendar_sync.sh
   ./scripts/calendar_sync.sh
   ```
3. A macOS prompt will appear: **"Terminal would like to access your Calendar."** Click OK.
4. Verify that today's event stubs were correctly generated in ```raw_sources/```.

### 2. Install the Background Watcher (launchd)
This step links the vault to the native macOS file-watching daemon, ensuring the agent only uses CPU when files are modified.

Ensure the watcher script is executable:

```bash
chmod +x scripts/mac_watcher.sh
chmod +x scripts/agent.py
```
Run the deployment script:

```bash
chmod +x scripts/install_daemon.sh
./scripts/install_daemon.sh
```

The script will output a success message and list the active daemon. Verify that ```com.minerva.agent``` is running.

### 3. Verification & Troubleshooting
To confirm the watcher is functioning correctly:

Create a dummy file in ```raw_sources/```.

Check the logs to ensure the daemon caught the file creation:

```bash
cat /tmp/minerva_agent.log
```

If changes are not registering, unload and reload the daemon:

```bash
launchctl unload ~/Library/LaunchAgents/com.minerva.agent.plist
launchctl load ~/Library/LaunchAgents/com.minerva.agent.plist
```

