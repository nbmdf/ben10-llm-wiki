"""Render check：截圖每頁並偵測文字溢出、導覽是否正常。"""
import sys, pathlib, json
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
url = (ROOT/"slides/index.html").as_uri()
issues=[]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width":1300,"height":740})
    pg.goto(url); pg.wait_for_timeout(1500)
    ids = pg.eval_on_selector_all(".slide","els=>els.map(e=>e.id)")
    for k,sid in enumerate(ids):
        pg.evaluate(f"location.hash='#{sid}'"); pg.wait_for_timeout(450)
        r = pg.evaluate("""()=>{const s=document.querySelector('.slide.active');const out=[];
          const sb=s.getBoundingClientRect();
          s.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect();
            if((e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2) && getComputedStyle(e).overflow==='hidden' && e.textContent.trim()) out.push('clip:'+e.className+':'+e.textContent.trim().slice(0,30));
            if(r.width && (r.bottom>sb.bottom-40 || r.right>sb.right+1) && !e.closest('.cover-band') && !e.classList.contains('cover-band') && !e.closest('.note') && !e.classList.contains('note')) out.push('out:'+e.tagName+':'+e.textContent.trim().slice(0,30));});
          let lo=1e9,hi=0;[...s.children].forEach(c=>{if(c.classList.contains('note')||c.classList.contains('cover-band'))return;const r=c.getBoundingClientRect();lo=Math.min(lo,r.top);hi=Math.max(hi,r.bottom);});
          const fill=(hi-lo)/sb.height; if(fill<0.45) out.push('sparse:fill='+fill.toFixed(2));
          const n=s.querySelector('.note'); if(n&&n.textContent.includes('Wiki')){s.dataset.wiki.split(',').forEach(w=>{if(!n.textContent.includes(w))out.push('note-missing-wiki:'+w)})}
          return {id:s.id,out:[...new Set(out)]}}""")
        if r["out"]: issues.append(r)
        pg.screenshot(path=str(ROOT/f"report/shots/{k+1:02d}-{sid}.png"))
    pg.evaluate("location.hash='#cover'"); pg.wait_for_timeout(300)
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(300)
    nav = pg.evaluate("location.hash")
    if nav!="#one-line": issues.append({"nav":nav})
    b.close()
print(json.dumps(issues,ensure_ascii=False,indent=1)); print("ISSUES",len(issues)); sys.exit(1 if issues else 0)
