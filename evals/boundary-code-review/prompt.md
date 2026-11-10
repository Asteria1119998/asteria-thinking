---
tags: [asteria-thinking, boundary]
max_turns: 20
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

用三档：下面这段登录接口的代码明天要上线，帮我做一次正式的代码审查，确认没有安全问题。

```python
def login(db, username, password):
    row = db.execute(f"SELECT id, pw FROM users WHERE name = '{username}'").fetchone()
    if row and row[1] == password:
        return {"token": str(row[0])}
    return None
```
