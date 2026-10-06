# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Lê Nguyễn Thái Dương | 2A202602383 | Cài đặt harness Deep Agents, subagents, runner, curator, cấu hình NVIDIA và báo cáo |

- Mô hình: NVIDIA NIM `deepseek-ai/deepseek-v4.1-flash`; nhiệt độ `LAB_TEMPERATURE=0`; `recursion_limit` mặc định của runner: 60.
- Phiên bản Deep Agents: 0.7.21; hệ điều hành: Windows 11; chạy trực tiếp trong `.venv`.
- Số lần chạy tác vụ đã dùng / ngân sách: chưa chạy tác vụ thật bằng LLM; mới chạy test offline không tốn token.
- Commit của tag `freeze`: chưa tạo tag `freeze`.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Dự đoán `subagents` có thể cao hơn `baseline` trên tác vụ đánh giá nếu tác tử chính giao việc đúng cho `explorer`/`implementer`/`reviewer`, vì việc tách vai trò giúp đọc đề, sửa và kiểm tra độc lập hơn. Tuy nhiên lợi ích có thể nhỏ hoặc âm nếu tác tử không gọi subagent, giao việc thiếu ngữ cảnh, hoặc chi phí token tăng mà không cải thiện check.
- H2 (skills-auto so với baseline): Dự đoán `skills-auto` có cơ hội cải thiện các lỗi quy trình lặp lại so với `baseline`, nhất là lỗi đọc thiếu quy ước, làm sạch dữ liệu/log hoặc kiểm tra đầu ra trước khi kết thúc. Rủi ro chính là skill tự sinh quá khớp tác vụ học hoặc không được đọc (`skills_read = 0`), nên trên tác vụ đánh giá có thể không vượt baseline.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm trên tác vụ học sẽ cao hơn tác vụ đánh giá, vì tác vụ học cung cấp feedback/trace để sinh skill và thiết kế subagent, còn tác vụ đánh giá có dữ liệu mới và thêm quy ước mới. Nếu chênh lệch lớn giữa học và đánh giá, đó là dấu hiệu nhiễu, quá khớp hoặc skill chưa tổng quát.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Bài lab dùng một tác tử chính Deep Agents làm bộ điều phối. Ở chế độ `single`/`baseline`, tác tử chính vẫn có thể gọi subagent mặc định `general-purpose` qua công cụ `task`; subagent này dùng cho câu hỏi phức tạp, tìm kiếm tệp/nội dung và tác vụ nhiều bước. Ở chế độ `subagents`, bài lab yêu cầu định nghĩa thêm 2 đến 3 subagent trong `src/lab/subagents.py` (ví dụ theo guide: `explorer` để đọc tài liệu/dữ liệu và báo cáo sự thật, `implementer` để sửa/chạy kiểm tra, `reviewer` để kiểm tra độc lập kết quả).
2. Tác tử chính giao việc cho worker/subagent bằng công cụ `task`. Khi gọi `task`, tác tử chính gửi `description` và `subagent_type`; mỗi lần gọi là một phiên làm việc tạm thời, mặc định không giữ trạng thái trước đó, chỉ thấy nội dung prompt được gửi và trả về một báo cáo cuối. Vì vậy prompt giao việc phải chứa đủ quy tắc, đường dẫn và yêu cầu đầu ra.
3. Các công cụ mặc định thấy được khi chạy `scripts/tour.py`: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `general-purpose` có cùng công cụ với tác tử chính. Nhóm công cụ tệp dùng để đọc/ghi/sửa/tìm kiếm trong sandbox; `execute` chạy lệnh shell cô lập; `task` dùng để gọi subagent. System prompt mặc định của Deep Agents là rỗng; repo bổ sung `BASE_PROMPT`, `SUBAGENTS_NOTE` và `SKILLS_NOTE` trong `src/lab/agent.py`.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| Chưa có dữ liệu | Chưa chạy `python -m lab.runner --condition baseline --tasks learn` | - | Hiện `results/` chưa có `run.json` thật |

