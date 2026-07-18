---
type: event
date: [YYYY-MM-DD]
project: [Internal project name or Trial ID]
attendees: 
  - "[[Entity - Person 1]]"
  - "[[Entity - Person 2]]"
tags: [meeting, decision_log]
---

# [YYYY-MM-DD] - [Clear Title]

## TL;DR
[A strict 1-2 sentence summary of the meeting's primary outcome.]

## Strategic Decisions & Rationale
- **Decision:** [e.g., Switch from bulk RNA-seq to scRNA-seq for the secondary cohort.]
  - **Rationale:** [Biological or technical justification discussed.]
  - **Owner:** [[Entity Name]]

## Technical & Biological Context
[Capture any specific context regarding [[Concepts]], [[Datasets]], or [[Papers]] discussed. This acts as the connective tissue for the knowledge graph.]

## Proposed Action Items
- [ ] [Rough notes on tasks or dependencies. The agent will extract these into a `type: alignment` memo for manager review.]

---

## 🔒 Private Impact Logging 
*(Agent Directive: Extract the following lines and append them to `trackers/impact_tracker.md` under the current month, categorized by pillar.)*

- **Pillar:** [Data Engineering | Biomarker Discovery | Data Science Lead]
- **Action:** [What I explicitly achieved or delivered] -> **Impact:** [The resulting biological, strategic, or time-saving value]