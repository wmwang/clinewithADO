# Report Package

## Output root

預設將成果放在：

`<target-path>/.legacy-analysis/<YYYYMMDD>-<slug>/`

如果使用者沒有指定檔名，沿用以下結構。

## Required Markdown files

### `00-overview.md`

必含內容：
- 分析範圍與排除範圍。
- 專案類型、主要資料夾、核心檔案數量。
- 最重要的 5 到 10 個觀察。
- 建議接手工程師先讀的模組順序。

### `01-project-map.md`

必含內容：
- 子專案目錄樹摘要。
- project file、form、module、class 的分群。
- 哪些檔案是 UI、資料存取、共用邏輯、批次、整合。
- 高耦合區與共享模組。

### `02-entrypoints-and-flows.md`

必含內容：
- 每個 entry point 的用途。
- entry point 到下游函式的主要呼叫鏈。
- 每條鏈的終點是資料庫、檔案、外部服務、或純計算。
- 對每條鏈標示 `inventory-derived` 或 `confirmed-by-read`。

### `03-function-relationships.md`

必含內容：
- 重要 function 群組與責任摘要。
- fan-in / fan-out 高的函式。
- 共用函式、跨 form 共用邏輯、重複規則。
- 對每個重要函式附檔案與行號，並指出 caller / callee / side effects。

### `04-data-access.md`

必含內容：
- 使用到的資料庫、connection boundary、交易處理方式。
- SQL 操作對應到哪個函式與資料表。
- 可能的預存程序、檔案 I/O、外部介接。
- 不安全 SQL、交易範圍不清、共用連線等風險。

### `05-ui-and-form-behavior.md`

**模式 A 輸出路徑**：`.legacy-code-analyzer/{frm-name}/05-ui-and-form-behavior.md`
**模式 B 輸出路徑**：`<target-path>/.legacy-analysis/<YYYYMMDD>-<slug>/05-ui-and-form-behavior.md`

檔案結構（模式 A 固定格式）：

```
## Form 佈局示意

+--[ Form Caption ]---...---+
| ...（ASCII 圖）...         |
+---------------------------+

> ⚠️ 圖為 AI 模擬示意，可能失真，請以實際 OMI 程式呈現為主。

---

## 功能說明
...
```

ASCII 佈局規則：
- 按控制項的 `Top`/`Left` 座標由上到下、由左到右排列。
- 使用控制項的 `Caption`（按鈕、Label）或 `Name`（TextBox、ComboBox）標示。
- DataGrid / ListView 用框線加欄位名稱表示。
- 不需要精確像素，重點是讓人一眼看懂表單布局與操作動線。

功能說明必含內容（以 SA 角度、**繁體中文**白話撰寫）：
- 這個 Form 的用途（一句話說清楚）。
- 使用者操作流程（步驟描述，不是程式碼）。
- 每個按鈕/動作背後在做什麼（白話語意，非函式名稱）。
- DB 操作：查哪些表、取什麼資料、更新什麼欄位。
- CORBA 呼叫（`Tx*` / `TSMC_tx*`）：白話說明業務意義。
- 畫面狀態與全域狀態的耦合風險。
- 哪些邏輯有風險（無驗證、直接刪除、共用全域物件等）。

> 模式 A 不需另外建立 `05b-form-ascii-layout.txt`，ASCII 圖與說明整合在同一檔案。

### `06-java-ca-api-spec.md`

**模式 A 輸出路徑**：`.legacy-code-analyzer/{frm-name}/06-java-ca-api-spec.md`
**模式 B 輸出路徑**：`<target-path>/.legacy-analysis/<YYYYMMDD>-<slug>/06-java-ca-api-spec.md`

依照 [references/java-ca-spec.md](java-ca-spec.md) 的模板，為 Form 的業務邏輯產出完整的 Java Clean Architecture API 規格。全文使用**繁體中文**撰寫說明文字。

必含內容：
- 模組名稱與業務邊界說明。
- 每個業務動作對應的 API Endpoint（HTTP method、path、summary）。
- 每個 endpoint 對應的 Use Case（介面名稱、方法簽名、input command/query、output response）。
- **Request / Response 欄位用表格呈現**（欄位名稱、型別、必填、說明）。
- Domain Entity 定義（欄位、業務規則）。
- Repository 介面（out port，僅列方法簽名，不含 SQL）。
- CORBA / 外部系統呼叫對應的 Integration Adapter 介面（out port）。
- 各層對應的 package 路徑（依團隊慣例）。

Spring CA mapping lens（Ports & Adapters）：
- UI event handler / 表單命令 → `adapter/in/controller/` Controller endpoint
- 跨多 repository 流程協調 → `usecase/impl/` Use Case（實作 `usecase/ports/in/` 介面）
- 純計算、驗證、資格判斷 → `domain/` Domain Service 或 policy object
- SQL / JPA 資料存取 → `adapter/out/jdbc/` 或 `adapter/out/jpa/`（實作 `usecase/ports/out/` 介面）
- CORBA 呼叫（`Tx*` / `TSMC_tx*`）→ `adapter/out/corba/` Integration Adapter（實作 `usecase/ports/out/` 介面）
- 批次、Timer → Scheduler / Batch job

### `07-open-questions.md`

必含內容：
- 尚未驗證的呼叫關係。
- 缺檔、動態呼叫、外部 DLL、反射、巨集等阻礙。
- 需要 SME 或業務確認的規則。
- 下一輪建議分析順序。

## Required artifacts

### `artifacts/inventory.json`

保留完整 inventory，至少包含：
- `project_files`
- `source_files`
- `functions`
- `call_edges`
- `sql_operations`
- `ui_controls`

### `artifacts/function-index.csv`

建議欄位：

`function_id,qualified_name,file,language,container,visibility,kind,start_line,end_line,is_event_handler,params,return_type,fan_in,fan_out,called_names,tables,sql_ops`

### `artifacts/call-edges.csv`

建議欄位：

`source_id,target_id,source_qualified_name,target_qualified_name,callee_name,qualifier,confidence,reason,evidence`

### `artifacts/sql-operations.csv`

建議欄位：

`function_id,qualified_name,file,sql_ops,tables`

### `artifacts/ui-controls.csv`

建議欄位：

`file,container,control_name,control_type,caption,source`

## Writing rules

- 報告用使用者當前語言；如果使用者沒指定，預設用繁體中文。
- 所有重要結論都要有檔案與行號。
- `confirmed` 與 `inferred` 必須分開寫。
- 寫出風險，不要只寫功能。
- 避免把整段原始碼大量貼進報告；用摘要、流程與引用說明。
