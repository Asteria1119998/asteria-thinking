# 示例：二档·精简

用户请求：「写个脚本把 logs/ 目录下 7 天前的 .log 文件删掉。」

四轴：不可逆 1（删除）、影响面 0（只动 logs/）、歧义度 0（"7 天前"有合理默认：mtime 早于 now-7d；不递归）、盲反馈 0（dry-run 可见）→ 1 分 → 二档。

定档那一轮从略：模型先给出上面的记分和建议，用户回了"按建议"，下面是之后的正式回复。

---

【Asteria思维模型】档位：二档·精简（按建议·不可逆）｜主类型：Data（次：Specification）

```
总图：可以删，但默认只列不删，看过列表加 --yes 才真删
├─ 结构分类：Data 为主，删什么取决于 mtime 可不可信
├─ 差距：边界、递归、符号链接三处没说，各取保守默认
├─ 关键决策：dry-run 默认；只匹配 *.log；不递归
├─ 假设/检验：人造 1/6/8 天前的文件跑过，列表正确
└─ 交付：清理脚本，两步运行
```

## 结构分类
主类型 Data：要删的集合完全取决于目录里实际有什么、mtime 是否可信（挂载盘和 git checkout 后的 mtime 常不可信）。次类型 Specification：7 天的边界含不含第 7 天、是否递归、符号链接怎么办，都没说——各取保守默认并写明。

## 差距
意图是清掉旧日志而不误删任何还要用的东西；规格缺三处：边界（默认 mtime < now − 7×24h）、递归（默认不递归）、链接（默认跳过）。最会出事的地方：mtime 不可信导致把新日志当旧的删掉。

## 关键决策与失败点
- 决策：默认 dry-run 只打印将删列表，加 `--yes` 才真删——把不可逆操作变成两步
- 决策：只匹配 `*.log`、不递归、跳过符号链接
- 失败点：mtime 不可信 → 误删新文件；发现方式：dry-run 列表里出现今天的文件
- 失败点：logs/ 不存在或为空时静默成功；处理：目录不存在直接报错退出
- 不处理：按文件名里的日期判断（需要时再加）

## 假设 / 检验 / 修正
- 假设：mtime 可信。检验：人造三个 .log 文件用 `touch -d` 设为 1／6／8 天前，外加一个 .txt 和一个符号链接，跑 dry-run，列表应只含 8 天前那个 → 已跑，正确（.txt 与链接被跳过）。若 8 天前的没进列表或 1 天前的进了：改为按文件名日期解析。
- 假设：边界取"严格早于 7×24 小时"符合用户预期。检验：恰好 7 天的文件落在哪边取决于毫秒级的 mtime 与 cutoff 先后，本身就不稳定——所以 dry-run 列表要给用户看一眼；若用户要"第 7 天也删"，把 `--days 7` 改成 6 比改 `<` 为 `<=` 更可预测。

```python
import argparse, os, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--dir", default="logs")
ap.add_argument("--days", type=int, default=7)
ap.add_argument("--yes", action="store_true", help="真的删除；不加只打印将删列表")
a = ap.parse_args()

root = Path(a.dir)
if not root.is_dir():
    sys.exit(f"目录不存在：{root}")
cutoff = time.time() - a.days * 86400
targets = [p for p in root.glob("*.log") if p.is_file() and not p.is_symlink() and p.stat().st_mtime < cutoff]

for p in targets:
    print(("DELETE " if a.yes else "would delete ") + str(p))
    if a.yes:
        p.unlink()
print(f"{len(targets)} 个文件" + ("已删除" if a.yes else "待删除（加 --yes 执行）"))
```

---

要点：删除把档位从一档抬到二档；总图先给结论再给细节；设计与字段图合并成五条"关键决策与失败点"；检验真的跑了。
