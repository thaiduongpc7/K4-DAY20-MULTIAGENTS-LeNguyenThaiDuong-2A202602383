### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: task
{"subagent_type": "explorer", "description": "Inspect the repository under workspace/, especially bookings source files, README/docs, and tests (do not modify anything). Identify failing behavior, docstring requirements, likely hidden edge cases, and report exact files/functions needing fixes. Do not edit tests."}

### Tool result
Inspection report for `workspace/`:

## Test/run observations

- Command from docs: `cd workspace && python -m pytest tests -q`
  - Initially failed before collecting tests due to local pytest plugin/`anyio` environment issue importing `asyncio` / `_overlapped`.
- Re-ran with plugin autoload disabled:
  - `cd workspace && set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1&& python -m pytest tests -q`
  - Result: `2 failed, 1 passed`.

Current visible failures:

1. `tests/test_bookings.py::test_total_minutes_mixed_formats`
   - Calls `total_minutes(["1h30m", "2h"])`
   - Fails because `bookings/timeutil.py::parse_duration("2h")` raises `ValueError`.
   - Expected total: `210`.

2. `tests/test_bookings.py::test_billable_blocks_rounds_up`
   - Calls `billable_blocks(20)`
   - Actual: `1`
   - Expected: `2`.
   - Cause: `round(minutes / block)` uses Python bankers/nearest rounding, not ceiling.

3. `tests/test_bookings.py::test_add_slot_single_call`
   - Currently passes for a single call only.

## Files/functions needing fixes

### `workspace/bookings/timeutil.py`

Function: `parse_duration(text)`

Docstring requirements say it must support:

- `"1h30m" -> 90`
- `"2h" -> 120`
- `"45m" -> 45`
- `"1:30" -> 90`
- `"45" -> 45`
- Surrounding whitespace ignored.

Current implementation only supports exactly:

```python
r"(\d+)h(\d+)m"
```

So it fails for all documented formats except compact hours+minutes like `"1h30m"`.

Likely hidden edge cases:
- Whitespace: `" 2h "`, `" 45m\n"` should work per

### Tool call: ls
{"path": "workspace"}

### Tool call: ls
{"path": "workspace/bookings"}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py"}

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

