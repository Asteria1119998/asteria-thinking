【Asteria思维模型】档位：一档·结构卡（零分）｜主类型：Specification

结构卡：主类型 Specification（排序键有分叉）｜最大差距：date 格式未说明｜最可能失败点：静默排错

```python
import csv
rows = list(csv.DictReader(open("data.csv")))
rows.sort(key=lambda r: r["date"])
print(len(rows))
```
