# evals

- `evals.json`、`triggers.json`：v1 原始用例，原样保留。
- `tier*/`：v2 用例文件夹（`claude plugin eval` 可直接读）。每个文件夹：`prompt.md`（运行设置＋用户提示）、`case.yaml`（名称与期望结果）、`graders/`（每条断言一个文件）、`files/`（输入文件，若有）。用例按期望档位命名，用来测刻度是否按四轴收缩／展开。
- `trigger-eval.json`：20 条触发测试（10 应触发 / 10 近似负例），配 skill-creator 的 description 优化循环使用。

运行方式（在 skill 目录的上一级）：`claude plugin eval ./asteria-thinking`。
