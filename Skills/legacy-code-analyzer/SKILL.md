---
name: legacy-code-analyzer
description: 深度分析 VB6、VB.NET、C# 舊系統或 monorepo 式 legacy codebase，輸出可交接、可移轉、可追函式關聯的報告與 artifacts。當使用者要盤點舊專案、理解指定子專案或資料夾、整理 GUI form 與模組邏輯、追查 function call 關係、找資料庫/UI/批次到 API 的對應、為 Java Spring 或其他新架構移轉做準備時，務必使用此技能。即使使用者只提供路徑並說「幫我看這個專案」、「整理這個子系統」、「做移轉分析」、「列出函式關係」或「這個 form 在幹嘛」也要觸發。
---

# Legacy Code Analyzer

分析單一 legacy 子專案，建立可驗證的程式邏輯盤點，讓接手工程師能快速理解目前行為並規劃移轉。

## Workflow

1. Confirm the exact scope.
- 預設只分析使用者指定的子專案路徑，不要擅自掃整個 monorepo。
- 如果路徑內還有多個 project 或 form 群，先列出候選範圍，再請使用者定義本輪分析對象；如果使用者已明確給出子專案路徑，直接進行。
- 記錄這次分析的焦點：整體盤點、特定表單、資料庫流程、批次/排程、或 Spring API 移轉。

2. Build a low-cost inventory before reading code deeply.
- 先執行：

```bash
python3 Skills/legacy-code-analyzer/scripts/build_inventory.py "<target-path>" --output "<target-path>/.legacy-analysis/inventory"
```

- 先讀 `inventory_summary.md`，再視需要讀 `inventory.json`、`function-index.csv`、`call-edges.csv`、`sql-operations.csv`、`ui-controls.csv`。
- 用 inventory 決定閱讀順序，先看 entry points、UI form、資料存取模組、共用 business modules，再看邏輯密度高的函式。
- 如果環境無法執行腳本，手動建立等價 inventory，並在報告裡註明哪些欄位是人工整理。

3. Split the work aggressively when subagents are available.
- 使用支援 subagent 的 agent 時，優先分拆，不要把所有檔案一次塞進單一 context。
- 依 [references/subagent-workflow.md](references/subagent-workflow.md) 將任務切成 UI/表單、業務邏輯、資料存取、整合/外部依賴、移轉映射。
- 每個子代理只拿自己需要的 inventory 片段與相關檔案。
- 主代理只負責下發任務、整併 findings、去重、補交叉引用、標示 confirmed vs inferred。
- 沒有 subagent 時，仍依相同分區順序逐段分析。

4. Produce a report package, not a single prose blob.
- 預設輸出到 `<target-path>/.legacy-analysis/<YYYYMMDD>-<slug>/`。
- 具體輸出格式與檔名，照 [references/report-package.md](references/report-package.md)。
- 除了 Markdown 報告，務必保留 CSV/JSON artifacts，方便後續再餵給 AI 或人工查核。
- 若使用者另外要求 HTML 或 PDF，再從 Markdown 轉出摘要版，不要把 HTML 當唯一成果。

## Analysis priorities

1. Map entry points and execution flow.
- 找出 `Form_Load`、`Click`、`Change`、menu handlers、batch entry methods、public service methods、以及專案啟動點。
- 對每個 entry point 追到主要 downstream functions，至少標示 2 到 4 層呼叫鏈，直到資料庫、檔案 I/O、外部系統或明確的 business rule。

2. Separate behavior from scaffolding.
- Designer、auto-generated、bootstrap、constant-only files 可保留摘要，不要浪費篇幅。
- 將分析深度集中在規則判斷、資料轉換、查詢封裝、交易處理、錯誤處理、共用 utility。

3. Classify each important function.
- 至少標示：所在檔案、容器、責任、輸入、輸出、依賴、被誰呼叫、呼叫了誰、資料表或外部資源、副作用、可信度。
- 明確區分「直接證據」與「根據命名/上下文推論」。

4. Extract migration-relevant seams.
- 將 legacy 函式映射到未來可能的 Spring 元件：Controller entrypoint、Application Service、Domain Service、Repository、Batch job、Integration adapter。
- 指出 transaction boundary、shared global state、UI state coupling、同步/非同步假設、例外處理缺口。
- 如果邏輯看起來不應直接搬成 API，說明原因，例如高度耦合 UI、依賴全域物件、SQL 與畫面事件混雜。

## Coverage rules

- 專案很大時，先按資料夾、namespace、form 群、模組群分批。
- 先完整覆蓋高風險區：接資料庫、對帳/金額/庫存/狀態轉換、刪除/取消/結帳、登入/權限。
- 對未完整讀完的部分，列在 `07-open-questions.md`，不要假裝已完全理解。
- 發現重名函式、動態呼叫、COM/ActiveX、反射、巨集或外部 DLL 時，明確標記為 call graph 風險點。

## Evidence rules

- 每個重要結論都附檔案與行號。
- 關聯圖若來自腳本 heuristics，標記為 `inventory-derived`；若來自實際閱讀函式內文，標記為 `confirmed-by-read`。
- 不要輸出 connection string 密碼、token 或個資。只保留伺服器、資料庫、系統邊界等安全摘要。
- 不懂的地方直接寫 `待確認`，附上建議下一步。

## Large-project fallback

當子專案仍然太大時：

1. 先用 inventory 列出前 20 個最值得深讀的檔案。
2. 優先深讀所有 entry point 與其第一圈依賴。
3. 再讀 SQL 最多、被呼叫次數最高、或同時被多個 form 共用的函式。
4. 明確分出「已驗證主流程」與「尚未深讀的邊角流程」。

## Final checklist

- 已限定分析範圍到單一子專案或明確的目錄集合。
- 已產出結構化 artifacts。
- 已說明主要功能群與 entry points。
- 已列出重要 function 關係與 call chain。
- 已整理資料表與外部依賴。
- 已提供對 Spring API 移轉有用的 mapping 與風險。
- 已標出不確定處與後續建議。
