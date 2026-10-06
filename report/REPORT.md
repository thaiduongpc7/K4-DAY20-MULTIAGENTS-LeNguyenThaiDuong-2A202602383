# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Lê Nguyễn Thái Dương | 2A202602383 | Cài đặt harness Deep Agents, subagents, runner, curator, cấu hình ModelAPI và báo cáo |

- Mô hình: ModelAPI `gpt-6.1-sol`; `LAB_TEMPERATURE=0`; `recursion_limit` mặc định của runner: 60.
- Phiên bản Deep Agents: 0.7.21; hệ điều hành: Windows 11; chạy trực tiếp trong `.venv`.
- Số lần chạy tác vụ đã dùng: 18 run chính/ghi nhận trong `results/` gồm `baseline`, `subagents`, `skills-auto`, cộng 3 run phát triển skill trong `results/skills-auto-dev`.
- Commit của tag `freeze`: `55db279`. Kiểm tra đóng băng: `PYTHONUTF8=1 python scripts/verify_freeze.py` -> `checked 6 runs of skill conditions: OK`.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán `subagents` có thể cao hơn `baseline` trên tác vụ đánh giá nếu tác tử chính giao việc đúng cho `explorer`/`implementer`/`reviewer`, vì việc tách vai trò giúp đọc đề, sửa và kiểm tra độc lập hơn. Tuy nhiên lợi ích có thể nhỏ hoặc âm nếu tác tử không gọi subagent, giao việc thiếu ngữ cảnh, hoặc chi phí token tăng mà không cải thiện check.
- H2 (skills-auto so với baseline): Dự đoán `skills-auto` có cơ hội cải thiện các lỗi quy trình lặp lại so với `baseline`, nhất là lỗi đọc thiếu quy ước, làm sạch dữ liệu/log hoặc kiểm tra đầu ra trước khi kết thúc. Rủi ro chính là skill tự sinh quá khớp tác vụ học hoặc không được đọc (`skills_read = 0`), nên trên tác vụ đánh giá có thể không vượt baseline.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm trên tác vụ học sẽ cao hơn tác vụ đánh giá, vì tác vụ học cung cấp feedback/trace để sinh skill và thiết kế subagent, còn tác vụ đánh giá có dữ liệu mới và thêm quy ước mới. Nếu chênh lệch lớn giữa học và đánh giá, đó là dấu hiệu nhiễu, quá khớp hoặc skill chưa tổng quát.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Công cụ `execute` cho phép chạy lệnh shell trong sandbox.
2. Công cụ `task` khởi chạy một subagent tạm thời. Subagent mặc định `general-purpose` dùng cho câu hỏi/tác vụ phức tạp, tìm file/nội dung và làm việc nhiều bước; nó có cùng bộ công cụ với tác tử chính nhưng mỗi lần gọi mặc định chỉ thấy prompt được giao và trả về một báo cáo cuối.
3. System prompt mặc định của Deep Agents rỗng. Mô tả `task` yêu cầu đưa đủ chi tiết trong prompt vì subagent chỉ thấy nội dung được gửi; mô tả `execute` nhắc dùng công cụ tìm kiếm file như `grep`/`glob` thay vì tự chạy `find`/`grep` trong shell.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Chỉ dùng tác vụ học của `baseline`. Lỗi hạ tầng API timeout ở `logs-learn` không được dùng làm bằng chứng lỗi tác tử theo `GLOSSARY.md`.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | A. Bỏ qua đặc tả | `detail`: original files in `tests/` must not be modified |
| `code-learn` | `rule_type_hints` | E. Vi phạm quy ước tổ chức | `RULE: every public function ... has type annotations ... return value` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function per bug ...` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under '## Unreleased' ...` |
| `data-learn` | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents ...` |
| `data-learn` | `rule_meta_block` | E | `RULE: answer.json has an object meta = ...` |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents ...` |

Nhận xét: nhóm E chiếm đa số trong các lỗi có phản hồi thật: 6/7 dòng ở bảng trên là quy ước tổ chức. `check_breakdown.py` cũng cho thấy baseline trên tác vụ học đạt 11/18 check kỹ thuật nhưng 0/9 house-rule checks. Một skill có thể phòng ngừa nhóm này nếu nó nhắc tác tử tìm và thực thi các artifact/quy ước ẩn như type hints, changelog, meta block, tiền cent và clean CSV.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa:
  - `explorer`: đọc instruction, README, docstring, sample data/log/test và báo cáo sự thật; không sửa file.
  - `implementer`: thực hiện thay đổi, chạy lệnh/test liên quan và báo cáo file đã đổi.
  - `reviewer`: kiểm tra độc lập kết quả với đề bài, edge case và yêu cầu output; không sửa file.
