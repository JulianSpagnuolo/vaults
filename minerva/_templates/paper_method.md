---
type: paper_method
citekey: [Zotero Citekey]
language: [Python | R | C++ | Nextflow/Snakemake]
input_modalities: [e.g., scRNA-seq, CITE-seq, Spatial]
tags: [methodology, computational_tool]
---

# [Tool/Algorithm Name]: [Paper Title]

## Core Concept
[A 2-sentence summary of what the algorithm actually does mathematically or conceptually, e.g., "Uses a variational autoencoder to integrate single-cell batches while preserving biological variance."]

## Benchmarking & Performance
- **Compared Against:** [e.g., Seurat v4, Harmony]
- **Key Advantages:** [e.g., Scales to 1M+ cells without RAM exhaustion, better rare-cell preservation]
- **Limitations/Caveats:** [e.g., Requires GPU for reasonable runtimes, sensitive to hyperparameter tuning]

## Implementation Considerations
- **Environment:** [e.g., PyTorch backend, requires dedicated conda env]
- **Integration:** [How hard would this be to drop into our existing Snakemake pipelines?]

## Proposed Internal Use Cases
- [ ] [Idea 1: Apply to the upcoming Phase II cohort to resolve the batch effects we saw in Phase I]
- [ ] [Idea 2: Benchmarking task to compare against our current standard]