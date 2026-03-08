# Legacy Code Analyzer 使用者手冊

> 目的：協助工程師針對 **指定子專案** 做 VB6 / VB.NET / C# 舊系統盤點，產出可交接、可驗證、可支援移轉到 Java Spring API 的分析報告包。

---

## 這個 skill 能做什麼

`legacy-code-analyzer` 適合處理這類場景：

- 大型舊系統像 mono repo，一個資料夾就是一個子專案、form 或模組群。
- 新接手工程師不知道某個子系統在做什麼。
- 要先盤點舊邏輯，再規劃移轉到 Java Spring API。
- 需要追查 form 事件、module function、SQL、共用邏輯之間的關係。
- 希望把分析結果保留成 Markdown + CSV/JSON artifacts，方便後續再餵給 AI 或人工核對。

這個 skill 不主張一次吞完整個 legacy repo。預設做法是：

1. 先鎖定單一子專案路徑。
2. 先做 inventory。
3. 再分區深讀。
4. 最後輸出報告包。

---

## 使用前準備

開始前，盡量準備這些資訊：

- 要分析的子專案路徑。
- 這一輪最關心的焦點。
  - 例：整體盤點、特定 form、資料庫流程、計價邏輯、批次、Spring API 移轉。
- 如果你知道高風險流程，也一起講。
  - 例：刪除、取消、結帳、登入、對帳、庫存調整。

如果你什麼都不知道，也沒關係。**至少提供路徑** 就能開始。

---

## 如何啟用

### 方式一：自然語言觸發

直接對 agent 說：

- `幫我分析這個 VB6 子專案：/path/to/project`
- `我剛接手這個 .NET 舊系統，請整理 function 關係`
- `請盤點這個 form 對應到哪些資料庫操作`
- `這個子系統未來要改成 Spring API，幫我做移轉分析`

### 方式二：顯式指定 skill

如果你的 agent 支援顯式 skill 語法，可直接寫：

```text
Use $legacy-code-analyzer to inspect /path/to/project and map function relationships for Spring migration.
```

---

## 標準使用流程

### 步驟 1：指定分析範圍

請明確提供一個子專案路徑。

推薦說法：

```text
請只分析這個子專案，不要掃整個 repo：
/Users/me/work/legacy-system/OrderModule
```

如果是大型 monorepo，**不要一開始就丟根目錄**。先切一個子系統、一個 form 群或一個模組群。

### 步驟 2：補充分析焦點

你可以加一句說明這次要解決什麼問題：

- `我要讓新接手工程師看得懂`
- `我要知道主要 function call chain`
- `我要找 UI 到 SQL 的對應`
- `我要拆成 Spring controller/service/repository`

### 步驟 3：讓 agent 先做 inventory

skill 會先跑低成本掃描，建立：

- `inventory.json`
- `function-index.csv`
- `call-edges.csv`
- `sql-operations.csv`
- `ui-controls.csv`

這一步的目的是避免 context 一次爆掉。

### 步驟 4：深度分析

agent 會根據 inventory 分段分析：

- UI / Forms
- Business Logic
- Data Access / SQL
- Integration / 外部依賴
- Spring Migration Mapping

如果平台支援 subagent，建議讓它分工後再整併。

### 步驟 5：閱讀報告包

最終輸出通常會放在：

```text
<target-path>/.legacy-analysis/<YYYYMMDD>-<slug>/
```

---

## 建議 prompt 範本

### 1. 基本盤點

```text
請只分析這個 VB6 子專案：
/path/to/project

我要一份給接手工程師看的詳細盤點，包含主要 form、function 關係、資料庫操作與 open questions。
```

### 2. 追 form 事件到 SQL

```text
請分析這個子專案：
/path/to/project

重點放在表單事件、背後呼叫的 modules/functions，以及最後碰到哪些資料表。
```

### 3. 為 Spring API 移轉做盤點

```text
請只分析這個子專案：
/path/to/project

目標是未來移轉到 Java Spring API。
請整理主要 entry points、function call chain、SQL 與可拆分的 controller/service/repository 候選。
```

### 4. 只看高風險流程

```text
請分析這個子專案：
/path/to/project

先只看高風險流程：取消、刪除、庫存調整。
我要知道這三條流程各自會呼叫哪些 function、碰哪些資料表、有哪些移轉風險。
```

---

## 報告包內容說明

預設會產出以下文件：

### `00-overview.md`

你先看這份，快速掌握：

- 這次分析範圍。
- 主要模組與風險。
- 建議先閱讀哪些檔案。

