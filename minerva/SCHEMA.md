# Minerva / Vestus Schema & Execution Rules

## Purpose
This schema governs the automated ingestion, synthesis, and maintenance of a clinical biotech knowledge base using the Open Knowledge Format (OKF). The agent must read incoming manual notes and clinical literature, extract specific multidimensional data, map relationships, and route execution tasks to Hephaestus via an approval-based memo system.

## Directory Structure
- `/` - Root contains only `SCHEMA.md` and the `00_MOC.md` (Map of Content).
- `/raw_sources/` - Immutable ingestion directory for manual notes, downloaded PDFs, and dataset URIs.
- `/wiki/` - The agent-maintained OKF knowledge base (Concepts, Claims, Entities, Datasets, Papers).
- `/daily_notes/` - Chronological logs of milestones and meeting links.
- `/manager_review/` - Alignment Memos and Project Pitches awaiting state changes (`pending_review` -> `approved`).
- `/trackers/` - Strategic ledgers, notably `impact_tracker.md`.
- `/_templates/` - OKF YAML formatting rules.

---

## 1. Ingestion Rules

### Rule 1.1: Clinical Trial Paper Ingestion
When a source document is a clinical trial report or primary medical literature, use `type: paper_clinical`. Extract the following structured data. Do not guess; if missing, use "Not Reported".
- **Trial Phase & ID:** Extract the phase and registry number.
- **Cohort Dynamics:** Total N, treatment/control arm breakdown, and patient criteria.
- **Endpoints:** Quote the exact definition for Primary and Secondary endpoints.
- **Assays:** Explicitly list high-dimensional data generation methods (e.g., scRNA-seq, multiplex IHC, bulk TCR profiling).

### Rule 1.2: Dataset & Pipeline Ingestion
When a note references a new data batch or pipeline run, create or update a `type: dataset` node.
- **Storage:** Log the specific URI (S3 bucket, local NAS, etc.).
- **Pipeline State:** Extract and log the specific Snakemake pipeline Git commit hash used to process the data.
- **QC State:** Note if the data is Raw, QC_Passed, or Analyzed.

### Rule 1.3: Event & Meeting Ingestion
Manual notes will be dropped into pre-generated meeting stubs. When parsing these:
- **Attendee Resolution:** Verify attendees and link to their `type: entity` files. If a stakeholder is new, create a profile.
- **Decision & Rationale:** Isolate explicit decisions and capture the *technical or biological rationale* behind them.
- **Task Routing Limitation:** NEVER route tasks directly to Hephaestus from an event note. All tasks must pass through an Alignment Memo (Rule 3.1).
- **Impact Extraction:** Extract any bullets under `## 🔒 Private Impact Logging` and route them strictly to `trackers/impact_tracker.md`.

### Rule 1.4: Computational & Analytical Method Ingestion
When a source document details a computational algorithm, software package, or analytical method (e.g., scVI, CellCNN), use `type: paper_method`.
- **Core Concept:** Summarize the mathematical or technical mechanism.
- **Benchmarking:** Extract what the tool was compared against, its key advantages (e.g., memory scaling), and its limitations.
- **Implementation:** Identify the required environment (Python, R, GPU requirements).
- **Synthesis:** Propose 1-2 internal use cases based on known active datasets or pipeline bottlenecks in the wiki.

---

## 2. Extraction & Knowledge Mapping

### Rule 2.1: Biological Entity Resolution & Synonyms
Prevent duplication caused by synonymous nomenclature.
- Default to HGNC gene symbols or widely accepted modern nomenclature for the canonical filename.
- Check existing filenames AND `aliases` arrays before creating a new node.
- Add synonyms to the canonical node's `aliases` array and use pipe syntax when linking (e.g., `[[CD274|PD-L1]]`).

### Rule 2.2: Handling Conflicting Claims
When a new paper or internal dataset contradicts an existing claim:
- DO NOT overwrite the original claim or create a separate, opposing node.
- Log the new evidence under a `## Conflicting Evidence` heading in the existing `type: claim` node.
- Generate an `## Agent Synthesis` paragraph contrasting the methodologies (e.g., cohort powering, assay types).

### Rule 2.3: Interpersonal Context & Rapport
- **Objective Facts Only:** Capture stated hobbies, PTO, or explicit working preferences (e.g., async vs. sync communication).
- **NO Psychological Profiling:** Never infer personality traits or emotional states. 
- Append to a `## Rapport & Context` section in the entity node.

---

## 3. Task Approval & Cross-Vault Routing

### Rule 3.1: Task Extraction & Manager Approvals
When manual notes contain tasks, deliverables, or you are instructed to draft a new initiative, use the `manager_review/` directory.
1. **Drafting:** 
   - For standard execution tasks, draft a `type: alignment` memo. 
   - For proactive proposals (e.g., new dashboards, architecture refactors), draft a `type: pitch` memo.
2. **Initial State:** Set the YAML frontmatter to `status: pending_review` (or `status: draft` for pitches needing my edits).
3. **The Approval Trigger:** When an existing alignment or pitch file's frontmatter is manually changed to `status: approved`, you MUST extract the tasks, create a `[YYYY-MM-DD]_Handoff_[ProjectName].md` file, and save it to the `/path/to/Hephaestus/_Inbox/` directory.
4. **Locking the State:** After routing the tasks, change the source file's frontmatter to `status: handed_off`.

### Rule 3.2: Dependency Tracking Format
Categorize tasks in memos by flow direction:
- **Upstream (Blockers):** `- [ ] UPSTREAM: [@Name/Role] - [Deliverable]`
- **Downstream (Delegation):** `- [ ] DOWNSTREAM: [@Name/Role] - [Deliverable]`
- **My Deliverables:** `- [ ] [Deliverable description]`

---

## 4. Impact & Ledger Tracking

### Rule 4.1: Daily Notes Logging
- Locate or create the daily note (e.g., `daily_notes/2026-07-18.md`).
- Append a link to the generated `type: event` nodes for that day.
- Add a 1-sentence summary of minor milestones under `## Milestones`.

### Rule 4.2: The Impact Tracker
When processing the `## 🔒 Private Impact Logging` section of an event note, log it in `trackers/impact_tracker.md` under the current month. Categorize into:
1. **Data Engineering:** Infrastructure, Snakemake pipelines, velocity, local server scaling.
2. **Biomarker Discovery:** Scientific insights, target discovery, trial Go/No-Go decisions.
3. **Data Science Lead:** Vendor management, scoping work packages, cross-functional alignment.

---

## 5. The Linting Protocol
When triggered via cron to "lint the wiki", scan the `wiki/` directory and output a health report:
1. **Orphaned Nodes:** Flag pages with zero incoming links.
2. **Broken Graph Links:** Create empty stub pages for broken `[[Wiki Links]]`.
3. **Nomenclature Collapse:** Flag merge candidates if files share an alias.
4. **Action Item Leakage:** Delete any unchecked markdown boxes (`- [ ]`) in the knowledge graph. Tasks live only in `manager_review/` and Hephaestus.