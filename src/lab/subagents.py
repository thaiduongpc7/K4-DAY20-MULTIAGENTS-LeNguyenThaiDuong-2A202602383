"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use this subagent to inspect task instructions, README files, docstrings, "
                "schemas, sample data, logs, and tests, then report facts without editing files."
            ),
            "system_prompt": (
                "You are an explorer subagent. Read the relevant files carefully and return "
                "a concise factual report with important paths, constraints, and likely failure causes. "
                "Do not modify files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use this subagent when code, data files, or generated outputs must be changed, "
                "and when commands or tests should be run to verify the change."
            ),
            "system_prompt": (
                "You are an implementer subagent. Make focused changes needed for the delegated task, "
                "run the relevant checks when possible, and report exactly what changed and what passed."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use this subagent to independently check an attempted solution against the task rules, "
                "edge cases, tests, and output file requirements before relying on it."
            ),
            "system_prompt": (
                "You are a reviewer subagent. Verify the result against the instructions and tests. "
                "Look for missing files, rule violations, edge cases, and unsupported claims. "
                "Do not modify files."
            ),
        },
    ]
