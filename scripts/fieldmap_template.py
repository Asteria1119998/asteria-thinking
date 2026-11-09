#!/usr/bin/env python3
"""
输出字段图（Field Map）骨架。
用法:
  python3 fieldmap_template.py            # 三档完整版：## 字段图
  python3 fieldmap_template.py --compact  # 二档合并版：## 关键决策与失败点
"""
import sys

FULL = """## 字段图

### 关键变量 / 状态
-

### 转换（状态如何变、谁触发）
-

### 可能的失败点（每条写"在哪里、怎么表现、怎么发现"）
-

### 关键假设
-

### Sampling / Variance 顾虑
-

### 此方案明确不处理的内容
-
"""

COMPACT = """## 关键决策与失败点
- 决策：<选了什么，为什么>
- 决策：<选了什么，为什么>
- 失败点：<在哪里、怎么表现、怎么发现>
- 失败点：<在哪里、怎么表现、怎么发现>
- 不处理：<明确排除的范围>
"""

if __name__ == "__main__":
    print(COMPACT if "--compact" in sys.argv[1:] else FULL)
