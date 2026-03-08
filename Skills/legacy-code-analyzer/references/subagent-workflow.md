# Subagent Workflow

## Split by workstream, not by random file chunks

先用 inventory 分群，再把每群交給不同子代理。優先切法：
- UI / Forms
- Business Logic
- Data Access / SQL
- Integration / Batch / External dependencies
- Spring Migration Mapping

每個子代理都只拿：
- 它負責的檔案清單。
- 對應的 `inventory.json` 片段或 CSV 摘要。
- 明確 deliverables。

## Standard subagent roles

### 1. Structure mapper

Goal:
- 先把子專案切成幾個責任區。

Input:
- `inventory_summary.md`
- `function-index.csv`
- `call-edges.csv`
- project files 與目錄樹

Deliverables:
- 模組分群
- entry point 清單
- 熱點檔案清單
- 建議閱讀順序

### 2. UI / form analyst

Goal:
- 解釋畫面、事件、操作流程與背後呼叫鏈。

Input:
- 所有 form 檔
- `ui-controls.csv`
- 與 form 直接相依的 modules/classes

Deliverables:
- 每個 form 的用途
- control / event / function 對照
- 主要使用者流程
- UI state coupling 風險

### 3. Logic and call-graph analyst

Goal:
- 確認重要 business rules 與 function 關係。

Input:
- fan-out / fan-in 高的函式
- 共用 modules
- 計算、驗證、狀態轉換相關檔案

Deliverables:
- 主要規則摘要
- 重要函式呼叫鏈
- 共用邏輯與重複邏輯
- 哪些 call edges 已確認、哪些仍是 heuristics

### 4. Data / integration analyst

Goal:
- 找出資料表、交易、檔案 I/O、外部系統邊界。

Input:
- SQL 重的 modules/classes
- `sql-operations.csv`
- connection / repository / helper 類檔案

Deliverables:
- table / function map
- transaction boundaries
- side effects
- 風險與安全注意事項

### 5. Spring migration mapper

Goal:
- 將前述 findings 映射到未來 Spring 架構。

Input:
- 前四類子代理的輸出
- `03-function-relationships.md`
- `04-data-access.md`
- `05-ui-and-form-behavior.md`

Deliverables:
- controller / service / repository candidates
- endpoint 或 use-case 命名建議
- 需要先解耦的 legacy patterns
- 缺少測試或規格的高風險點

## Prompt contract for each subagent

每個子代理任務都應明確包含：
- 分析範圍。
- 必讀 artifacts。
- 必讀原始碼檔案。
- 期望輸出檔名。
- 必須區分 `confirmed` 與 `inferred`。
- 必須附檔案與行號。

## Merge protocol for the main agent

- 先去重相同函式與相同 SQL observation。
- 發現不同子代理結論衝突時，保留兩者並標記衝突來源。
- 把所有 cross-reference 補成穩定名稱，例如 `frmOrderList.btnCancel_Click -> DatabaseHelper.CancelOrder`。
- 若某些結論只有 inventory 支撐，標註 `inventory-derived`，不要冒充為已讀碼驗證。

## No-subagent fallback

若平台沒有 subagent：
- 沿用相同分區順序。
- 每次只讀一個責任區。
- 完成一區就先落盤成報告檔，再進下一區。
