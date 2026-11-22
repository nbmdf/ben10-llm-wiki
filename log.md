# Wiki 操作紀錄（log）— 2026-11-22 實際執行一次

| # | 時間 | 節點 | 動作 | 結果 |
|---|------|------|------|------|
| 1 | 23:18 | 討論 Discuss | 提出 4 個候選主題（MQTT 安全、IoT 威脅建模、AI Agents、零信任 IoT） | 使用者改選「Ben 10」；議定讀者＝完全沒看過的人、簡報目標＝看完知道故事/道具/作品順序/怎麼入坑 |
| 2 | 23:20 | 取得 Acquire | 5 次搜尋 + 5 次整頁擷取 | 3 頁擷取成功；2 頁（Omnitrix、2016 版）被擷取白名單拒絕 → 退回用搜尋摘要，sources.yaml 標 method: snippet |
| 3 | 23:24 | 匯入 Ingest | 寫入 raw/sources.yaml、raw/notes.md | 9 個可作依據來源（S1–S9）＋4 個低可信比對用來源（X1–X4） |
| 4 | 23:24 | 匯入 Ingest（交叉比對） | 每個數字跟所有來源比對 | 發現 8 個衝突 C1–C8（首播日、集數、電影數、「最長壽」說法、60 億美元零售額…），寫入 conflicts.md |
| 5 | 23:26 | 編譯 Compile | 9 個 wiki 頁、facts.yaml 34 條事實 | — |
| 6 | 23:27 | Wiki Lint #1 | `lint_wiki.py` | **4 ERROR / 3 WARN**：frontmatter 來源與內文不一致 ×3、電影年份缺來源標記 ×2、事實值未出現在任何頁 ×1 |
| 7 | 23:28 | 人工審閱 | 逐行對照 raw notes | 再找到 3 處 lint 抓不到的：「怪獸週冒險」（來源沒有）、「從墜落外星艙掉出」（混入低可信來源）、Azmuth 句沒有來源 |
| 8 | 23:28 | Wiki Lint #2 | 修正後重跑 | 0 ERROR / 0 WARN ✅ |
| 9 | 23:29 | 查詢 Query | 寫 slides/outline.yaml：14 頁，每頁＝一個學習者問題＋wiki 頁＋fact keys | — |
| 10 | 23:31 | 生成 Generate v1 | 依 outline 產生 slides/index.html | — |
| 11 | 23:32 | Grounding Check #1 | `check_slides.py` | **47 ERROR**，分類：Query 漏宣告事實 24、檢查器自身誤判 17、生成時多編內容 6 |
| 12 | 23:34 | 修正 | 修檢查器（逐文字節點比對、剔除含數字的專有名詞）、補 outline 事實、Wiki 補 Cannonbolt（回到 Compile）、刪掉沒依據的句子 | — |
| 13 | 23:34 | 人工語意審閱 | 對照 wiki 逐句看 | 再刪 3 句沒依據的話（Vilgax「想搶 Omnitrix」、Gwen「聰明」、「爺爺失蹤」不在 wiki 頁）；Max 改成「半退休成員」 |
| 14 | 23:35 | Grounding Check #2 | 重跑 | 0 ERROR ✅ |
| 15 | 23:35 | 突變測試 | 故意塞入「60 億美元」與不存在的名詞 | 3/3 被抓到 ✅（確認檢查器沒有變太鬆） |
| 16 | 23:36 | Render Check #1 | headless Chrome 截圖 14 頁 | 0 issue，**但目視發現**：大半頁空白、時間軸文字被裁切、兩頁頁腳過期 → 檢查器有盲點 |
| 17 | 23:38 | Render Check #2–#4 | 加入垂直裁切、內容填滿率、頁腳一致性檢查；調整版面 | #2：2 issue → #3：1 issue → #4：0 ✅ |
| 18 | 23:40 | 前移檢查 | 新增 `check_outline.py`，在生成前檢查大綱 | 0 ERROR ✅ |
| 19 | 23:41 | 發布 Publish | 簡報與 Wiki 發布為網頁 | ✅ |
