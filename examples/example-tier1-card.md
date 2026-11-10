# 示例：一档·结构卡

用户请求：「帮我写个 Python 脚本，把 data.csv 按 date 列升序排序后另存为 sorted.csv。」

四轴：不可逆 0（另存新文件）、影响面 0（单文件）、歧义度 0（排序键唯一，日期格式有合理默认）、盲反馈 0（跑一下就知道）→ 0 分 → 一档。

定档那一轮从略：模型先给出上面的记分和建议，用户回了"按建议"，下面是之后的正式回复。

---

【Asteria思维模型】档位：一档·结构卡（按建议·零分）｜主类型：Specification

结构卡：主类型 Specification（唯一分叉是按字符串还是按日期排，默认按日期解析，非 ISO 格式会报错而不是静默排错）｜最大差距：date 的格式与同日期行的先后未说明｜最可能失败点：非 ISO 日期被当字符串排错｜检验：对 data.csv 跑一次并核对顺序 → 已跑，1-20 / 2-11 / 3-05，正确

```python
import csv
from datetime import date

with open("data.csv", newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fields = reader.fieldnames

rows.sort(key=lambda r: date.fromisoformat(r["date"].strip()))  # 稳定排序，同日期保持原顺序

with open("sorted.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
```

用法：与 data.csv 同目录运行 `python3 sort.py`。日期不是 `YYYY-MM-DD` 时会在出错行报 `ValueError`，告诉我格式我再改。

---

要点：前置只有横幅和一行结构卡；"检验"字段写的是跑过的结果，不是"应该没问题"。