### Tool result
['/workspace/.pytest_cache/', '/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: task
{"subagent_type": "implementer", "description": "Modify only source files under workspace/bookings (never workspace/tests) to satisfy all docstrings and hidden edge cases. Required: in workspace/bookings/timeutil.py implement parse_duration supporting surrounding whitespace and exactly documented formats: digits+h+digits+m, digits+h, digits+m, H:MM, bare digits; reject malformed inputs with ValueError. In workspace/bookings/billing.py implement billable_blocks with partial blocks always ceiling, minutes >=0 else ValueError; validate block sensibly (must be positive) and preserve numeric behavior. In workspace/bookings/schedule.py fix mutable default and ensure add_slot returns a NEW list without mutating caller input; separate default calls independent. Inspect files first, edit them, run tests from sandbox root using relative paths (pytest with plugin autoload disabled if needed), and report files changed and test results."}

### Tool result
Implemented requested changes under `workspace/bookings` only.

Files changed:
- `workspace/bookings/timeutil.py`
  - Implemented `parse_duration` for documented formats:
    - `digits+h+digits+m`
    - `digits+h`
    - `digits+m`
    - `H:MM`
    - bare digits
  - Surrounding whitespace is ignored.
  - Malformed inputs raise `ValueError`.

- `workspace/bookings/billing.py`
  - Implemented ceiling behavior for partial billing blocks.
  - Added validation:
    - `minutes < 0` raises `ValueError`
    - `block <= 0` raises `ValueError`
  - Preserves numeric behavior using floor-division ceiling logic.

- `workspace/bookings/schedule.py`
  - Removed mutable default argument.
  - `add_slot` now returns a new list and does not mutate caller input.
  - Independent default calls no longer share state.

Test results:
- Initial command failed due to Windows shell environment syntax:
  - `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest workspace/tests`
- Second command needed `PYTHONPATH`:
  - `set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1&& set PYTHONPATH=workspace&& pytest workspace/tests`
  - Result: `3 passed in 0.03s`

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool call: task
{"subagent_type": "reviewer", "description": "Review the current source changes in workspace/bookings against every docstring and likely hidden tests. Do not edit files. Inspect timeutil.py, billing.py, schedule.py, calendar_export.py and tests. Report any defects, especially type/validation/format edge cases and Acme Python conventions."}

### Tool result
@@ lines 1-28 of 28 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    stripped = text.strip()
    patterns = (
        (r"(\d+)h(\d+)m", lambda m: int(m.group(1)) * 60 + int(m.group(2))),
        (r"(\d+)h", lambda m: int(m.group(1)) * 60),
        (r"(\d+)m", lambda m: int(m.group(1))),
        (r"(\d+):(\d{2})", lambda m: int(m.group(1)) * 60 + int(m.group(2))),
        (r"(\d+)", lambda m: int(m.group(1))),
    )
    for pattern, converter in patterns:
        m = re.fullmatch(pattern, stripped)
        if m:
            return converter(m)
    raise ValueError(f"bad duration: {text!r}")

### Tool result
@@ lines 1-15 of 15 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    if minutes < 0:
        raise ValueError("minutes must be >= 0")
    if block <= 0:
        raise ValueError("block must be positive")
    return -(-minutes // block)

### Tool result
@@ lines 1-18 of 18 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=None):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    if slots is None:
        slots = []
    return [*slots, slot]

### Tool result
Review completed for `workspace/bookings` and `workspace/tests`. I did not edit files.

## Test status

- Running `cd workspace && python -m pytest tests -q` failed due to the local environment loading an external `anyio` pytest plugin and hitting a Windows `_overlapped`/asyncio initialization error.
- Re-running with plugin autoload disabled passed:

```text
cd workspace && set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1&& python -m pytest tests -q
...
3 passed in 0.01s
```

## Files inspected

- `workspace/bookings/timeutil.py`
- `workspace/bookings/billing.py`
- `workspace/bookings/schedule.py`
- `workspace/bookings/calendar_export.py`
- `workspace/bookings/__init__.py`
- `workspace/tests/test_bookings.py`
- `workspace/README.md`
- `workspace/CHANGELOG.md`

## Findings

### 1. `parse_duration()` lacks type validation for non-strings

Location: `workspace/bookings/timeutil.py`

```python
stripped = text.strip()
```

The docstring says it converts a duration string. Current behavior for non-string inputs is whatever `.strip()` does or an `AttributeError` if absent:

```python
parse_duration(None)  # AttributeError
parse_duration(123)   # AttributeError
```

Hidden tests may expect a consistent `ValueError` for invalid duration input, especially because malformed strings raise `ValueError`. If Acme conventions require explicit validation and predictable exception types, this is a likely defect.

### 2. `parse_duration()` accepts zero and semantically questionable durations

Current impl

### Tool call: execute
{"command": "set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1&& set PYTHONPATH=workspace&& python -m pytest workspace/tests -q", "timeout": 120}

### Tool call: execute
{"command": "git -C workspace diff -- bookings tests", "timeout": 120}

### Tool result
...                                                                      [100%]
3 passed in 0.01s

[Command succeeded with exit code 0]

### Tool result
diff --git a/bookings/__init__.py b/bookings/__init__.py
deleted file mode 100644
index daa50c7..0000000
--- a/bookings/__init__.py
+++ /dev/null
@@ -1 +0,0 @@
-__version__ = "1.4.2"
diff --git a/bookings/__pycache__/__init__.cpython-312.pyc b/bookings/__pycache__/__init__.cpython-312.pyc
deleted file mode 100644
index 567e9a3..0000000
Binary files a/bookings/__pycache__/__init__.cpython-312.pyc and /dev/null differ
diff --git a/bookings/__pycache__/billing.cpython-312.pyc b/bookings/__pycache__/billing.cpython-312.pyc
deleted file mode 100644
index f276cad..0000000
Binary files a/bookings/__pycache__/billing.cpython-312.pyc and /dev/null differ
diff --git a/bookings/__pycache__/calendar_export.cpython-312.pyc b/bookings/__pycache__/calendar_export.cpython-312.pyc
deleted file mode 100644
index 5a7fcad..0000000
Binary files a/bookings/__pycache__/calendar_export.cpython-312.pyc and /dev/null differ
diff --git a/bookings/__pycache__/schedule.cpython-312.pyc b/bookings/__pycache__/schedule.cpython-312.pyc
deleted file mode 100644
index 4d04e99..0000000
Binary files a/bookings/__pycache__/schedule.cpython-312.pyc and /dev/null differ
diff --git a/tests/__pycache__/test_bookings.cpython-312-pytest-9.1.1.pyc b/tests/__pycache__/test_bookings.cpython-312-pytest-9.1.1.pyc
new file mode 100644
index 0000000..15960cd
Binary files /dev/null and b/tests/__pycache__/test_bookings.cpython-312-pytest-9.1.1.pyc differ
diff --git a/bookings/__pycache__/timeutil.cpython-312.pyc b/bookings/__p

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py"}

### Tool call: execute
{"command": "set PYTHONPATH=workspace&& python -c \"from bookings.timeutil import parse_duration; from bookings.billing import billable_blocks; from bookings.schedule import add_slot; assert [parse_duration(x) for x in ['1h30m','2h','45m','1:30','45',' 2h ']] == [90,120,45,90,45,120]; assert billable_blocks(0)==0 and billable_blocks(16)==2 and billable_blocks(30)==2; a=add_slot('a'); b=add_slot('b'); assert a==['a'] and b==['b']; base=['x']; out=add_slot('y',base); assert out==['x','y'] and base==['x']; print('custom checks passed')\"", "timeout": 120}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
custom checks passed

[Command succeeded with exit code 0]

### Tool call: task
{"subagent_type": "implementer", "description": "Re-check current workspace/bookings implementation for numeric edge cases strictly implied by docstrings. In particular assess whether billing's -(-minutes // block) is correct for allowed numeric inputs and whether math.ceil is preferable. If a source change is warranted, make it (do not touch tests), then run the visible tests and a few targeted checks. Otherwise leave files unchanged and report why."}

### Tool result
No source changes were made.

What I checked:
- `workspace/bookings/billing.py`
- Other booking helpers/docstrings in `workspace/bookings/`
- Visible tests in `workspace/tests/test_bookings.py`

Assessment:
- The `billable_blocks(minutes, block=15)` docstring says:
  - partial blocks are billed as full blocks
  - `minutes` must be `>= 0`
  - negative `minutes` raises `ValueError`
- It does not explicitly constrain inputs to `int`, but examples and package duration parsing are whole-minute/integer-oriented.
- For integer numeric inputs, `-(-minutes // block)` is the correct ceiling-division idiom and is preferable to `math.ceil(minutes / block)` because it avoids float conversion/precision loss.

Targeted edge case finding:
- For very large integers, `math.ceil(minutes / block)` can be wrong due to float rounding:
  - `minutes = 10**30`, `block = 15`
  - current implementation returns the exact integer result:
    - `66666666666666666666666666667`
  - `math.ceil(minutes / block)` returns an imprecise result:
    - `66666666666666666819495919616`
- This supports keeping the current implementation.

Checks run:
- `cd workspace && python -m pytest tests -q`
  - Did not complete due to environment failure importing `asyncio` through an installed pytest plugin/anyio:
    - `OSError: [WinError 10106] The requested service provider could not be loaded or initialized`
- Targeted billing checks:
  - `billable_blocks(0, 15) == 0`
  - `billable_blocks(1, 15) == 1`
  - `billable_blocks(15

### Assistant
Updated the bookings source code:

- `workspace/bookings/timeutil.py`: Added support for all documented duration formats, including hours-only, minutes-only, `H:MM`, bare minutes, and surrounding whitespace.
- `workspace/bookings/billing.py`: Implemented correct ceiling-based billing and validation for negative minutes and invalid block sizes.
- `workspace/bookings/schedule.py`: Removed the mutable default argument and ensured `add_slot` returns a new list without mutating input state.

All visible tests pass: **3 passed**.