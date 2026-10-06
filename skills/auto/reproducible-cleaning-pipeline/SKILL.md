---
name: reproducible-cleaning-pipeline
description: Use when cleaning CSV or log inputs with deduplication, timestamps, canonical labels, and derived summaries.
---
- Implement a small script or notebook-style pipeline that reads raw input and writes final artifacts.
- Count raw rows before filtering; count distinct usable records after deduplication and missing-value rules.
- Normalize labels with explicit mappings and verify no unexpected categories remain.
- Parse timestamps with timezone awareness and emit UTC in the required format.
- Sort output records by the specified keys before writing.
- Keep the generation script until outputs are verified, so artifacts can be regenerated consistently.
