【Asteria思维模型】档位：一档·结构卡（按建议·零分）｜主类型：Specification

结构卡：主类型 Specification（字符串排序 vs 日期排序有分叉，默认按日期解析）｜最大差距：date 格式未说明｜最可能失败点：非 ISO 日期静默排错｜检验：对 fixture 跑一次并核对顺序 → 已跑，顺序正确

```python
import csv
rows = list(csv.DictReader(open("data.csv")))
rows.sort(key=lambda r: r["date"])
print(len(rows))
```
