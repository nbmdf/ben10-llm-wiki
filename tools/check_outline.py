#!/usr/bin/env python3
"""Outline check（前移的檢查）：在生成簡報『之前』確認每頁要用的 wiki 頁與事實都存在、可用。"""
import sys, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parent.parent
facts = yaml.safe_load((ROOT / "wiki/facts.yaml").read_text())
pages = {p.stem for p in (ROOT / "wiki").glob("*.md")} | {"index", "sources"}
outline = yaml.safe_load((ROOT / "slides/outline.yaml").read_text())
err = []
for s in outline:
    if not s.get("question"): err.append(f"[{s['id']}] 沒有寫學習者問題")
    for w in s["wiki"]:
        if w not in pages: err.append(f"[{s['id']}] wiki 頁 {w} 不存在")
    for k in s["facts"]:
        if k not in facts: err.append(f"[{s['id']}] fact {k} 不存在 → 先回 Wiki 補資料")
        elif facts[k]["status"] == "excluded": err.append(f"[{s['id']}] fact {k} 已 excluded，不可規劃使用")
    # 規則：提到年份/集數/年齡的頁面，必須至少宣告 1 個 fact
    if s["id"] not in ("cover",) and not s["facts"]: err.append(f"[{s['id']}] 沒有宣告任何 fact")
for e in err: print("ERROR", e)
print(f"大綱 {len(outline)} 頁｜ERROR {len(err)}"); sys.exit(1 if err else 0)
