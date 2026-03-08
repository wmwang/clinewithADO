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

必含內容：
- 每個 form 或主要畫面的用途。
- 控制項與事件對應到哪些處理函式。
- 畫面狀態與全域狀態的耦合。
- 使用者操作流程與背後資料處理。

### `06-spring-migration-candidates.md`

必含內容：
- 建議拆出的 Controller / endpoint candidates。
- 建議拆出的 Application Service、Domain Service、Repository、Batch、Integration Adapter。
- 每個候選元件對應哪些 legacy functions。
- 哪些邏輯不適合直接搬，需要先解耦或補測試。

Spring mapping lens:
- UI event handler 或表單命令通常是 Controller 或 command endpoint 的候選入口。
- 跨多個 repository 的流程協調通常是 Application Service。
- 純計算、驗證、資格判斷通常是 Domain Service 或 policy object。
- SQL helper、資料表 CRUD、外部查詢通常是 Repository 或 Gateway。
- Timer、批次啟動、固定週期工作通常是 Scheduler / Batch job。
- COM、ActiveX、檔案交換、外部系統呼叫通常是 Integration Adapter。

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
