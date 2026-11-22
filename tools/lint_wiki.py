#!/usr/bin/env python3
"""Wiki lint：Wiki 層的檢查節點。回傳非 0 代表要退回 ingest / compile 重做。"""
import re, sys, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sources = yaml.safe_load((ROOT / "raw/sources.yaml").read_text())
facts = yaml.safe_load((ROOT / "wiki/facts.yaml").read_text())
pages = {p.stem: p.read_text() for p in (ROOT / "wiki").glob("*.md")}
errors, warns = [], []

conflicts_text = pages.get("conflicts", "")
for name, text in pages.items():
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"[{name}] 缺 frontmatter"); continue
    fm = yaml.safe_load(m.group(1))
    for k in ("title", "sources", "updated"):
        if k not in fm: errors.append(f"[{name}] frontmatter 缺 {k}")
    body = text[m.end():]
    cited = set(re.findall(r"\[((?:S|X)\d+)\]", body))
    for c in cited:
        if c not in sources: errors.append(f"[{name}] 引用未登錄來源 {c}")
        if c.startswith("X") and name != "conflicts":
            errors.append(f"[{name}] 低可信來源 {c} 被當作事實依據")
    fm_src = set(fm.get("sources", []))
    if cited - fm_src: errors.append(f"[{name}] 內文引用 {sorted(cited - fm_src)} 未列在 frontmatter")
    if fm_src - cited: warns.append(f"[{name}] frontmatter 列了 {sorted(fm_src - cited)} 但內文沒用到")
    for link in re.findall(r"\[\[([^\]]+)\]\]", body):
        if link not in pages: errors.append(f"[{name}] 斷鏈 [[{link}]]")
    # 含數字的事實行必須有來源標記（教學比喻段落除外）
    section = ""
    for line in body.splitlines():
        if line.startswith("#"): section = line; continue
        if "比喻" in section or "怎麼選" in section: continue
        is_claim = line.lstrip().startswith(("-", "|", "1.", "2.", "3.")) and not re.match(r"^\|[-| ]+\|$", line.strip())
        if is_claim and re.search(r"\d", line) and not re.search(r"\[(S|X)\d+\]|C\d|\[\[", line):
            if not line.strip().startswith("| #") and not line.strip().startswith("| 系列"):
                errors.append(f"[{name}] 含數字但沒有來源標記：{line.strip()[:60]}")

all_wiki = "\n".join(pages.values())
for key, f in facts.items():
    st = f.get("status")
    if st not in ("verified", "resolved", "excluded"):
        errors.append(f"[facts.{key}] status 不合法：{st}")
    for s in f.get("sources", []):
        if s not in sources: errors.append(f"[facts.{key}] 未登錄來源 {s}")
    if st in ("verified", "resolved") and all(s.startswith("X") for s in f.get("sources", [])):
        errors.append(f"[facts.{key}] 只有低可信來源卻標為 {st}")
    if st == "resolved" and key not in conflicts_text:
        errors.append(f"[facts.{key}] 標為 resolved 但 conflicts.md 沒有裁決紀錄")
    if st != "excluded":
        core = re.split(r"[（(]", str(f["value"]))[0].strip()
        if core and core not in all_wiki:
            warns.append(f"[facts.{key}] 值「{core}」沒有出現在任何 wiki 頁面")

for w in warns: print("WARN ", w)
for e in errors: print("ERROR", e)
print(f"\n頁面 {len(pages)}｜事實 {len(facts)}｜ERROR {len(errors)}｜WARN {len(warns)}")
sys.exit(1 if errors else 0)