- `subagent_calls`: `code-eval=4`, `data-learn=1`, `logs-eval=1`; các run còn lại bằng 0 do timeout hoặc tác tử chính không giao việc.
- Vết cho thấy khi có giao việc, prompt thường đủ đường dẫn và quy tắc chính. Ví dụ `data-learn` giao cho `implementer` với đường dẫn `workspace/sales.csv`, `workspace/answer.json`, yêu cầu dùng đường dẫn tương đối, loại trùng, tính doanh thu Q1 North và ghi `answer.json`.
- Ảnh hưởng token/thời gian: trung bình token/run của `subagents` là 92,751, cao hơn `baseline` 74,375 nhưng điểm eval thấp hơn (0.38 so với 0.57). `subagents` không đáng chi phí trong lần chạy này; riêng `code-eval` dùng 240,674 token nhưng vẫn 6/11 như baseline.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Chạy curator 1 lần, không xóa skill nào. Curator sinh 3 skill hợp lệ, `validate_skill` trả `[]` cho cả ba.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai | Độ dài, `description` và `skills_read` |
|---|---|---|---|
| `code-repair-task-compliance` | Tổng quát cho tác vụ sửa Python có quy tắc chất lượng/bookkeeping | Đúng; nhắc không sửa test gốc, thêm type hints, regression tests, changelog, chạy test | 6 dòng thân; description đúng tình huống. Được đọc ở `code-learn` (`skills_read=1`), không đọc ở `code-eval` do timeout trước khi gọi tool |
| `data-artifact-contracts` | Tổng quát cho task data cần artifact/schema/unit/meta | Đúng; nhắc liệt kê artifact, giữ schema, tiền cent, meta, validate JSON/CSV | 6 dòng thân; description rõ. Được đọc ở `data-learn`, `data-eval`, `logs-learn`, `logs-eval` |
| `reproducible-cleaning-pipeline` | Tổng quát cho cleaning CSV/log có dedupe, timestamp, label, sort | Đúng; không chứa dữ liệu eval; hướng dẫn lập pipeline tái lập | 6 dòng thân; description đúng nhưng hơi rộng nên kích hoạt cả data và logs. Được đọc cùng `data-artifact-contracts` trong các task data/log |

Ở Phần 3.4 (`results/skills-auto-dev`), cùng bộ skill đạt `code-learn=7/10`, `data-learn=5/8`, `logs-learn=6/9`. Sau đóng băng, kết quả học là giống hệt về điểm: `7/10`, `5/8`, `6/9`.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Nội dung `report/table.md`:

```text
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 7/10 |
| data-learn | 5/8 | 5/8 | 5/8 |
| logs-learn | 0/9 | 0/9 | 6/9 |
| code-eval | 6/11 | 6/11 | 0/11 |
| data-eval | 5/9 | 0/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 6/10 |
| **Mean score - learning tasks** | 0.41 | 0.41 | 0.66 |
| **Mean score - evaluation tasks** | 0.57 | 0.38 | 0.39 |
| **Mean tokens per run** | 74,375 | 92,751 | 87,282 |
| **Runs that read a skill** | 0/6 | 0/6 | 5/6 |
```

Kết quả `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     17/18         0/12          84,623      0/3
baseline      learn    11/18         0/9           64,127      0/3
subagents     eval     12/18         0/12         112,510      0/3
subagents     learn    11/18         0/9           72,993      0/3
skills-auto   eval     11/18         0/12          69,062      2/3
skills-auto   learn    17/18         1/9          105,502      3/3
```

Các run có `error`: `baseline/logs-learn`, `subagents/code-learn`, `subagents/data-eval`, `subagents/logs-learn`, `skills-auto/code-eval` đều gặp `OpenAITimeoutError: Request timed out`. Không có run `skills-auto` nào có `skills_modified=true`. Freeze check OK với 6 run skill conditions.

## 8. Phân tích

