【Asteria思维模型】档位：二档·精简（不可逆）｜主类型：Data（次：Specification）

## 结构分类
主类型 Data，因为要删的集合取决于目录实际内容与 mtime 可信度。
## 差距
意图是清旧日志不误删；规格缺边界与递归。
## 假设 / 检验 / 修正
假设 mtime 可信。检验：人造文件 dry-run 核对。若错则改按文件名日期。

```python
import csv
rows = list(csv.DictReader(open("data.csv")))
rows.sort(key=lambda r: r["date"])
print(len(rows))
```
