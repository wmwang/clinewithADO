# gitnexus-exploring — 技術手冊

> **一句話摘要**：引導 Claude 透過 GitNexus MCP 工具系統性地探索、理解程式碼庫架構與執行流程。

**文件版本**：依據 SKILL.md 產出　**適用對象**：使用者 / 開發者

---

## 目錄

1. [技能概覽](#技能概覽)
2. [架構圖](#架構圖)
3. [執行流程](#執行流程)
4. [元件說明](#元件說明)
5. [使用指南](#使用指南)
6. [開發者指南](#開發者指南)
7. [注意事項與常見問題](#注意事項與常見問題)

---

## 技能概覽

| 欄位 | 說明 |
|------|------|
| **技能名稱** | `gitnexus-exploring` |
| **觸發關鍵字** | "How does X work?", "What calls this function?", "Show me the auth flow", "What's the project structure?", "Where is the database logic?", "Show me the main components" |
| **主要功能** | 透過 GitNexus MCP 工具讀取程式碼圖譜索引，以概念查詢、符號追蹤、執行流程追蹤三個層次回答「程式碼如何運作」的問題。 |
| **前置條件** | GitNexus 已建立索引（`npx gitnexus analyze`）；MCP 伺服器已啟動並可存取 `gitnexus://` 資源 |
| **產出物** | 文字說明：架構概覽、執行流程摘要、符號呼叫關係、原始碼位置 |
| **技術依賴** | GitNexus MCP（`gitnexus_query`、`gitnexus_context` 工具）、`gitnexus://` MCP 資源協定 |

### 這個 Skill 做什麼

`gitnexus-exploring` 是一個程式碼探索導引 skill。當使用者想了解某段程式碼如何運作、某個功能由哪些元件組成、或者整個專案的架構是什麼，這個 skill 會指引 Claude 依序使用 GitNexus 提供的 MCP 工具與資源，從「全局索引概覽」到「單一符號的360度檢視」，逐層縮小範圍並提供精確答案。

這個 skill 的核心價值在於：GitNexus 預先分析了整個程式碼庫並建立了呼叫圖（call graph）與執行流程（execution flows），因此 Claude 不需要對每個檔案進行全文搜尋，而是可以透過語意查詢直接命中相關流程，大幅減少 token 消耗並提升答案的準確性。

Skill 所定義的 5 步驟工作流程形成一個漏斗：先確認索引存在且為最新版本，再用概念查詢找到相關執行流程群，接著對關鍵符號做深度脈絡分析，最後讀取原始碼確認實作細節。這個「由寬到窄」的探索策略讓回答既有全局觀又有細節支撐。

---

## 架構圖

```
.claude/skills/gitnexus/gitnexus-exploring/
└── SKILL.md          # Claude 的執行指引（觸發條件 + 5 步驟工作流程）

元件關係：

┌────────────────────────────────────────────────────────┐
│                      SKILL.md                          │
│  (觸發條件 + 工作流程 + 工具使用範例)                   │
└──────────────────────────┬─────────────────────────────┘
                           │ 指引 Claude 呼叫
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────────────┐
│ MCP 資源讀取  │  │ gitnexus_query   │  │ gitnexus_context         │
│              │  │                  │  │                          │
│ gitnexus://  │  │ 概念語意搜尋      │  │ 單一符號360度脈絡         │
│ repo/.../    │  │ → 執行流程群      │  │ → 呼叫者/被呼叫者/流程   │
│ context      │  └──────────────────┘  └──────────────────────────┘
│ clusters     │
│ cluster/{n}  │           ↓ 共同指向
│ process/{n}  │  ┌──────────────────────────────────┐
└──────────────┘  │     GitNexus 程式碼圖譜索引        │
                  │  (呼叫圖 + 執行流程 + 符號資料庫)   │
                  └──────────────────────────────────┘
```

---

## 執行流程

### 主流程

```
使用者輸入探索請求
（例："How does authentication work?"）
        │
        ▼
┌───────────────────────────────────────┐
│  Step 1: 發現已索引的 repo             │
│  READ gitnexus://repos                │
│  → 取得可用 repo 名稱清單              │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│  Step 2: 讀取程式碼庫概覽             │
│  READ gitnexus://repo/{name}/context  │
│  → 符號數量、流程數量、索引新鮮度       │
└───────────────────┬───────────────────┘
                    │
          ┌─────────▼──────────┐
          │  索引是否為最新？   │
          └─────┬──────────┬───┘
            是  │          │  否（stale）
                │          ▼
                │   ┌──────────────────────┐
                │   │  提示使用者執行：      │
                │   │  npx gitnexus analyze │
                │   └──────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────┐
│  Step 3: 概念語意查詢                                  │
│  gitnexus_query({query: "<使用者想理解的概念>"})        │
│  → 回傳相關執行流程群（Processes）                     │
│  → 每個流程包含符號清單與檔案位置                      │
└───────────────────────────┬───────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────┐
│  Step 4: 關鍵符號深度脈絡分析                          │
│  gitnexus_context({name: "<symbol>"})                  │
│  → 呼叫者（Incoming calls）                            │
│  → 被呼叫者（Outgoing calls）                          │
│  → 參與的執行流程（Processes）                         │
└───────────────────────────┬───────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────┐
│  Step 5: 完整執行流程追蹤（選用）                      │
│  READ gitnexus://repo/{name}/process/{processName}    │
│  → 逐步執行追蹤（Step-by-step trace）                  │
│  → 讀取原始碼確認實作細節                              │
└───────────────────────────┬───────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  向使用者說明架構、   │
                │  流程與元件關係       │
                └───────────────────────┘
```

---

## 元件說明

### 檔案清單

| 檔案 | 類型 | 功能說明 |
|------|------|---------|
| `SKILL.md` | 指令文件 | Claude 的執行指引：觸發條件、5 步驟工作流程、工具與資源參考表、使用範例 |

### 工具與資源對照

| 工具 / 資源 | 類型 | 說明 | 回傳大小估計 |
|------------|------|------|-------------|
| `gitnexus://repo/{name}/context` | MCP 資源 | 程式碼庫統計資訊與索引新鮮度警告 | ~150 tokens |
| `gitnexus://repo/{name}/clusters` | MCP 資源 | 所有功能區域清單與凝聚力分數 | ~300 tokens |
| `gitnexus://repo/{name}/cluster/{name}` | MCP 資源 | 特定功能區域的成員與檔案路徑 | ~500 tokens |
| `gitnexus://repo/{name}/process/{name}` | MCP 資源 | 特定執行流程的逐步追蹤 | ~200 tokens |
| `gitnexus_query` | MCP 工具 | 概念語意搜尋，回傳相關執行流程群 | 依結果而異 |
| `gitnexus_context` | MCP 工具 | 單一符號的呼叫者、被呼叫者、所在流程 | 依符號而異 |

---

## 使用指南

### 快速開始

**場景 1：了解某個功能的完整運作方式**

```
使用者說：「How does payment processing work?」

Claude 會執行：
1. READ gitnexus://repo/my-app/context
   → 確認索引包含 918 個符號、45 個執行流程
2. gitnexus_query({query: "payment processing"})
   → 找到 CheckoutFlow、RefundFlow、WebhookHandler
3. gitnexus_context({name: "processPayment"})
   → 呼叫者：checkoutHandler、webhookHandler
   → 被呼叫者：validateCard、chargeStripe、saveTransaction
4. READ gitnexus://repo/my-app/process/CheckoutFlow
   → 取得逐步執行追蹤
5. 讀取 src/payments/processor.ts 確認實作細節

輸出：付款流程的架構說明、元件關係圖、呼叫鏈
```

**場景 2：找到某個函式的所有呼叫者**

```
使用者說：「What calls the validateUser function?」

Claude 會執行：
1. READ gitnexus://repo/{name}/context（確認索引新鮮）
2. gitnexus_context({name: "validateUser"})
   → 呼叫者：loginHandler、apiMiddleware
   → 被呼叫者：checkToken、getUserById
   → 參與流程：LoginFlow (step 2/5)、TokenRefresh (step 1/3)

輸出：validateUser 的完整呼叫關係與所在執行流程
```

**場景 3：了解專案的整體架構**

```
使用者說：「What's the project structure?」 或 「Show me the main components」

Claude 會執行：
1. READ gitnexus://repo/{name}/context（概覽：符號數、流程數）
2. READ gitnexus://repo/{name}/clusters
   → 列出所有功能區域（如 auth、payments、api、database）
3. 針對每個主要 cluster：READ gitnexus://repo/{name}/cluster/{clusterName}
   → 取得各區域的成員符號與檔案路徑

輸出：專案功能分區說明與各區域主要元件
```

### 使用技巧

- **先查概念再查符號**：用 `gitnexus_query` 找到相關流程後，再用 `gitnexus_context` 深入特定符號，比直接猜測符號名稱更有效率。
- **索引可能過時**：如果回傳的符號名稱或檔案路徑與實際程式碼不符，先執行 `npx gitnexus analyze` 重新建立索引。
- **context 資源是入口點**：每次探索都應從 `gitnexus://repo/{name}/context` 開始，它告訴你索引是否新鮮，以及整個程式碼庫的規模。
- **善用 process 資源**：`gitnexus://repo/{name}/process/{name}` 提供的逐步追蹤（每個約 200 tokens）比讀取整個原始碼更高效，適合快速理解執行路徑。

---

## 開發者指南

### 如何擴充這個 Skill

這個 skill 只有 `SKILL.md` 一個檔案，所有邏輯都在其中。擴充時直接修改該檔案。

#### 新增探索策略

```
想要新增「跨 repo 比較分析」的探索策略時，需要修改：
1. SKILL.md → 在 Workflow 區塊新增步驟
2. SKILL.md → 在 Resources 表格新增對應資源說明
3. SKILL.md → 在 Example 區塊補充使用範例
```

#### 修改觸發條件

SKILL.md 的 `description` 欄位控制 Claude 何時使用這個 skill：

```yaml
description: >
  Use when the user asks how code works, wants to understand architecture,
  trace execution flows, or explore unfamiliar parts of the codebase.
  新增觸發情境：例如「Explain the data model」、「Map the dependencies of X」
```

### 設計決策記錄

| 決策 | 選擇 | 原因 |
|------|------|------|
| 工作流程步驟數 | 5 步驟固定流程 | 從「發現 repo」到「讀取原始碼」形成完整漏斗，確保 Claude 不跳過索引新鮮度確認 |
| 索引新鮮度前置檢查 | Step 2 強制讀取 context 資源 | 過時索引會導致錯誤的符號位置，早期發現可避免後續誤導 |
| 不包含腳本檔案 | 僅 SKILL.md | 所有探索邏輯透過 MCP 工具完成，不需要本地腳本；保持 skill 輕量 |
| 英文為主 | 說明文件使用英文 | 與 GitNexus 工具回傳的資料語言一致，減少切換認知負擔 |

### 測試方式

在已有 GitNexus 索引的專案中，說出以下語句驗證 skill 是否正確觸發：

```
1. 「How does X work?」—— 應觸發 skill 並執行 5 步驟工作流程
2. 「What calls functionName?」—— 應執行 gitnexus_context
3. 「Show me the main components」—— 應讀取 clusters 資源
```

驗證指標：
- Claude 是否先讀取 `context` 資源（而不是直接 grep）
- 如果索引過時，是否提示執行 `npx gitnexus analyze`
- 回答是否引用了具體的執行流程名稱與符號位置

---

## 注意事項與常見問題

### 已知限制

- **索引必須事先建立**：這個 skill 完全依賴 GitNexus 索引，若索引不存在或未啟動 MCP 伺服器，所有工具呼叫都會失敗。
- **符號名稱需精確**：`gitnexus_context` 的 `name` 參數需要與程式碼中的實際符號名稱完全匹配，拼寫錯誤會回傳空結果。
- **索引可能落後於最新程式碼**：每次提交後需重新執行 `npx gitnexus analyze` 才能反映新增或刪除的符號。

### 常見錯誤

| 錯誤情境 | 原因 | 解決方法 |
|---------|------|---------|
| `gitnexus_query` 回傳空結果 | 查詢詞與索引中的概念不匹配，或索引過時 | 嘗試不同的關鍵字；若仍無結果執行 `npx gitnexus analyze` |
| `gitnexus_context` 找不到符號 | 符號名稱拼寫錯誤，或該符號不在索引中 | 先用 `gitnexus_query` 找到正確的符號名稱 |
| context 資源顯示 "Index is stale" | 程式碼有更新但索引尚未重建 | 在終端機執行 `npx gitnexus analyze` |
| MCP 工具呼叫失敗 | GitNexus MCP 伺服器未啟動 | 確認 MCP 伺服器設定並重啟 Claude 工作階段 |
