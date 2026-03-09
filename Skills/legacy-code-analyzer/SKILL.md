---
name: legacy-code-analyzer
description: 深度分析 VB6、VB.NET、C# 舊系統或 monorepo 式 legacy codebase，輸出可交接、可移轉、可追函式關聯的報告與 artifacts。當使用者要盤點舊專案、理解指定子專案或資料夾、整理 GUI form 與模組邏輯、追查 function call 關係、找資料庫/UI/批次到 API 的對應、為 Java Spring Boot Clean Architecture 移轉做準備、分析單一 VB6 form 的行為時，務必使用此技能。即使使用者只提供路徑並說「幫我看這個專案」、「整理這個子系統」、「做移轉分析」、「列出函式關係」、「這個 form 在幹嘛」、「幫我把這個 form 轉成 Java API」或「畫出表單結構」也要觸發。
---

# Legacy Code Analyzer

分析 legacy 子專案或單一 VB6 form，建立可驗證的程式邏輯盤點，讓接手工程師能快速理解目前行為並規劃移轉至 Java Spring Boot Clean Architecture。

## 分析模式

**模式 A：單一 Form 深入分析**（使用者提供一個 `.frm` 檔，或說「分析這個 form」）
- 以指定的 `.frm` 為根，追蹤 3 層呼叫鏈
- 輸出 ASCII form layout、SA 角度說明、Java CA API 規格
- 不必掃整個專案，context 保持在單一 form 的相關範圍

**模式 B：子專案全盤分析**（使用者提供路徑或說「分析整個子專案」）
- 執行完整 inventory，依分區閱讀
- 輸出完整報告包（overview、entrypoints、functions、data access、migration）

若使用者只給一個 `.frm` 檔案路徑，預設使用**模式 A**。

---

## Workflow（模式 A：單一 Form）

### Step 1 — 解析 Form 結構，畫出 ASCII 佈局

讀取 `.frm` 檔，找出所有控制項（TextBox、ComboBox、Label、CommandButton、DataGrid 等）與其 `Caption`、`Name`、`TabIndex`、座標屬性（`Left`、`Top`、`Width`、`Height`），畫出近似的 ASCII 示意圖：

```
+--[ Form Caption ]------------------------------------------+
| 欄位標籤:  [TextBox Name____________]                      |
| 下拉選單:  [ComboBox▼              ]                       |
|                                                             |
| [CommandButton1]  [CommandButton2]  [CommandButton3]        |
+------------------------------------------------------------+
```

規則：
- 按 `Top`/`Left` 排列，由上到下、由左到右。
- 按鈕集中在底部或右側。
- `Caption` 用來顯示，沒有 Caption 就用 `Name`。
- 不需要精確像素，重點是讓人一眼看懂表單用途與操作流程。

輸出至：`05b-form-ascii-layout.txt`

---

### Step 2 — 辨識 Entry Points

從 `.frm` 找出所有事件處理函式：
- `Form_Load`、`Form_Activate`
- `btnXxx_Click`、`cmdXxx_Click`（按鈕點擊）
- `txtXxx_LostFocus`、`cboXxx_Change`（欄位事件）
- 工具列、選單 `mnuXxx_Click`

每個 entry point 記錄：按鈕/控制項標題、事件類型、對應函式名稱。

---

### Step 3 — 追蹤 3 層呼叫鏈

從每個 entry point 往下追，最多 3 層：

```
層 1：Form 的 Event Handler（_Click、_Load 等）
層 2：Event Handler 呼叫的 Module/Class 函式
層 3：那些函式再呼叫的下層函式（到 DB、CORBA、外部系統即停止）
```

若按鈕呼叫另一個 `.frm`（例如 `frmDetail.Show`），記錄為「開啟子表單 frmDetail」，不繼續往子表單內追（可另外啟動新一輪分析）。

對每層函式，標記：
- 所在檔案與行號
- 是否為 DB 操作（SQL 字串、ADO/DAO 呼叫）
- 是否為 CORBA 呼叫（見下方說明）
- 是否呼叫另一個 Form
- `confirmed-by-read` 或 `inventory-derived`

---

### Step 4 — 識別 CORBA 呼叫（白話說明）

凡函式名稱以 `Tx` 或 `TSMC_tx` 開頭，視為 **CORBA 遠端服務呼叫**。

處理方式：
1. 列出呼叫的 CORBA 方法名稱與傳入參數
2. 用白話說明這個呼叫「在做什麼」，例如：
   - `TxGetLotInfo(lotId)` → 「向製造執行系統查詢指定 Lot 的目前狀態與位置」
   - `TSMC_txTransferLot(lotId, toolId)` → 「通知系統將 Lot 移機台，觸發後續製程流程」
3. 不要只列函式名，要說明業務語意
4. 標記 CORBA 呼叫的輸出入參數，以便後續對應到 Java API 的 request/response

---

### Step 5 — 產出 SA 說明文件

以 SA（系統分析師）角度撰寫 `05-ui-and-form-behavior.md`，讓不懂舊程式的同事也能看懂：

- 這個 Form 的用途是什麼（一句話）
- 使用者操作流程（步驟描述，不是程式碼）
- 每個按鈕/動作背後在做什麼（白話）
- DB 查詢到哪些表、取什麼資料、更新什麼
- CORBA 呼叫代表什麼業務動作
- 哪些邏輯有風險（無驗證、直接刪除、共用全域變數等）

---

