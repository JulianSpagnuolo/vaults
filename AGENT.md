# System Context & Maintenance Guide

**Target Audience:** Autonomous Coding Agents (e.g., Claude Code, Antigravity, SWE-agent)

**Purpose:** This document provides the architectural intent, constraints, and operational mechanics of the dual-vault system. Read this before proposing code changes, refactoring scripts, or extending capabilities.

## 1. Core Architecture & Separation of Concerns

This repository houses a dual-vault Obsidian system designed for a computational immunologist and data science lead. It operates on a strict separation of concerns to prevent context collapse:

- **Minerva (The Knowledge Vault):** A strategic knowledge base utilizing the Open Knowledge Format (OKF). It handles clinical trial literature extraction, pipeline state tracking, biological hypotheses (claims), entity resolution, and meeting event logs.
    
- **Hephaestus (The Execution Vault):** A centralized, agent-ready command center focused purely on execution. It tracks deadlines, project deliverables, and states using Kanban-style views and project-specific folders that mirror GitHub repositories.
    

**The Bridge:** The two vaults interact strictly via a one-way handoff mechanism. Minerva generates task payloads (from manager-approved memos) and drops them into the Hephaestus `_Inbox/`.

## 2. Directory Structure & Vault Mechanics

### Minerva (Knowledge & Strategy)

- `raw_sources/`: Immutable ingestion zone for daily calendar stubs (JXA-generated) and manual notes.
    
- `wiki/`: Agent-maintained OKF nodes (`concepts`, `claims`, `entities`, `datasets`, `methodologies`, `papers`).
    
- `for_review/`: Draft and pending project pitches or alignment memos awaiting manager approval.
    
- `trackers/`: Houses `impact_tracker.md`, a ledger populated dynamically by the background agent extracting private logs from meeting notes.
    
- `_templates/`: Source of truth for OKF YAML frontmatter structures.
    
- `scripts/`: Portable macOS background automation (launchd, bash, and python).
    

### Hephaestus (Execution)

- `_Inbox/`: The sole ingestion point for tasks handed off by Minerva.
    
- Project Folders: Structured identically to active GitHub repositories to maintain contextual alignment.
    
- Dataview Integrations: Queries tasks, upstream dependencies, and downstream delegations across the vault.
    

## 3. Automation & Scripting Constraints

When maintaining or extending the automation scripts located in `Minerva/scripts/`, you must adhere to the following constraints:

1. **Zero Third-Party Dependencies:** Scripts must run natively on an employer-provided MacBook Pro out of the box. Do not introduce requirements for `pip install` (e.g., `pandas`, `watchdog`, `pyyaml`). Use standard Python libraries (`re`, `os`, `json`) and native macOS tools (`launchd`, JXA, `bash`).
    
2. **Idempotency & State Locking:** Scripts must not double-process files. The current Python agent uses flags in the YAML frontmatter (e.g., `impact_logged: true` or `status: handed_off`) to lock extraction loops. Maintain this pattern.
    
3. **Portability (No Hardcoded Paths):** The system is a zero-state boilerplate designed to be cloned onto new machines. All scripts must dynamically resolve their execution paths (e.g., `VAULT_PATH=$(cd "$(dirname "$0")/.." && pwd)`). `launchd` `.plist` files must be generated from a `.template` file via an installation script.
    
4. **CPU Efficiency:** Do not write continuous `while True` polling loops. Utilize macOS `launchd` `WatchPaths` to trigger the Python agent only when filesystem modification events occur.
    

## 4. Extension Guidelines for Future Agents

If instructed to add new features or data types to this system, follow this workflow:

1. **Define the Schema:** Update `SCHEMA.md` in the Minerva root with the extraction logic, relationship mapping, or routing rules.
    
2. **Create the Template:** Add a new `type: [name].md` to the `_templates/` folder with strict OKF YAML frontmatter.
    
3. **Update the Parsing Logic:** Modify `Minerva/scripts/agent.py` to recognize the new `type`. Rely on stable regex anchors (e.g., `> **Format:**`) or frontmatter properties rather than flexible human language.
    
4. **Update the MOC:** Ensure the new folder or flow is linked in `00_MOC.md`.
    
5. **Maintain Separation:** Never build task execution or deadline tracking features into Minerva. Route them to Hephaestus. Never build broad biological knowledge graphs in Hephaestus. Route them to Minerva.