Nhận xét: chưa thể phân loại lỗi vì chưa có kết quả baseline trên tác vụ học. Sau khi chạy baseline, mục này cần lấy các check `passed=false` trong `results/baseline/*/run.json`.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa:
  - `explorer`: đọc instruction, README, docstring, sample data/log/test và báo cáo sự thật; không sửa file. Vai trò này giảm rủi ro bỏ sót quy ước.
  - `implementer`: thực hiện thay đổi, chạy lệnh/test liên quan và báo cáo file đã đổi. Vai trò này tách phần sửa khỏi phần khảo sát.
  - `reviewer`: kiểm tra độc lập kết quả với đề bài, edge case và yêu cầu output; không sửa file. Vai trò này giúp bắt lỗi trước khi tác tử chính kết thúc.
- `subagent_calls` ở từng tác vụ và nhận xét: chưa có dữ liệu vì chưa chạy điều kiện `subagents` trên tác vụ học/đánh giá thật.
- Thông tin thiếu hoặc thừa khi giao việc: chưa có trace thật để đánh giá. Thiết kế hiện tại nhắc tác tử chính phải đưa đủ quy tắc và đường dẫn vì subagent chỉ thấy prompt được giao.
- Ảnh hưởng đến token và thời gian: chưa đo bằng LLM thật. Kỳ vọng token cao hơn baseline vì mỗi subagent là thêm lời gọi mô hình.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: chưa chạy curator thật; `skills/auto/` hiện chỉ có README/.gitkeep, chưa có skill tự sinh.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| Chưa có skill | - | - | - |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
Chưa có bảng so sánh vì chưa chạy các điều kiện thật bằng LLM.
Test offline hiện tại: `pytest -q` đạt 29/29.

Khi có dữ liệu, tạo bảng bằng:
python -m lab.compare > report/table.md
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. Chỉ mới kiểm thử offline bằng mô hình giả (`ScriptedChatModel`), chưa chạy LLM thật trên 6 tác vụ. Vì vậy kết luận hiện tại chỉ xác nhận code harness đúng hợp đồng test, chưa chứng minh hiệu quả agent trên tác vụ thật.
2. Chưa có dữ liệu `results/` cho baseline, subagents và skills-auto. Các nhận định về điểm, token, `subagent_calls`, `skills_read` và overfitting phải chờ sau khi chạy `lab.runner` và `lab.curator`.
3. Mỗi điều kiện trong thiết kế lab thường chỉ chạy một lần trên số tác vụ nhỏ, nên kết quả thật có thể nhiễu do mô hình và không đủ để khẳng định khác biệt nhỏ là có ý nghĩa thống kê.
4. Chạy trên Windows trong khi README khuyến nghị macOS/Linux/WSL vì shell của agent dùng lệnh kiểu Unix. Code đã bổ sung Git Unix tools vào PATH để test offline qua được, nhưng chạy thật vẫn nên theo dõi lỗi shell/path trong trace.
5. Cấu hình hiện dùng một model NVIDIA duy nhất. Kết luận nếu có sẽ phụ thuộc model, khả năng tool-calling và giới hạn API của provider.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

Đã hoàn thiện phần code offline của lab: backend, agent builder, subagents, runner, curator và cấu hình NVIDIA; toàn bộ test offline đạt 29/29. Chưa thể kết luận điều kiện nào tốt hơn vì chưa chạy benchmark thật bằng LLM và chưa có `results/run.json`. Bước tiếp theo là chạy baseline/subagents trên tác vụ học, chạy curator để sinh skill, commit giả thuyết trước `freeze`, rồi chạy đánh giá chính thức và điền mục 4, 6, 7, 8 bằng số liệu thật.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  - `.\.venv\Scripts\python.exe -m pytest tests/test_01_provided.py -q` -> 12 passed
  - `.\.venv\Scripts\python.exe scripts\tour.py` -> liệt kê tools mặc định: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`
  - `.\.venv\Scripts\python.exe -m pytest tests/test_02_agent.py -q` -> 9 passed
  - `.\.venv\Scripts\python.exe -m pytest tests/test_03_runner.py -q` -> 6 passed
  - `.\.venv\Scripts\python.exe -m pytest tests/test_04_curator.py -q` -> 2 passed
  - `.\.venv\Scripts\python.exe -m pytest -q` -> 29 passed
- Thử thách mở rộng (nếu có): chưa chọn.
- Ghi chú khác: `.env` nằm trong `.gitignore`; không commit khóa API. NVIDIA được cấu hình qua `NVIDIA_API_KEY`, `NVIDIA_MODEL`, `NVIDIA_BASE_URL`, `NVIDIA_TOP_P`, `NVIDIA_MAX_TOKENS`.