### `01-project-map.md`

用來看：

- 子專案底下有哪些 form、module、class。
- 哪些檔案負責 UI、SQL、共用邏輯、外部整合。

### `02-entrypoints-and-flows.md`

用來看：

- `Form_Load`、`Click`、批次入口、public methods 等 entry points。
- 每個入口往下會走到哪些 function。

### `03-function-relationships.md`

用來看：

- 哪些 function 是核心。
- 哪些 function 被大量共用。
- 哪些 function 是主要 orchestrator。

### `04-data-access.md`

用來看：

- SQL 在哪裡。
- 哪些 function 對應哪些資料表。
- 哪裡有 transaction、共用 connection 或潛在風險。

### `05-ui-and-form-behavior.md`

用來看：

- 每個 form 的用途。
- 控制項 / 事件 / function 對照。
- 使用者操作流程。

### `06-spring-migration-candidates.md`

用來看：

- 哪些 legacy entry points 適合變成 API。
- 哪些邏輯適合拆成 service、domain service、repository。
- 哪些地方必須先解耦再移轉。

### `07-open-questions.md`

用來看：

- 哪些部分尚未確認。
- 哪些呼叫關係只是 heuristics。
- 下一輪應該補看什麼。

### `artifacts/`

這些是最重要的機器可讀資料：

- `inventory.json`
- `function-index.csv`
- `call-edges.csv`
- `sql-operations.csv`
- `ui-controls.csv`
- `connections.csv`

---

## 如何閱讀結果

### 如果你是新接手工程師

建議閱讀順序：

1. `00-overview.md`
2. `01-project-map.md`
3. `02-entrypoints-and-flows.md`
4. `05-ui-and-form-behavior.md`
5. `03-function-relationships.md`
6. `04-data-access.md`

### 如果你是要做移轉設計的人

建議閱讀順序：

1. `00-overview.md`
2. `02-entrypoints-and-flows.md`
3. `03-function-relationships.md`
4. `04-data-access.md`
5. `06-spring-migration-candidates.md`
6. `07-open-questions.md`

### 如果你只想快速找某個 function

先看：

- `artifacts/function-index.csv`
- `artifacts/call-edges.csv`

---

## 大型 monorepo 使用建議

### 原則一：一次只分析一個子專案

不要說：

```text
幫我看整個 legacy repo
```

請改成：

```text
先看 /legacy/OrderModule
下一輪再看 /legacy/InventoryModule
```

### 原則二：先抓高風險流程

如果專案很大，先盤點：

- 會改資料的流程
- 會算錢的流程
- 狀態轉換複雜的流程
- 有外部依賴的流程

### 原則三：善用 subagent

如果你的平台支援 subagent，可以明確要求：

```text
請把 UI、資料庫、業務邏輯分開分析，再整併成一份報告。
```

這樣通常比單一 context 更穩定。

---

## 手動執行 inventory

如果你想先自己產出 inventory，再交給 agent 深讀，可直接跑：

```bash
python3 Skills/legacy-code-analyzer/scripts/build_inventory.py "/path/to/project" --output "/path/to/project/.legacy-analysis/inventory"
```

建議先打開：

- `inventory_summary.md`
- `function-index.csv`
- `call-edges.csv`

---

## 常見問題

### Q1：這個 skill 會自動分析整個 repo 嗎？

不會。預設應該只分析你指定的子專案路徑。

### Q2：它畫出的 function 關係一定 100% 正確嗎？

不一定。inventory 的 call graph 是 heuristic，特別是遇到：

- 動態呼叫
- COM / ActiveX
- 外部 DLL
- reflection
- 巨集
- 重名函式

這些都需要人工再確認。

### Q3：它適合直接拿來產出最終設計文件嗎？

適合當「第一輪盤點與移轉前分析」。正式設計仍建議由工程師根據報告再收斂。

### Q4：如果分析結果太大怎麼辦？

縮小範圍，只看：

- 一個 form 群
- 一個業務流程
- 一個 module cluster
- 一個 migration slice

---

## 最佳實務

- 永遠先給明確的子專案路徑。
- 永遠說清楚這輪分析焦點。
- 大專案先做分批，不要一次全吞。
- 看報告時優先核對 `open questions` 與高風險流程。
- 要做 Spring 移轉時，不要只看 API 候選，也要看 shared state、transaction boundary、SQL 耦合。

---

## 一句話總結

這個 skill 最適合拿來做：**legacy 子專案盤點、function 關係整理、UI/SQL 對照，以及 Java Spring API 移轉前的分析準備。**
