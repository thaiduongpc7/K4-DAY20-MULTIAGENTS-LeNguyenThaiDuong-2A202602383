---
name: data-artifact-contracts
description: Use when a data-analysis task requires specific output files, schemas, units, or metadata.
---
- List every required artifact and schema before calculating results.
- Write all requested files, not just a narrative or partial answer.
- Preserve required field names, nesting, header order, and file locations exactly.
- Convert money to integer minor units when requested; avoid floats for currency.
- Include metadata such as source file, input row count, and used row count exactly as specified.
- Validate generated JSON/CSV by re-reading it and checking types, headers, and row counts.
