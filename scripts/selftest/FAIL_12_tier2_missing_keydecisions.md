【Asteria思维模型】档位：二档·精简（按建议·不可逆）｜主类型：Data（次：Specification）

```
总图：可以删，但先 dry-run，列表看过再真删
├─ 结构分类：Data 为主，删什么取决于 mtime 可信度
├─ 差距：边界、递归、链接三处取保守默认
├─ 关键决策：dry-run 默认，--yes 才删
├─ 假设/检验：人造 mtime 文件跑过，列表正确
└─ 交付：清理脚本
```

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
