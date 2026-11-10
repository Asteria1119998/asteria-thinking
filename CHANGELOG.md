# Changelog

## 2026-11-10 — v2.3：边界
- 新增"边界"一节：本 skill 做的是阅读级检查，不是工程代码审查。用户要正式审查时：环境里有专门的工程审查 skill、并且它能处理这次的输入就转交，不限 Asteria 系列（在定档之前判断，要转交就不先问档位）；没有就照常定档输出，回复末尾加一句边界提示。明显的问题（如把用户输入直接拼进 SQL）看到了要指出，但不下"没有问题"的结论
- 用户明说想把某个概念学会时：有 asteria-learning 可用就转交，学完回到分析；没有就讲清与当前分析有关的那一块，回复末尾加一句边界提示。只是需要知道概念才能继续时，不转交、不提示
- 边界提示的写法：一句话，照抄，每种每个对话只说一次；工程那条提到 Asteria 系列的工程 skill 单独提供，但不写它的名字；便携版不带这半句（名字、状态与入口只写在 README）；对话里第一次出现时附一行系列地址；写明"调用"的含义与调用不了时的做法
- description：触发范围不变，代码审查请求仍然触发；写明给的是阅读级检查，不是正式的工程审查
- README 新增"它不做什么"与「Asteria 系列」（各 skill 的状态、公开版每月同步一次的规则、抖音主页链接）；portable-core 同步边界
- 一致性修正：示例与自测探针的横幅改为带来源的新格式；横幅规则写明"用户指定时触发轴可省，零分时写零分"；portable-core 首句不再与跳过规则字面冲突；评测提示改为"不用问我选档，直接输出"（对应来源"自动"）；说明定档那一轮不跑校验器；两个示例注明定档那一轮从略
- 评测：新增 boundary-code-review 用例（代码贴在对话里，只看 diff 的审查 skill 不算可转交）；evals/README 的触发测试条数更正为 21；trigger-eval 加一条正式代码审查请求（应触发）

## 2026-11-10 — v2.2：先定档再输出
- 每个新任务的第一轮只输出四轴记分、建议档位和三个选项，由用户选档，问完即停；四轴规则从"定档"改为"给建议"
- 三种跳过：用户已点名档位；同一任务的后续轮次沿用；没有用户可问时按建议输出
- 横幅括号内增加来源：用户指定／按建议／自动
- 反模式新增：不问档位直接输出、问完档位又在同条消息开始分析
- 评测：五个档位用例的提示加"按建议档位直接输出，不用问我"；新增 asks-tier-first 用例
- README：项目内安装的更新方式改为"先删旧文件夹再解压"

## 2026-11-10 — v2.1：总图
- README 安装改为三条路径：Claude Code 一行 clone（可 pull 更新）；claude.ai／Desktop 从 Releases 下载顶层为 `asteria-thinking/` 的 zip；其他平台贴 portable-core。Release v2.1.0 附该 zip
- 二档、三档在横幅之后必须有「总图」：代码块，根节点为整个回复的一句话结论，每个节点为后文一个章节的结论（不是标题），顺序一致；顺延章节标"（顺延）"；只用 `├─ └─ │`，行首对齐，每行 ≤30 汉字宽；后文若推翻总图，在末尾加「总图更正：…」。一档不画（结构卡即总图）
- 校验器：二档、三档缺总图／总图在章节之后／节点少于 2／节点未覆盖该档必需章节／节点只有标题没有结论 → FAIL；行过宽 → WARN；一档出现总图 → WARN
- 自测：原二、三档探针补总图；新增 FAIL_16（无总图）、FAIL_17（总图漏章节）、FAIL_18（节点只有标题）
- 示例：二档示例补总图；README、portable-core 同步
- 未动：其余配图（记分条、分叉图、状态流、判定树）待总图用过再定

## 2026-11-09 — v2：品牌横幅、档位、分流、校验器重写
- skill 标识改名：`deep-structure-thinking` → `asteria-thinking`（SKILL.md name、评测 tags、文档中的文件夹名与 `claude plugin eval` 路径）；方法名 Deep Structure Thinking 与横幅品牌「Asteria思维模型」不变；安装时文件夹须命名为 `asteria-thinking`
- 新增 `scripts/selftest.sh` ＋ `scripts/selftest/`：15 份探针（文件名前缀 PASS_/FAIL_ 为期望结果），改校验器后跑一遍
- 开场横幅（强制第一行）：`【Asteria思维模型】档位：…｜主类型：…`，替代"我已加载…"的寒暄；品牌、档位、主类型一行声明，用户一个词可改档
- 档位（刻度）：四轴（不可逆／影响面／歧义度／盲反馈）定档；一档·结构卡（一行）／二档·精简（四节带行数上限，设计＋字段图合并为"关键决策与失败点"）／三档·完整（八节）；澄清协议归三档
- 分类分流：每个结构类型附"分类后额外必做"；补 Sampling／Distribution、Data／Specification、Optimization／Specification 的边界判据；Mixed 按主类型分流
- `validate_output.py` v2：识别横幅与档位并按档检查；接受 `## 1.`／`## 一、`／`**1. 结构分类**`／`## **结构分类**` 等写法；章节正文按 markdown 层级提取（### 子标题不截断）；空壳章节判失败（长度下限＋结构分类须有类型词与理由＋假设节须有检验与修正）；代码检测只认带语言标签或读起来像代码的围栏（去掉"方案"等词触发）；设计／字段图必须在第一个代码围栏之前；识别澄清协议（≥2 个选项）时不要求设计／字段图；`--tier`、`--lang zh|en|auto`、`--json`
- `fieldmap_template.py`：中文骨架；`--compact` 输出二档合并版
- 新增示例：一档结构卡（排序脚本）、二档精简（删旧日志），示例中的检验结果为实际运行结果；原两份示例改中文标题并标注用途
- 反模式新增：档位错配、对着校验器写字、贴标签不分流
- description 改为中英双语并以品牌开头，删去正文中的"何时使用"段（触发条件只放 description）；原 description 列出的 "probability" 不在分类法中，已对齐为五类
- README／portable-core 与 SKILL.md 对齐；README 补解压后改名说明
- 未动：语言规则仍为"标题与正文中文"（英文用户场景待定）；evals.json 原样保留

## 2026-11-04
- Initial skill creation
- Core workflow: structure classification → intent/spec/gap → design/field map → hypothesis-test-correct
- Added validation script and field map template for higher obedience
- Added portable-core.md for cross-platform use
- Updated to Chinese-primary with key English terms retained (section names, structure types, critical instructions)
- Added retrieval scenario extension (`references/retrieval.md`)
- Requires explicit Grounded Data, bidirectional evidence (positive + negation), evidence comparison, and negation blind-spot check for retrieval/RAG tasks
- Updated SKILL.md with navigation rule for retrieval scenarios
- 新增差距过大时的澄清协议：先提出 3 个多选问题，仍模糊时再提出最多 3 个，总数不超过 6 个。
