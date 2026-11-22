#!/usr/bin/env python3
"""Grounding check：簡報的檢查節點。每頁的數字與英文專有名詞都必須能追溯到該頁宣告的 Wiki 頁面/事實。"""
import re, sys, pathlib, yaml
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
facts = yaml.safe_load((ROOT / "wiki/facts.yaml").read_text())
outline = {s["id"]: s for s in yaml.safe_load((ROOT / "slides/outline.yaml").read_text())}
wiki = {p.stem: p.read_text() for p in (ROOT / "wiki").glob("*.md")}
wiki["index"] = (ROOT / "index.md").read_text()
wiki["sources"] = (ROOT / "raw/sources.yaml").read_text()
html = (ROOT / "slides/index.html").read_text()

class P(HTMLParser):
    def __init__(s): super().__init__(); s.slides=[]; s.cur=None; s.depth=0; s.skip=0
    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag == "section" and "slide" in (a.get("class") or ""):
            s.cur = {"id": a["id"], "wiki": [w for w in a.get("data-wiki","").split(",") if w],
                     "facts": [f for f in a.get("data-facts","").split(",") if f], "text": [], "note": []}
            s.slides.append(s.cur); s.depth = 0
        if s.cur is not None:
            s.depth += 1
            if tag == "div" and "note" in (a.get("class") or ""): s.skip = s.depth
    def handle_endtag(s, tag):
        if s.cur is not None:
            if s.skip and s.depth == s.skip: s.skip = 0
            s.depth -= 1
            if tag == "section": s.cur = None
    def handle_data(s, d):
        if s.cur is not None: (s.cur["note"] if s.skip else s.cur["text"]).append(d)

p = P(); p.feed(html)
errors = []
for sl in p.slides:
    sid = sl["id"]
    nodes = [re.sub(r"^\s*\d+\.\s", "", n) for n in sl["text"] if n.strip()]
    text = " ".join(nodes)
    if sid not in outline: errors.append(f"[{sid}] 不在 outline（未經 Query 節點）"); continue
    o = outline[sid]
    if set(sl["facts"]) != set(o["facts"]): errors.append(f"[{sid}] data-facts 與 outline 不一致")
    for w in sl["wiki"]:
        if w not in wiki: errors.append(f"[{sid}] 引用不存在的 wiki 頁 {w}")
    allowed = set()
    for k in sl["facts"]:
        f = facts.get(k)
        if not f: errors.append(f"[{sid}] 未知 fact {k}"); continue
        if f["status"] == "excluded": errors.append(f"[{sid}] 使用了 excluded 事實 {k}")
        allowed |= set(re.findall(r"\d+", f"{f['value']} {f.get('note','')}"))
    src = "\n".join(wiki.get(w, "") for w in sl["wiki"])
    terms = set()
    for node in nodes:
        for term in re.findall(r"[A-Za-z][A-Za-z0-9.,\-]*(?: [A-Za-z0-9][A-Za-z0-9.,\-]*)*", node):
            terms.add(term.strip(" ,."))
    stripped = text
    for t in sorted(terms, key=len, reverse=True):
        if t in src: stripped = stripped.replace(t, " ")
    # 1) 數字必須來自本頁宣告的事實（已出現在 wiki 的專有名詞如「Ben 10」「XLR8」先剔除）
    for n in re.findall(r"\d+", stripped):
        if n not in allowed: errors.append(f"[{sid}] 數字 {n} 沒有對應的 fact")
    # 2) 英文專有名詞必須出現在本頁引用的 wiki 頁面
    for t in terms:
        if len(t) > 1 and t not in src: errors.append(f"[{sid}] 名詞「{t}」不在引用的 wiki 頁")
    # 3) excluded 事實的內容不能出現
    for k, f in facts.items():
        if f["status"] == "excluded" and str(f["value"])[:6] in text:
            errors.append(f"[{sid}] 出現 excluded 內容（{k}）")

missing = set(outline) - {s["id"] for s in p.slides}
for m in missing: errors.append(f"[{m}] outline 有但簡報沒做")
for e in errors: print("ERROR", e)
print(f"\n投影片 {len(p.slides)}｜ERROR {len(errors)}")
sys.exit(1 if errors else 0)
