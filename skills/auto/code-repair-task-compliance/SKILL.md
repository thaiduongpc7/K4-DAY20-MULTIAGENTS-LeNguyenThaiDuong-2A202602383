---
name: code-repair-task-compliance
description: Use when fixing bugs in a Python package with explicit quality or bookkeeping rules.
---
- Inspect task rules before editing; treat them as required deliverables, not optional polish.
- Do not modify existing files under `tests/`; add new regression test files only when requested.
- Add type annotations to every public package function, including return types.
- Add one focused regression test per fixed bug in the required test file.
- Update the changelog under the required heading with one bullet per fix, using the requested format.
- Run the full test suite from the correct project root with the package import path configured.
