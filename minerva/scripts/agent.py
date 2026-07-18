#!/usr/bin/env python3

import os
import re
import sys
import argparse
from datetime import datetime

# =============================================================================
# Minerva OKF Parser & Agent Logic
# =============================================================================

def parse_okf(filepath):
    """Parses a markdown file with YAML frontmatter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to split frontmatter and body
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content

    yaml_block, body = match.groups()
    
    # Minimal dictionary parser for standard YAML frontmatter (no external dependencies)
    metadata = {}
    for line in yaml_block.strip().split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            metadata[key.strip()] = val.strip().strip('"').strip("'")
            
    return metadata, body

def update_status(filepath, new_status):
    """Updates the status field in the YAML frontmatter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the exact status line
    updated_content = re.sub(
        r'^status:\s*.*$', 
        f'status: {new_status}', 
        content, 
        flags=re.MULTILINE
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def execute_handoff(source_file, target_dir):
    """Converts an approved alignment/pitch into a Hephaestus handoff stub."""
    metadata, body = parse_okf(source_file)
    
    # Ensure it's actually approved before acting
    if metadata.get('status') != 'approved':
        print(f"Skipping {source_file} - Status is not 'approved'")
        return

    project_name = metadata.get('project', metadata.get('project_name', 'Unnamed_Project'))
    today = datetime.today().strftime('%Y-%m-%d')
    safe_project = re.sub(r'[^A-Za-z0-9_-]', '_', project_name)
    filename = os.path.basename(source_file).replace('.md', '')
    
    # Extract unresolved action items
    tasks = [line.strip() for line in body.split('\n') if line.strip().startswith('- [ ]')]
    
    # Format the Handoff Payload
    handoff_content = f"# {today} Handoff: {project_name}\n\n"
    handoff_content += f"**Source Alignment:** [obsidian://open?vault=Minerva&file=manager_review/{filename}]\n\n"
    handoff_content += "## Action Items & Dependencies\n"
    
    if tasks:
        handoff_content += "\n".join(tasks)
    else:
        handoff_content += "- [ ] Review project alignment (No specific tasks extracted)."

    # Write to Hephaestus Inbox
    out_file = os.path.join(target_dir, f"{today}_Handoff_{safe_project}.md")
    os.makedirs(target_dir, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(handoff_content)

    print(f"Generated handoff: {out_file}")
    
    # Lock the source file
    update_status(source_file, 'handed_off')
    print(f"Locked source memo: {source_file}")

def update_frontmatter(filepath, key, value):
    """Adds or updates a specific key in the YAML frontmatter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If the key exists, replace it
    if re.search(rf'^{key}:\s*.*$', content, flags=re.MULTILINE):
        updated_content = re.sub(
            rf'^{key}:\s*.*$', 
            f'{key}: {value}', 
            content, 
            flags=re.MULTILINE
        )
    # Otherwise, inject it right before the closing ---
    else:
        updated_content = re.sub(
            r'\n---\n(.*)', 
            f'\n{key}: {value}\n---\n\\1', 
            content, 
            flags=re.DOTALL,
            count=1
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def route_impact_to_tracker(tracker_path, pillar_raw, impact_line):
    """Routes an extracted impact statement to the correct pillar and month in the tracker."""
    if not os.path.exists(tracker_path):
        print(f"Error: Tracker not found at {tracker_path}")
        return

    with open(tracker_path, 'r', encoding='utf-8') as f:
        tracker_content = f.read()

    current_month = datetime.today().strftime('%B %Y')
    
    # Map raw pillar text to exact tracker headers
    pillar_map = {
        'Data Engineering': '### 🛠️ Data Engineering & Infrastructure',
        'Biomarker Discovery': '### 🔬 Biomarker Discovery & Clinical Strategy',
        'Data Science Lead': '### 🤝 Data Science Lead & Resource Leverage'
    }
    
    # Fuzzy match the pillar
    target_header = None
    for key, header in pillar_map.items():
        if key.lower() in pillar_raw.lower():
            target_header = header
            break
            
    if not target_header:
        print(f"Warning: Could not map pillar '{pillar_raw}'. Skipping line: {impact_line}")
        return

    # 1. Ensure the current month exists. If not, this requires a template insertion (omitted for brevity, assumes month exists or handles basic append)
    if f"## {current_month}" not in tracker_content:
        # Prepend the new month block to the top of the file, just below the agent directive
        new_month_block = f"\n## {current_month}\n\n{pillar_map['Data Engineering']}\n*(Focus: Snakemake pipelines, automation, scale, velocity, local server configuration)*\n\n{pillar_map['Biomarker Discovery']}\n*(Focus: Scientific insights, target discovery, trial Go/No-Go decisions, high-dimensional assay findings)*\n\n{pillar_map['Data Science Lead']}\n*(Focus: Vendor management, scoping work packages, unblocking clinical ops, cross-functional alignment)*\n\n"
        tracker_content = re.sub(
            r'(> \*\*Format:\*\*.*?)\n', 
            f'\\1\n{new_month_block}', 
            tracker_content, 
            flags=re.DOTALL
        )

    # 2. Insert the impact line under the correct month and pillar
    # We use a regex that looks for the month, then looks for the specific pillar header within that month,
    # and inserts the impact line immediately after the italicized *(Focus...)* line.
    
    pattern = rf'(## {current_month}.*?{re.escape(target_header)}\n\*\([^\)]+\)\*)'
    replacement = rf'\1\n{impact_line}'
    
    updated_tracker = re.sub(pattern, replacement, tracker_content, flags=re.DOTALL | re.IGNORECASE)

    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(updated_tracker)


def execute_ingest(source_dir, vault_dir):
    """Processes raw files, extracts private impact logs, and routes them to the tracker."""
    tracker_path = os.path.join(vault_dir, "trackers", "impact_tracker.md")
    
    for filename in os.listdir(source_dir):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(source_dir, filename)
        metadata, body = parse_okf(filepath)

        # Only process event files that haven't been logged yet
        if metadata.get('type') == 'event' and metadata.get('impact_logged') != 'true':
            
            # Look for the private impact section
            impact_section_match = re.search(r'## 🔒 Private Impact Logging\s*(.*)', body, re.DOTALL)
            
            if impact_section_match:
                impact_text = impact_section_match.group(1).strip()
                lines = impact_text.split('\n')
                
                current_pillar = None
                impact_extracted = False
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('- **Pillar:**'):
                        current_pillar = line.replace('- **Pillar:**', '').strip()
                    elif line.startswith('- **Action:**') and current_pillar:
                        # Found a valid impact line, route it
                        route_impact_to_tracker(tracker_path, current_pillar, line)
                        impact_extracted = True
                        print(f"Routed impact to {current_pillar} from {filename}")
                
                # Lock the file from future impact extractions
                if impact_extracted:
                    update_frontmatter(filepath, 'impact_logged', 'true')
                    print(f"Locked impact extraction for {filename}")

        # Note: Future logic for Rule 1.1 (Clinical Papers) and Rule 1.2 (Datasets) goes here.

# =============================================================================
# CLI Routing
# =============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Minerva Background Agent")
    parser.add_argument('--mode', choices=['handoff', 'ingest'], required=True)
    parser.add_argument('--source', help="Source file or directory")
    parser.add_argument('--target', help="Target directory (for handoff)")
    parser.add_argument('--vault', help="Root vault directory (for ingest)")
    
    args = parser.parse_args()

    if args.mode == 'handoff':
        if not args.source or not args.target:
            sys.exit("Error: --source and --target are required for handoff mode.")
        execute_handoff(args.source, args.target)
        
    elif args.mode == 'ingest':
        if not args.source or not args.vault:
            sys.exit("Error: --source and --vault are required for ingest mode.")
        execute_ingest(args.source, args.vault)