1. Trên tác vụ học, `skills-auto` cải thiện rõ so với `baseline`: mean score 0.66 so với 0.41. Cải thiện chính đến từ `logs-learn` 0/9 -> 6/9 và `code-learn` 6/10 -> 7/10. Trên tác vụ đánh giá, không có cải thiện: `baseline` cao nhất với mean 0.57; `skills-auto` chỉ 0.39 và `subagents` 0.38. Đây là dấu hiệu skill học được giúp tập học nhưng không tổng quát ổn định sang tập đánh giá, cộng thêm nhiễu do timeout ở `skills-auto/code-eval`.
2. Tách check cho thấy baseline eval đã đạt 17/18 check kỹ thuật nhưng 0/12 house rules. `skills-auto` học đạt 17/18 kỹ thuật và 1/9 house rules, tức skill giúp kỹ thuật/artifact trên tập học nhiều hơn quy ước tổ chức. Trên eval, `skills-auto` chỉ đạt 11/18 kỹ thuật và 0/12 house rules; check quy ước mới của eval không được skill giúp.
3. Một check skill giúp: `logs-learn` từ 0/9 lên 6/9; trace ghi tác tử đọc `data-artifact-contracts` và `reproducible-cleaning-pipeline`, rồi tạo `workspace/errors.json` và script tái lập `workspace/generate_errors.py`, đúng tinh thần skill pipeline. Một check skill không giúp: `code-eval` đạt 0/11 vì timeout trước khi đọc skill (`skills_read=0`, `tool_calls=0`), nên không có cơ chế áp dụng `code-repair-task-compliance`.
4. Chi phí: `baseline` rẻ nhất trung bình 74,375 token/run và có điểm eval cao nhất 0.57. `subagents` đắt nhất 92,751 token/run nhưng eval thấp hơn baseline; đa tác tử không đáng chi phí trong lần chạy này. `skills-auto` dùng 87,282 token/run, giúp learn nhưng không giúp eval; hiệu quả điểm/token trên eval kém baseline.
5. Không thấy dấu hiệu rò rỉ dữ liệu trong skill: tên và nội dung skill không chứa marker eval, `validate_skill` hợp lệ, `verify_freeze.py` OK. Dấu hiệu quá khớp có: skill cải thiện learn (0.41 -> 0.66) nhưng không cải thiện eval (0.57 -> 0.39).
6. Nhiễu: điểm learn của cùng bộ skill ở Phần 3.4 và sau đóng băng không đổi (`code=7/10`, `data=5/8`, `logs=6/9`), chênh lệch 0 trong lần đo này. Tuy nhiên các timeout ở nhiều điều kiện cho thấy độ tin cậy của chênh lệch nhỏ thấp; kết luận nên dựa vào khác biệt lớn và có trace hỗ trợ.

## 9. Hạn chế và tính hợp lệ

1. Chỉ có 3 task học và 3 task eval, mỗi điều kiện chạy một lần, nên kết quả dễ nhiễu và không đủ để khẳng định khác biệt nhỏ có ý nghĩa thống kê.
2. Nhiều run bị `OpenAITimeoutError`; đây là lỗi hạ tầng/API, làm giảm điểm một số task và có thể che khuất năng lực thật của tác tử.
3. Model duy nhất là ModelAPI `gpt-6.1-sol`; kết luận phụ thuộc khả năng tool-calling, tốc độ và timeout của provider này.
4. Chạy trên Windows trong khi README khuyến nghị macOS/Linux/WSL vì shell của tác tử dùng lệnh Unix. Code đã thêm Git Unix tools vào PATH, nhưng vẫn có rủi ro khác biệt shell/path so với môi trường chuẩn.
5. Skill do curator tự sinh có thể hợp lệ về định dạng nhưng vẫn quá rộng hoặc quá khớp. Kết quả eval cho thấy lợi ích trên learn không chuyển ổn định sang task mới.

## 10. Kết luận

Đã hoàn thiện harness Deep Agents, subagents, runner, curator, cấu hình ModelAPI và chạy đủ thí nghiệm chính thức. `pytest` đạt 29/29 và `verify_freeze.py` báo OK. Kết quả cho thấy `skills-auto` cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá; `baseline` là điều kiện tốt nhất trên eval trong lần chạy này. Đa tác tử làm tăng chi phí token nhưng không tăng điểm trung bình. Cải tiến tiếp theo nên là chạy lặp nhiều lần hoặc đổi model/tool-calling ổn định hơn để giảm timeout và đo nhiễu.

## Phụ lục

- Lệnh đã chạy:
  - `.\.venv\Scripts\python.exe -m pytest -q` -> 29 passed
  - `.\.venv\Scripts\python.exe scripts\tour.py`
  - `.\.venv\Scripts\python.exe -m lab.runner --condition baseline --tasks learn`
  - `.\.venv\Scripts\python.exe -m lab.runner --condition subagents --tasks learn`
  - `.\.venv\Scripts\python.exe -m lab.curator`
  - `.\.venv\Scripts\python.exe -m lab.runner --condition skills-auto --tasks learn`
  - `Move-Item results\skills-auto results\skills-auto-dev`
  - `git commit -m "hypotheses"`
  - `git commit --allow-empty -m "freeze skills"; git tag freeze`
  - `.\.venv\Scripts\python.exe -m lab.runner --condition baseline --tasks eval`
  - `.\.venv\Scripts\python.exe -m lab.runner --condition subagents --tasks eval`
  - `.\.venv\Scripts\python.exe -m lab.runner --condition skills-auto --tasks all`
  - `.\.venv\Scripts\python.exe -m lab.compare > report\table.md`
  - `$env:PYTHONUTF8='1'; .\.venv\Scripts\python.exe scripts\verify_freeze.py`
  - `.\.venv\Scripts\python.exe scripts\check_breakdown.py`
- Thử thách mở rộng: chưa chọn.
- Ghi chú khác: `.env` nằm trong `.gitignore`; không commit khóa API. `verify_freeze.py` trên Windows cần `PYTHONUTF8=1` để tránh lỗi decode khi đọc commit chứa tiếng Việt.