### Step 6 — 生成 Java Clean Architecture API 規格

根據分析結果，依照 `references/java-ca-spec.md` 的模板，為這個 Form 的業務邏輯產出 `06-java-ca-api-spec.md`：

- 每個重要業務動作（按鈕功能）對應一個 Use Case
- 產出 Controller endpoint、Use Case 定義、input port、output port、Domain entity、Repository interface
- 遵循團隊現有的 Ports & Adapters 架構（參見 `references/java-ca-spec.md`）
- CORBA 呼叫映射為 Integration Adapter（out port）
- DB 操作映射為 Repository（out port）

---

## Workflow（模式 B：子專案全盤）

1. Confirm the exact scope.
   - 預設只分析使用者指定的子專案路徑，不要擅自掃整個 monorepo。
   - 如果路徑內還有多個 project 或 form 群，先列出候選範圍，再請使用者定義本輪分析對象。

2. Build a low-cost inventory before reading code deeply.

```bash
python3 Skills/legacy-code-analyzer/scripts/build_inventory.py "<target-path>" --output "<target-path>/.legacy-analysis/inventory"
```

   - 先讀 `inventory_summary.md`，再視需要讀各 CSV。
   - 用 inventory 決定閱讀順序，先看 entry points、UI form、資料存取模組。
   - 環境無法執行腳本時，手動建立等價 inventory 並在報告裡標示。

3. Split the work aggressively when subagents are available.
   - 依 [references/subagent-workflow.md](references/subagent-workflow.md) 將任務切成 UI/業務邏輯/資料存取/整合/移轉映射。

4. Produce a report package.
   - 預設輸出到 `<target-path>/.legacy-analysis/<YYYYMMDD>-<slug>/`。
   - 具體格式照 [references/report-package.md](references/report-package.md)。

---

## Analysis priorities（共用）

1. Map entry points and execution flow.
   - 找出 `Form_Load`、`Click`、`Change`、menu handlers、batch entry methods。
   - 追到主要 downstream functions，標示終點（資料庫、CORBA、外部系統、純計算）。

2. Separate behavior from scaffolding.
   - Designer、auto-generated、constant-only 可保留摘要，不浪費篇幅。
   - 分析深度集中在規則判斷、資料轉換、查詢封裝、交易處理、CORBA 呼叫。

3. Classify each important function.
   - 至少標示：所在檔案、行號、責任、輸入、輸出、依賴、副作用、可信度。
   - 明確區分「直接證據（confirmed-by-read）」與「推論（inventory-derived）」。

4. Extract migration-relevant seams.
   - legacy 函式 → Spring CA 元件：Controller / Use Case / Domain Service / Repository / Integration Adapter。
   - 指出 transaction boundary、UI state coupling、全域物件依賴。
   - 若邏輯不宜直接搬，說明原因。

---

## 外部呼叫辨識規則

### CORBA 遠端服務呼叫（需要映射為 Integration Adapter）

| 特徵 | 判斷 |
|------|------|
| 函式名稱以 `Tx` 開頭 | CORBA 遠端呼叫 |
| 函式名稱以 `TSMC_tx` 開頭 | CORBA 遠端呼叫 |
| 呼叫 `.orb`、`ORB.init`、`_stub`、`_skel` | CORBA 底層 |
| 傳入/接收 IDL 型別（如 `READ_STR_T`） | CORBA 資料結構 |

每個 CORBA 呼叫必須：
1. 用白話說明業務語意（不只列函式名）
2. 記錄傳入參數與回傳結構
3. 在移轉文件中映射為 `adapter/out/corba/` Integration Adapter（out port）

### OMI 框架呼叫（移轉時直接捨棄，不需對應 Java 業務邏輯）

POSEIDON OMI 系統特有的框架函式，負責 UI 初始化、語系管理、程式生命週期：

| 函式前綴/名稱 | 用途 | 移轉處理 |
|-------------|------|---------|
| `OMI_PanelInit` | 初始化畫面面板顏色/樣式 | Spring 不需要，捨棄 |
| `OMI_fnReadString` / `OMI_ReadOneString` | 讀取多語系字串 | 改用 Spring i18n / MessageSource |
| `OMI_SwitchLanguage` | 切換介面語言 | Spring i18n 取代 |
| `OMI_SetPgmParm` | 設定程式結束狀態（ABORT/NORMAL） | API 改用 HTTP status code |
| `OMI_PgmEnd` | 終止整個 OMI 程式 | API 無對應，捨棄 |
| `OMI_ShowLogWindow` | 顯示系統日誌視窗 | 改用後端 logging（Logback/ELK） |
| `OMI_LBL_*` 常數 | 多語系字串 key | 移轉時整理為 i18n message key |

> 若在分析中遇到 `OMI_*` 呼叫，在報告裡標記為「OMI Framework（移轉時捨棄）」，不需要列入 Java CA 的 out port。

---

## Coverage rules

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

- 已確定分析模式（單一 Form / 全專案）與範圍。
- 已產出 ASCII form 佈局（模式 A）。
- 已說明主要功能群與 entry points（白話 SA 角度）。
- 已列出重要 function 關係與 call chain（最多 3 層）。
- 已識別並白話說明 CORBA 呼叫（Tx* / TSMC_tx*）。
- 已整理資料表與外部依賴。
- 已產出 Java CA API 規格（Controller / Use Case / Domain / Repository / Adapter）。
- 已標出不確定處與後續建議。
