#!/usr/bin/env python3
"""
Asteria思维模型 / asteria-thinking — 下限校验器（v2）

检查一份回复是否满足所声明档位的"形"的下限：
  * 第一行横幅：品牌 + 档位 + 主类型
  * 该档位要求的章节存在、顺序正确、不是空壳
  * 结构分类里有类型词和理由；假设节里有检验和修正
  * 有代码时，设计/字段图（二档：关键决策与失败点）出现在第一个代码围栏之前
  * 标题中文（--lang zh，默认）

它不检查你想得对不对。PASS ≠ 想清楚了。

用法:
  python3 validate_output.py output.md [--tier 1|2|3] [--lang zh|en|auto] [--json]
退出码: 0 = PASS（可能带 WARN），1 = FAIL
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Tuple

# ---------- 词表 ----------
BRAND = "Asteria思维模型"
TIER_WORDS = {"一": 1, "1": 1, "二": 2, "2": 2, "三": 3, "3": 3}
TIER_LABELS = {1: "一档·结构卡", 2: "二档·精简", 3: "三档·完整"}

TYPE_WORDS = r"(?:Sampling|Distribution|Optimization|Data|Specification|Mixed|抽样|采样|分布|优化|数据|规格|混合)"
REASON_WORDS = r"(?:因为|理由|原因|信号|依据|判据|所以|分叉|在于|说明|取决于|由于|决定于|源于|体现在)"
TEST_WORDS = r"(?:检验|测试|验证|重跑|复跑|跑一次|跑了|对比|核对)"
FIX_WORDS = r"(?:修正|改为|改成|换成|若|如果|失败|不成立|不通过|则)"
FAIL_WORDS = r"(?:失败|风险|炸|出错|错位|漂移|退化)"

# 章节名 → 识别模式（在标题文本内任意位置匹配）
SECTION_PATTERNS: Dict[str, str] = {
    "结构分类": r"(?:结构分类|深层结构分类|Structure\s*Classification)",
    "意图": r"(?:意图|Intent)",
    "规格": r"(?:规格|规范|Specification)",
    "差距": r"(?:差距|间隙|Gap)",
    "设计": r"(?:设计|Design)",
    "字段图": r"(?:字段图|域图|Field\s*Map)",
    "关键决策": r"(?:关键决策|Key\s*Decisions)",
    "假设": r"(?:假设|Hypothesis)",
    "澄清": r"(?:澄清|Clarif)",
    "实现": r"(?:实现|Implementation|最终答案)",
}

NUM = r"(?:[0-9]{1,2}|[一二三四五六七八九十]{1,3})\s*[.、．)）:：]?\s*"
HEADING_MD = re.compile(r"^\s{0,3}(#{2,4})\s*(?:\*\*)?\s*(?:" + NUM + r")?\s*(?:\*\*)?\s*(.+?)\s*(?:\*\*)?\s*#*\s*$")
HEADING_BOLD = re.compile(r"^\s*\*\*\s*(?:" + NUM + r")?\s*([^*]+?)\s*\*\*\s*[:：]?\s*$")
FENCE = re.compile(r"^\s{0,3}(```+|~~~+)\s*([\w+#.-]*)\s*$")
OPTION_LINE = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?[A-Fa-f][.、．)）]\s*\S")
CJK = re.compile(r"[一-鿿]")

CODE_LANGS = {
    "python", "py", "python3", "js", "javascript", "ts", "typescript", "bash", "sh", "shell", "zsh",
    "go", "golang", "rust", "rs", "java", "c", "cpp", "c++", "cs", "csharp", "sql", "yaml", "yml",
    "json", "toml", "html", "css", "php", "ruby", "rb", "swift", "kotlin", "kt", "r", "scala",
    "powershell", "ps1", "dockerfile", "makefile", "lua", "perl", "dart", "jsx", "tsx",
}
NON_CODE_LANGS = {"", "text", "txt", "md", "markdown", "plain", "plaintext", "mermaid", "diagram", "tree", "ascii", "output", "log"}
CODEISH = re.compile(r"(?:^\s*(?:def|class|import|from|return|if|for|while|function|const|let|var|SELECT|INSERT|CREATE)\b|=>|;\s*$|\{\s*$|^\s*\}|\bprint\(|\$\s*\w+\s+)")


class Heading:
    def __init__(self, line_no: int, level: int, text: str):
        self.line_no = line_no
        self.level = level
        self.text = text
        self.kinds = [k for k, p in SECTION_PATTERNS.items() if re.search(p, text, re.IGNORECASE)]
        self.body = ""  # filled later


def parse(text: str):
    lines = text.splitlines()
    headings: List[Heading] = []
    fences: List[Tuple[int, int, str, List[str]]] = []  # (start, end, lang, content lines)
    in_fence = False
    fence_start = 0
    fence_lang = ""
    fence_mark = ""
    buf: List[str] = []
    for i, line in enumerate(lines):
        m = FENCE.match(line)
        if in_fence:
            if m and m.group(1)[0] == fence_mark[0] and len(m.group(1)) >= len(fence_mark) and not m.group(2):
                fences.append((fence_start, i, fence_lang, buf))
                in_fence = False
                buf = []
            else:
                buf.append(line)
            continue
        if m:
            in_fence = True
            fence_start = i
            fence_mark = m.group(1)
            fence_lang = m.group(2).lower()
            continue
        hm = HEADING_MD.match(line)
        if hm:
            headings.append(Heading(i, len(hm.group(1)), hm.group(2).strip("* ").strip()))
            continue
        hb = HEADING_BOLD.match(line)
        if hb and len(hb.group(1)) <= 40:
            cand = Heading(i, 2, hb.group(1).strip())
            if cand.kinds:  # a bold line only counts as a heading when it names a protocol section
                headings.append(cand)
    if in_fence:  # unterminated fence: treat as content
        fences.append((fence_start, len(lines), fence_lang, buf))
    # bodies: a section runs until the next heading of the same or higher level (markdown semantics),
    # so ### sub-heads inside a ## section stay part of its body
    for idx, h in enumerate(headings):
        end = len(lines)
        for nxt in headings[idx + 1:]:
            if nxt.level <= h.level:
                end = nxt.line_no
                break
        h.body = "\n".join(lines[h.line_no + 1:end])
    return lines, headings, fences


def is_code_fence(lang: str, content: List[str]) -> bool:
    if lang in CODE_LANGS:
        return True
    if lang in NON_CODE_LANGS or not lang:
        hits = sum(1 for l in content if CODEISH.search(l))
        return hits >= 2 and lang == ""  # untagged fence that reads like code
    return False  # unknown tag (e.g. a made-up label): not counted as code


def body_len(s: str) -> int:
    return len(re.sub(r"[\s\-\*\|#>`_]+", "", s))


def detect_banner(lines: List[str]) -> Tuple[Optional[int], Optional[int], Optional[str], List[str]]:
    """returns (line_no, tier, primary_type, warnings)"""
    warnings: List[str] = []
    nonempty = [(i, l) for i, l in enumerate(lines) if l.strip()]
    for pos, (i, l) in enumerate(nonempty[:10]):
        if BRAND in l:
            tier = None
            tm = re.search(r"([一二三123])\s*档", l) or re.search(r"Tier\s*([123])", l, re.IGNORECASE)
            if tm:
                tier = TIER_WORDS.get(tm.group(1))
            elif "结构卡" in l:
                tier = 1
            elif "精简" in l:
                tier = 2
            elif "完整" in l:
                tier = 3
            pm = re.search(r"主类型\s*[:：]?\s*(" + TYPE_WORDS + r")", l) or re.search(TYPE_WORDS, l)
            ptype = pm.group(1) if pm and pm.lastindex else (pm.group(0) if pm else None)
            if pos != 0:
                warnings.append(f"横幅不在第一行（在第 {i + 1} 行）：横幅应是回复的第一行")
            return i, tier, ptype, warnings
    return None, None, None, warnings


def first_section(headings: List[Heading], kind: str) -> Optional[Heading]:
    for h in headings:
        if kind in h.kinds:
            return h
    return None


def validate(text: str, tier_override: Optional[int] = None, lang: str = "zh") -> Dict:
    errors: List[str] = []
    warnings: List[str] = []
    info: List[str] = []
    lines, headings, fences = parse(text)

    # --- 语言模式 ---
    if lang == "auto":
        cjk = len(CJK.findall(text))
        letters = len(re.findall(r"[A-Za-z]", text))
        lang = "zh" if cjk >= 0.2 * max(1, cjk + letters) else "en"

    # --- 横幅 / 档位 ---
    banner_line, banner_tier, ptype, w = detect_banner(lines)
    warnings += w
    if banner_line is None:
        errors.append(f"缺少开场横幅：第一行应为「【{BRAND}】档位：…｜主类型：…」")
    elif banner_tier is None:
        errors.append("横幅里没有声明档位（一档·结构卡 / 二档·精简 / 三档·完整）")
    if banner_line is not None and ptype is None:
        errors.append("横幅里没有声明主类型（Sampling / Distribution / Optimization / Data / Specification / Mixed）")

    tier = tier_override or banner_tier
    if tier_override and banner_tier and tier_override != banner_tier:
        warnings.append(f"--tier {tier_override} 与横幅声明的 {TIER_LABELS[banner_tier]} 不一致，按 --tier 检查")
    if tier is None:
        tier = 3
        warnings.append("无法确定档位，按三档（最严）检查")

    # --- 代码围栏 ---
    code_fences = [(s, e) for (s, e, lg, content) in fences if is_code_fence(lg, content)]
    first_code = code_fences[0][0] if code_fences else None
    has_code = first_code is not None

    # --- 标题语言 ---
    if lang == "zh":
        bad = [h.text for h in headings if h.kinds and not CJK.search(h.text)]
        if bad:
            errors.append("标题须为中文（可保留术语），以下标题无中文：" + "；".join(bad[:5]))

    def require(kind: str, min_len: int) -> Optional[Heading]:
        h = first_section(headings, kind)
        if h is None:
            errors.append(f"缺少章节：{kind}")
            return None
        if body_len(h.body) < min_len:
            errors.append(f"章节「{kind}」是空壳（正文 {body_len(h.body)} 字 < {min_len}）")
        return h

    def has_reason(s: str, min_after: int) -> bool:
        """理由 = 出现理由标记词，或类型词之后紧跟着一段实质说明（不是只贴标签）。"""
        if re.search(REASON_WORDS, s):
            return True
        m = re.search(TYPE_WORDS, s, re.IGNORECASE)
        if not m:
            return False
        tail = s[m.end():]
        tail = re.split(r"[｜|]", tail, maxsplit=1)[0]  # 结构卡：只看本字段
        tail = re.sub(r"[\s\W_]+", "", tail)  # 去掉标点与空白
        return len(tail) >= min_after

    def check_classification_text(s: str, where: str, min_after: int = 20):
        if not re.search(TYPE_WORDS, s, re.IGNORECASE):
            errors.append(f"{where}没有结构类型词（Sampling/Distribution/Optimization/Data/Specification/Mixed）")
        elif not has_reason(s, min_after):
            errors.append(f"{where}只有标签没有理由：类型词后面要跟一句为什么")

    def check_hypothesis_text(s: str, where: str):
        if not re.search(TEST_WORDS, s):
            errors.append(f"{where}没有检验（需写出怎么测、可观察的结果）")
        if not re.search(FIX_WORDS, s):
            errors.append(f"{where}没有修正（测试失败要改什么）")

    # --- 分档检查 ---
    if tier == 1:
        card = next((l for i, l in enumerate(lines)
                     if i != banner_line and re.match(r"^\s*(?:[-*>]\s*)?(?:\*\*)?\s*结构卡\s*[:：]", l)), None)
        if card is None:
            errors.append("一档缺少结构卡行：「结构卡：主类型 …｜最大差距：…｜最可能失败点：…｜检验：… → …」")
        else:
            check_classification_text(card, "结构卡", min_after=10)
            if "差距" not in card:
                errors.append("结构卡缺「最大差距」")
            if not re.search(FAIL_WORDS, card):
                errors.append("结构卡缺「最可能失败点」")
            if not re.search(TEST_WORDS, card):
                errors.append("结构卡缺「检验」")
            elif not re.search(r"(→|->|结果|已跑|通过|正确|未跑)", card):
                warnings.append("结构卡的「检验」没有写结果：能跑的检验应在交付前跑掉")
        pre = [l for l in lines[: (first_code if first_code is not None else len(lines))] if l.strip()]
        if first_code is not None and len(pre) > 8:
            warnings.append(f"一档代码前有 {len(pre)} 个非空行（期望 ≤ 5 行）：是否该升到二档，或压缩前置内容？")

    elif tier == 2:
        c = require("结构分类", 30)
        if c:
            check_classification_text(c.body, "「结构分类」")
            if body_len(c.body) > 400:
                warnings.append("二档「结构分类」超过约 3 行，考虑压缩或升三档")
        require("差距", 30)
        hyp = require("假设", 30)
        if hyp:
            check_hypothesis_text(hyp.body, "「假设 / 检验 / 修正」")
        if has_code:
            pre_chars = body_len("\n".join(lines[:first_code]))
            if pre_chars > 1200:
                warnings.append(f"二档代码前约 {pre_chars} 字（期望 600–900）：行数达标但每行很密，考虑压缩或升三档")
            kd = first_section(headings, "关键决策")
            d, f = first_section(headings, "设计"), first_section(headings, "字段图")
            if kd is None and not (d and f):
                errors.append("二档有代码但缺「关键决策与失败点」（或设计＋字段图）")
            else:
                sec = kd or f
                if sec.line_no > first_code:
                    errors.append("「关键决策与失败点」出现在代码之后：必须在第一个代码围栏之前")
                if not re.search(FAIL_WORDS, sec.body):
                    errors.append("「关键决策与失败点」没有写失败点")
                bullets = [l for l in sec.body.splitlines() if re.match(r"^\s*(?:[-*]|\d+[.、)])\s*\S", l)]
                if len(bullets) < 2:
                    errors.append("「关键决策与失败点」少于 2 条")

    else:  # tier 3
        order_kinds = ["结构分类", "意图", "规格", "差距", "假设"]
        min_len = {"结构分类": 50, "意图": 20, "规格": 40, "差距": 40, "假设": 50}
        found: Dict[str, Heading] = {}
        for k in order_kinds:
            h = require(k, min_len[k])
            if h:
                found[k] = h
        if "结构分类" in found:
            check_classification_text(found["结构分类"].body, "「结构分类」")
        if "假设" in found:
            check_hypothesis_text(found["假设"].body, "「假设 / 检验 / 修正」")
        seq = [found[k].line_no for k in order_kinds if k in found]
        if seq != sorted(seq):
            errors.append("章节顺序错误：应为 结构分类 → 意图 → 规格 → 差距 → … → 假设 / 检验 / 修正")
        d, f = first_section(headings, "设计"), first_section(headings, "字段图")
        clar = first_section(headings, "澄清")
        clar_ok = bool(clar) and sum(1 for l in clar.body.splitlines() if OPTION_LINE.match(l)) >= 2
        if has_code:
            if d is None or f is None:
                errors.append("三档有代码但缺「设计」或「字段图」：两者都必须在代码之前")
            else:
                for name, sec, mn in (("设计", d, 40), ("字段图", f, 50)):
                    if sec.line_no > first_code:
                        errors.append(f"「{name}」出现在第一个代码围栏之后：必须在代码之前")
                    if body_len(sec.body) < mn:
                        errors.append(f"章节「{name}」是空壳（正文 {body_len(sec.body)} 字 < {mn}）")
                if not re.search(FAIL_WORDS, f.body):
                    errors.append("「字段图」没有写失败点")
            if clar_ok:
                warnings.append("同时出现澄清问题和代码：差距过大时应停在澄清，不出代码")
        else:
            if clar_ok:
                info.append("检测到澄清协议（≥2 个选项）：设计／字段图／实现顺延，不作要求")
            elif d is None or f is None:
                warnings.append("三档无代码、无澄清：若回复包含方案或计划，必须补「设计」与「字段图」（校验器无法从文字判断是否含方案）")

    ok = not errors
    return {
        "ok": ok,
        "tier": tier,
        "tier_label": TIER_LABELS.get(tier, "?"),
        "primary_type": ptype,
        "has_code": has_code,
        "lang": lang,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "headings": [h.text for h in headings if h.kinds],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Asteria思维模型 下限校验器 v2")
    ap.add_argument("file")
    ap.add_argument("--tier", type=int, choices=(1, 2, 3), help="强制按某档检查（默认读横幅）")
    ap.add_argument("--lang", choices=("zh", "en", "auto"), default="zh", help="标题语言规则（默认 zh）")
    ap.add_argument("--json", action="store_true", help="机读输出")
    a = ap.parse_args()
    with open(a.file, "r", encoding="utf-8") as fh:
        text = fh.read()
    r = validate(text, a.tier, a.lang)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        head = "PASS" if r["ok"] else "FAIL"
        print(f"{head}  档位：{r['tier_label']}  主类型：{r['primary_type'] or '—'}  代码：{'有' if r['has_code'] else '无'}")
        for e in r["errors"]:
            print(f"  ✗ {e}")
        for w in r["warnings"]:
            print(f"  ! {w}")
        for i in r["info"]:
            print(f"  · {i}")
        print("  — 校验只查形；PASS ≠ 想清楚。")
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
