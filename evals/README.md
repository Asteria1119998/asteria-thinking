# evals

- `evals.json`、`triggers.json`：v1 原始用例，原样保留。
- `tier*/`：v2 用例文件夹（`claude plugin eval` 可直接读）。每个文件夹：`prompt.md`（运行设置＋用户提示）、`case.yaml`（名称与期望结果）、`graders/`（每条断言一个文件）、`files/`（输入文件，若有）。用例按期望档位命名，用来测刻度是否按四轴收缩／展开。
- `trigger-eval.json`：21 条触发测试（11 应触发 / 10 近似负例），配 skill-creator 的 description 优化循环使用。

运行方式（在 skill 目录的上一级）：`claude plugin eval ./asteria-thinking`。

档位用例的提示末尾带"不用问我选档，直接输出"，对应跳过规则里的"没有用户可问"，横幅来源应写"自动"；`asks-tier-first` 不带这句，用来测定档那一轮。定档那一轮不是正式回复，不跑校验器。

`boundary-code-review` 的代码是贴在对话里的。只看 git diff 或 PR 的审查 skill（例如 Claude Code 自带的 code-review）处理不了这种输入，按规则不转交，用例照常适用；环境里若装了能直接审查贴入代码的 skill，转交才是正确行为，这个用例就不适用。
