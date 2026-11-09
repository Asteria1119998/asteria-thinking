# Cross-Platform Usage

## Claude / Grok
Place the entire folder in the skills directory, renamed to `asteria-thinking/` (Claude Code requires the folder name to match the `name` in SKILL.md).
The model will load SKILL.md when the description matches. Every response then starts with the banner
`【Asteria思维模型】档位：…｜主类型：…`, which declares the tier the model chose; reply "用三档" / "一档就行" to override.
Instruct it to run `scripts/validate_output.py` on its finished draft (not before writing it).

## GPT (ChatGPT, GPTs, Projects)
- Paste the contents of `portable-core.md` into Custom Instructions or Project knowledge.
- Optionally upload `scripts/validate_output.py` and tell the model to use Code Interpreter to self-check.
- For highest obedience, create a GPT whose instructions begin with the portable core.

## Other platforms (Workbuddy, etc.)
Use `portable-core.md` as a system prompt or persistent instruction block.
The validation script can be run manually by the user on the model's output.

## Shared Principle
The portable core is intentionally strict and short so it survives context limits and different system-prompt styles.
