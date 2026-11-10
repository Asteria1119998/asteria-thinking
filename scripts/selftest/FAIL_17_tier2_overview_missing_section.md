【Asteria思维模型】档位：二档·精简（按建议·不可逆）｜主类型：Data（次：Specification）

```
总图：可以删，但先 dry-run，列表看过再真删
├─ 结构分类：Data 为主，删什么取决于 mtime 可信度
├─ 差距：边界、递归、链接三处取保守默认
├─ 关键决策：dry-run 默认，--yes 才删
└─ 交付：清理脚本
```

## 结构分类
主类型 Data，因为脚本要删的文件集合取决于目录里实际有什么、mtime 是否可信（挂载盘常不可信）；次类型 Specification：7 天的边界含不含当天未说明。
## 差距
意图是清理旧日志而不误删；规格缺：边界含不含第 7 天、是否递归、符号链接怎么办。默认：不含当天、不递归、跳过链接。
## 关键决策与失败点
- 先 dry-run 列出将删文件，再加 --yes 才真删
- 失败点：mtime 不可信导致误删新文件；失败点：目录不存在时静默退出
## 假设 / 检验 / 修正
假设：mtime 可信。检验：对三份人造文件设不同 mtime 跑 dry-run，核对列表。若列表错，修正为按文件名日期解析。

```python
import csv
rows = list(csv.DictReader(open("data.csv")))
rows.sort(key=lambda r: r["date"])
print(len(rows))
```
