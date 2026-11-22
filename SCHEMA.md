# Ben 10 LLM Wiki — Schema（給 LLM 的維護規則）

這份檔案是 LLM 維護 Wiki 的「規則書」，每次 ingest / query / lint 前都先讀。

## 三層結構
1. `raw/`：原始資料層。`sources.yaml` 登錄每篇來源，`notes.md` 是逐篇改寫摘要。**不可修改原意，只能追加。**
2. `wiki/`：知識層。LLM 撰寫的主題頁面，每頁頂端有 frontmatter（title / sources / updated）。
3. `wiki/facts.yaml`：事實表。所有「數字、日期、名稱」類的關鍵事實集中在這裡，每條都要有 `sources` 和 `status`。

## 事實 status 規則
- `verified`：至少 1 個 high 可信來源，且沒有其他來源矛盾。
- `resolved`：來源之間有衝突，已在 `wiki/conflicts.md` 寫下裁決理由。
- `excluded`：無法用 high 來源證實 → **簡報不可使用**。

## 頁面規則
- 每個段落的事實要加 `[S#]` 來源標記；只能用 `raw/sources.yaml` 有登錄的 ID。
- 頁面之間用 `[[page-name]]` 互相連結，連結目標必須存在。
- 低可信來源（X#）只能出現在 `conflicts.md`，不能當作事實依據。

## 三種操作
- **Ingest**：新資料 → 寫進 raw → 更新相關 wiki 頁與 facts.yaml → 跑 lint → 記一筆 log。
- **Query**：回答問題（例如「簡報第 3 頁要講什麼」）時，只能用 wiki 頁與 facts.yaml，答案要附上 fact key。
- **Lint**：`python3 tools/lint_wiki.py`，檢查來源標記、斷鏈、缺 status、衝突未裁決。
