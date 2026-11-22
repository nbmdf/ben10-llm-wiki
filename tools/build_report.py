import pathlib, re, html, yaml, markdown
R = pathlib.Path(__file__).resolve().parent.parent
md = lambda t: markdown.markdown(t, extensions=["tables"])
def page_html(path):
    t = path.read_text(); t = re.sub(r"^---\n.*?\n---\n", "", t, flags=re.S)
    t = re.sub(r"\[\[([^\]]+)\]\]", r'<a href="#wiki-\1">\1</a>', t)
    t = re.sub(r"\[((?:S|X)\d+)\]", r'<a class="src" href="#sources">\1</a>', t)
    return md(t)
order = ["overview","man-of-action","omnitrix","characters","series-timeline","continuity","films-and-media","impact","conflicts"]
pages = {n: page_html(R/f"wiki/{n}.md") for n in order}
titles = {n: re.search(r"title: (.*)", (R/f"wiki/{n}.md").read_text()).group(1) for n in order}
srcs = yaml.safe_load((R/"raw/sources.yaml").read_text())
facts = yaml.safe_load((R/"wiki/facts.yaml").read_text())
src_rows = "".join(f"<tr><td><b>{k}</b></td><td><a href='{v['url']}'>{html.escape(v['title'])}</a></td><td>{v['method']}</td><td>{v['reliability']}</td></tr>" for k,v in srcs.items())
fact_rows = "".join(f"<tr><td><code>{k}</code></td><td>{html.escape(str(v['value']))}{(' <span class=mute>（'+html.escape(v['note'])+'）</span>') if v.get('note') else ''}</td><td>{', '.join(v['sources'])}</td><td><span class='st {v['status']}'>{v['status']}</span></td></tr>" for k,v in facts.items())
nav_wiki = "".join(f'<a href="#wiki-{n}">{titles[n]}</a>' for n in order)
wiki_secs = "".join(f'<section class="view" id="wiki-{n}"><div class="crumb">Wiki / {n}.md</div>{pages[n]}</section>' for n in order)
svg = (R/"tools/graph.svg").read_text()
log = md(re.sub(r"^# .*\n", "", (R/"log.md").read_text()))
schema = md(re.sub(r"^# .*\n", "", (R/"SCHEMA.md").read_text()))
def pre(f): return html.escape((R/f).read_text())
SLIDES = "https://claude.ai/artifact/BN5epi2Rvi2YPXAUv1oiVR"
body = f"""
<section class="view" id="home">
<div class="kicker">作業繳交總覽</div>
<h1>Ben 10 LLM Wiki → 教學 HTML 簡報</h1>
<p class="lead">先用「先討論、後生成」的方式建立 Ben 10 主題的 LLM Wiki（ingest 9 篇可作依據的資料＋4 篇比對用資料），再讓 AI 只能用 Wiki 當知識來源，產生給新手看的教學簡報。每一步都有檢查節點，檢查失敗就退回對應節點重做。</p>
<div class="cards">
 <a class="card" href="#wiki-overview"><b>1–2. LLM Wiki</b><span>9 個主題頁、34 條事實、8 個衝突裁決</span></a>
 <a class="card" href="{SLIDES}"><b>3. 教學 HTML 簡報 ↗</b><span>14 頁，←→ 翻頁，含小測驗</span></a>
 <a class="card" href="#graph"><b>4. Loop / Graph</b><span>11 個節點、4 個檢查節點、7 條退回邊</span></a>
 <a class="card" href="#run"><b>5. 實際執行紀錄</b><span>19 步，含每次檢查的原始輸出</span></a>
 <a class="card" href="#reflect"><b>6. 反思</b><span>最常出錯的節點與調整</span></a>
</div>
<h2>Wiki 主題簡介</h2>
<p><b>主題：Ben 10 動畫系列入門。</b>Ben 10 是 Man of Action 構思、Cartoon Network Studios 製作的美國科幻英雄動畫：10 歲男孩 Ben 撿到外星手錶 Omnitrix，能變身成各種外星人。系列共 5 部電視動畫、分成經典與重啟 2 條時間線。這個 Wiki 的讀者設定是「完全沒看過的人」，所以內容聚焦在核心概念、作品順序與入門建議，不追劇情細節。</p>
<h2>Wiki 結構（Karpathy 式三層）</h2>
<table><tr><th>層</th><th>檔案</th><th>作用</th></tr>
<tr><td>Raw 原始層</td><td><code>raw/sources.yaml</code>、<code>raw/notes.md</code></td><td>登錄來源、逐篇改寫摘要；只追加不改原意</td></tr>
<tr><td>Wiki 知識層</td><td><code>wiki/*.md</code>、<code>wiki/facts.yaml</code></td><td>LLM 撰寫的主題頁＋關鍵事實表（每條有來源與 status）</td></tr>
<tr><td>Schema 規則層</td><td><code>SCHEMA.md</code>、<code>index.md</code>、<code>log.md</code></td><td>LLM 每次操作前要讀的規則、目錄、操作紀錄</td></tr></table>
</section>

<section class="view" id="schema"><div class="crumb">SCHEMA.md</div><h1>Schema（維護規則）</h1>{schema}</section>
{wiki_secs}
<section class="view" id="facts"><div class="crumb">wiki/facts.yaml</div><h1>關鍵事實表</h1><p>簡報上每個數字都要對應到這裡 <span class="st verified">verified</span> 或 <span class="st resolved">resolved</span> 的條目；<span class="st excluded">excluded</span> 的條目不可使用。</p><table><tr><th>key</th><th>值</th><th>來源</th><th>status</th></tr>{fact_rows}</table></section>
<section class="view" id="sources"><div class="crumb">raw/sources.yaml</div><h1>Ingest 來源（13 篇）</h1><p>S1–S9 可作事實依據；X1–X4 是低可信來源，只用來找出衝突。method = snippet 表示整頁擷取被拒、改用搜尋摘要。</p><table><tr><th>ID</th><th>來源</th><th>方式</th><th>可信度</th></tr>{src_rows}</table></section>

<section class="view" id="graph">
<div class="kicker">步驟三</div><h1>Loop / Graph 設計</h1>
<div class="svgwrap">{svg}</div>
<h2>流程（文字版）</h2>
<p class="flow">討論 → 取得 → 匯入＋交叉比對 → 編譯 Wiki → <b>Wiki Lint</b> → 查詢 Wiki（大綱）→ <b>大綱檢查</b> → 生成簡報 → <b>依據檢查</b> → <b>渲染＋目視檢查</b> → 發布</p>
<h2>哪些步驟會重複執行？</h2>
<ul>
<li><b>取得 → 匯入 → 編譯 → Lint</b> 是一個迴圈：每多 ingest 一篇資料就跑一輪，lint 沒過就不能往下走。</li>
<li><b>查詢 → 大綱檢查</b>：大綱要用的事實如果 Wiki 沒有，就回到「編譯 Wiki」先補，再重新查詢。這次 Cannonbolt 就是這樣補進 Wiki 的。</li>
<li><b>生成 → 依據檢查 → 渲染檢查</b>：內層迴圈，這次跑了 2 輪依據檢查、4 輪渲染檢查才全部通過。</li>
</ul>
<h2>哪些地方需要檢查或重新生成？</h2>
<table><tr><th>檢查節點</th><th>檢查什麼</th><th>失敗退回</th><th>工具</th></tr>
<tr><td>③ 匯入時交叉比對</td><td>同一個數字在不同來源是否一致</td><td>寫進 conflicts.md 裁決；無法證實就標 excluded</td><td>人工＋LLM</td></tr>
<tr><td>⑤ Wiki Lint</td><td>frontmatter、來源 ID、斷鏈、含數字的句子有沒有來源標記、resolved 事實有沒有裁決紀錄</td><td>④ 修頁面；缺資料回 ②</td><td><code>lint_wiki.py</code></td></tr>
<tr><td>⑦ 大綱檢查（新增）</td><td>每頁規劃用的 wiki 頁與事實都存在、沒有 excluded</td><td>④ 先補 Wiki</td><td><code>check_outline.py</code></td></tr>
<tr><td>⑨ 依據檢查</td><td>每頁的數字都要來自該頁宣告的事實；英文專有名詞都要出現在引用的 wiki 頁；不可出現 excluded 內容</td><td>⑥ 補宣告／⑧ 刪多編的內容</td><td><code>check_slides.py</code></td></tr>
<tr><td>⑩ 渲染＋目視</td><td>headless Chrome 截圖；文字裁切、內容填滿率、頁腳與引用一致；人工看截圖</td><td>⑧ 改版面</td><td><code>render_check.py</code></td></tr></table>
<h2>為什麼這樣設計？</h2>
<ul>
<li><b>事實跟文字分開管理</b>：LLM 最容易錯的是數字和日期，所以把它們集中到 facts.yaml，每條都要有來源和 status，簡報只能「引用 key」而不是自己寫數字，這樣就能用程式檢查。</li>
<li><b>檢查越前面越便宜</b>：來源衝突在匯入時就處理，不要等到簡報做完才發現首播日寫錯。</li>
<li><b>每個檢查都知道該退回哪裡</b>：錯誤分成「Wiki 沒有」「大綱漏宣告」「生成時多編」「版面問題」，分別退回不同節點，而不是整份重做。</li>
<li><b>檢查器本身也要被檢查</b>：用突變測試（故意塞錯）確認檢查器沒有因為修正而變太鬆。</li>
</ul>
</section>

<section class="view" id="run">
<div class="kicker">步驟四 · 實際執行一次</div><h1>執行紀錄與檢查輸出</h1>
{log}
<h2>檢查原始輸出</h2>
<details open><summary>Wiki Lint #1（4 ERROR / 3 WARN）</summary><pre>{pre('report/lint_run1.txt')}</pre></details>
<details><summary>Wiki Lint #2（通過）</summary><pre>{pre('report/lint_run2.txt')}</pre></details>
<details open><summary>依據檢查 #1（47 ERROR）</summary><pre>{pre('report/slides_check_run1.txt')}</pre></details>
<details><summary>依據檢查 #2（通過）</summary><pre>{pre('report/slides_check_run2.txt')}</pre></details>
<details><summary>渲染檢查 #2 → #4</summary><pre>#2\n{pre('report/render_run2.txt')}\n#3\n{pre('report/render_run3.txt')}\n#4\n{pre('report/render_run4.txt')}</pre></details>
<details><summary>大綱檢查（新增節點）</summary><pre>{pre('report/outline_check.txt')}</pre></details>
<h2>依據檢查 #1 的 47 個錯誤分類</h2>
<table><tr><th>類型</th><th>數量</th><th>例子</th><th>處理</th></tr>
<tr><td>⑥ 查詢節點漏宣告事實</td><td>24</td><td>continuity 頁寫了 2005／2021，但大綱沒宣告 original_years、finale_specials 的日期</td><td>補大綱事實；facts 補 note</td></tr>
<tr><td>⑨ 檢查器自己誤判</td><td>17</td><td>把「Ben 10」「XLR8」的數字當成事實；把相鄰的外星人名字黏成一個名詞</td><td>改成逐文字節點比對、先剔除 Wiki 內的專有名詞</td></tr>
<tr><td>⑧ 生成時多編內容</td><td>6</td><td>「XLR8 唸起來像 accelerate」、小測驗的「8 歲／5 種／100 種」選項、「No.2」</td><td>刪除，或改用 Wiki 裡有的內容</td></tr></table>
<p>另外人工語意審閱又抓到 3 句檢查器抓不到的多編內容（例如「Vilgax 一直想搶走 Omnitrix」：Wiki 只寫他是宿敵）。</p>
</section>

<section class="view" id="reflect">
<div class="kicker">反思</div><h1>反思</h1>
<h2>哪一個節點最常出錯？</h2>
<p><b>⑥ 查詢 Wiki（做大綱）</b>：依據檢查的 47 個錯誤中有 24 個來自這裡。大綱只列了每頁「主要」的事實，生成時卻自然地寫出年份、季數、比較用的數字，結果這些數字在檢查時找不到依據。真正寫錯內容的則是 <b>⑧ 生成</b>：6 個自動抓到加上 3 個人工抓到，都是 LLM 為了讓簡報「更好懂」而補上的說明，看起來很合理，但 Wiki 裡根本沒有。</p>
<p>資料面最大的風險在 <b>③ 匯入</b>：同一件事在不同來源有 8 處不一致（例如首播日 2005-12-27 vs 2006-01，重啟版 166 集 vs 184 集，電影 4 部 vs 5 部）。因為一開始就把交叉比對放在匯入節點，這些都在 Wiki 階段解決，沒有流到簡報。</p>
<h2>發現問題後，把檢查往前移到哪一步？</h2>
<ul>
<li><b>從「生成後」移到「生成前」</b>：新增 ⑦ 大綱檢查。原本要等簡報做完才知道「這頁用的數字沒有依據」；現在大綱就必須宣告每頁會用到的所有事實，不存在或 excluded 的事實在生成前就擋下，並退回 ④ 先補 Wiki。</li>
<li><b>從「人工目視」移到「自動檢查」</b>：渲染檢查 #1 顯示 0 個問題，但看截圖發現大片留白和時間軸文字被裁切。把「垂直裁切、內容填滿率、頁腳一致」寫進 <code>render_check.py</code>，之後的版本就會自動抓到。</li>
<li><b>從「簡報」移到「Wiki」</b>：簡報需要 Cannonbolt 這個事實時，不是直接寫進簡報，而是先補進 Wiki 的 omnitrix 頁（附來源 S7），再讓簡報引用。</li>
</ul>
<h2>有沒有因此修改 workflow / graph？為什麼？</h2>
<p>有，改了三處：</p>
<ol>
<li><b>新增節點</b>：⑥ 和 ⑧ 之間加上 ⑦ 大綱檢查（圖中綠色虛線框）。理由：最多錯誤來自大綱，最便宜的修正點就在大綱本身。</li>
<li><b>新增退回邊</b>：⑧ 生成 → ④ 編譯 Wiki。理由：生成過程發現缺資料時，資料必須先進 Wiki，維持「簡報只能引用 Wiki」的原則，Wiki 也會越用越完整。</li>
<li><b>強化檢查器並加入突變測試</b>：檢查器自己有 17 個誤判，修正後怕變太鬆，所以故意塞入「60 億美元」和不存在的名詞，確認 3/3 都被抓到。理由：檢查節點也會出錯，需要被驗證。</li>
</ol>
<p>還沒解決的限制：依據檢查只能比對數字和英文名詞，中文敘述是否忠於 Wiki（例如「想搶走 Omnitrix」）目前仍要靠人工語意審閱；下一步可以加一個 LLM-as-judge 節點，逐句比對簡報與 Wiki 段落。</p>
</section>
"""
nav = f"""<a href="#home">繳交總覽</a><a href="{SLIDES}">教學簡報 ↗</a>
<div class="navh">Wiki</div><a href="#schema">Schema 規則</a>{nav_wiki}<a href="#facts">事實表 facts</a><a href="#sources">來源 sources</a>
<div class="navh">流程</div><a href="#graph">Loop / Graph</a><a href="#run">執行紀錄</a><a href="#reflect">反思</a>"""
out = f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ben 10 LLM Wiki 與作業報告</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0c1117;--panel:#141b24;--line:#253041;--ink:#e9eef4;--mute:#93a1b3;--acc:#8be36a;--acc2:#5cc8ff;--warn:#ffb84d}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 "Noto Sans TC",system-ui,sans-serif;display:flex;min-height:100vh}}
nav{{width:250px;flex:none;border-right:1px solid var(--line);padding:22px 14px;position:sticky;top:0;height:100vh;overflow:auto;background:#0a0e13}}
nav .brand{{font-weight:900;font-size:18px;margin:0 8px 14px}}nav a{{display:block;color:var(--mute);text-decoration:none;padding:5px 10px;border-radius:7px;font-size:14.5px}}
nav a:hover,nav a.on{{background:var(--panel);color:var(--ink)}}nav a.on{{box-shadow:inset 3px 0 var(--acc)}}.navh{{font-size:12px;letter-spacing:.12em;color:#5d6b7d;margin:16px 10px 4px}}
main{{flex:1;min-width:0;padding:40px 56px 80px;max-width:1080px}}
.view{{display:none}}.view.on{{display:block}}
h1{{font-size:34px;line-height:1.25;margin:.2em 0 .6em}}h2{{font-size:22px;margin:1.8em 0 .6em;color:var(--acc)}}
.kicker{{color:var(--acc);letter-spacing:.14em;font-size:13px}}.crumb{{color:#5d6b7d;font-size:13px;font-family:monospace}}
.lead{{font-size:18px;color:#cfd8e3}}a{{color:var(--acc2)}}a.src{{font-size:12px;text-decoration:none;background:#1b2836;border-radius:4px;padding:0 4px;margin-left:2px}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:14.5px}}th,td{{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}}th{{background:var(--panel)}}
code{{background:#1b2430;padding:1px 6px;border-radius:5px;font-size:13.5px}}
pre{{background:#070a0e;border:1px solid var(--line);border-radius:10px;padding:14px;font-size:12.5px;line-height:1.55;overflow:auto;white-space:pre-wrap}}
details{{margin:10px 0}}summary{{cursor:pointer;color:var(--ink);font-weight:500}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px;margin:26px 0}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;text-decoration:none;color:var(--ink);display:flex;flex-direction:column;gap:6px}}.card:hover{{border-color:var(--acc)}}.card span{{color:var(--mute);font-size:14px}}
.st{{font-size:12px;padding:1px 8px;border-radius:99px}}.verified{{background:#1d3a20;color:#a9f08c}}.resolved{{background:#3a311b;color:#ffd38a}}.excluded{{background:#3a1e22;color:#ff9aa2}}
.mute{{color:var(--mute)}}.svgwrap{{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:10px;overflow:auto}}.svgwrap svg{{width:100%;min-width:760px;height:auto}}
.flow{{background:var(--panel);border-radius:10px;padding:14px 18px}}blockquote{{border-left:3px solid var(--warn);margin:12px 0;padding:4px 14px;color:#e8d3a8}}
@media(max-width:820px){{body{{display:block}}nav{{position:static;width:auto;height:auto;border-right:0;border-bottom:1px solid var(--line)}}main{{padding:24px 18px}}}}
</style></head><body>
<nav><div class="brand">Ben 10 LLM Wiki</div>{nav}</nav>
<main>{body}</main>
<script>
function go(){{var h=location.hash.slice(1)||'home';var v=document.getElementById(h);if(!v||!v.classList.contains('view')){{h='home';v=document.getElementById('home');}}
document.querySelectorAll('.view').forEach(function(e){{e.classList.toggle('on',e===v)}});
document.querySelectorAll('nav a').forEach(function(a){{a.classList.toggle('on',a.getAttribute('href')==='#'+h)}});window.scrollTo(0,0);}}
addEventListener('hashchange',go);go();
</script></body></html>"""
(R/"report/index.html").write_text(out)
print("ok", len(out))
