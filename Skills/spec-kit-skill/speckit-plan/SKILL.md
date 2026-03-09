---
name: speckit-plan
description: 從 feature spec 產生實作規劃文件（research.md、data-model.md、contracts/）。不需安裝任何 CLI。
---
> **重要**：所有檔案讀寫操作均相對於使用者的 **project root（當前工作目錄）**，不是 skill 檔案所在路徑。如有疑慮，先執行 `pwd` 確認再操作。


## 使用者輸入

請考慮使用者在對話中提供的技術偏好或額外說明（如技術堆疊、框架選擇等）。

## 流程說明

### 步驟 1：找到當前 feature

```bash
git branch --show-current
```

- 分支符合 `[0-9]+-[a-z0-9-]+` → `FEATURE_DIR` = `specs/{BRANCH}`
- 否則：掃描 `specs/` 找最近修改的子目錄，或詢問使用者

確立變數：
- `BRANCH` = 當前 git 分支
- `FEATURE_DIR` = `specs/{BRANCH}`（絕對路徑）
- `FEATURE_SPEC` = `{FEATURE_DIR}/spec.md`
- `IMPL_PLAN` = `{FEATURE_DIR}/plan.md`

確認 `FEATURE_SPEC` 存在。若不存在：請使用者先使用 speckit-specify skill。

建立目錄：
```bash
mkdir -p specs/{BRANCH}/contracts
```

### 步驟 2：初始化 plan.md

若 `IMPL_PLAN` 不存在，使用以下結構建立：

```markdown
# 實作計畫：{功能名稱}

**分支**：`{BRANCH}` | **日期**：{今天} | **規格**：[spec.md](spec.md)

## 摘要

{主要需求 + 選定的技術方向}

## 技術背景

**語言/版本**：{例如 Python 3.11 | 待釐清}
**主要相依套件**：{例如 FastAPI、SQLAlchemy | 待釐清}
**儲存方式**：{例如 PostgreSQL | N/A}
**測試框架**：{例如 pytest | 待釐清}
**目標平台**：{例如 Linux server、瀏覽器 | 待釐清}
**專案類型**：{函式庫 / CLI / Web 服務 / 行動 App / 桌面 App | 待釐清}
**效能目標**：{例如 p95 < 200ms | 待釐清}
**限制條件**：{例如 離線可用、< 100MB 記憶體 | 待釐清}
**規模/範疇**：{例如 10k 用戶 | 待釐清}

## 憲法檢核

*關卡：在第 0 階段研究前必須通過。第 1 階段設計後重新確認。*

{依據 .specify/memory/constitution.md 的關卡，若無憲法則填「尚未定義憲法」}

## 專案結構

### 文件（此 feature）

\`\`\`
specs/{BRANCH}/
├── plan.md         ← 本檔案
├── research.md     ← 第 0 階段產出
├── data-model.md   ← 第 1 階段產出
├── quickstart.md   ← 第 1 階段產出
├── contracts/      ← 第 1 階段產出
└── tasks.md        ← speckit-tasks 產出
\`\`\`

### 原始碼

\`\`\`
{依技術堆疊的具體目錄樹}
\`\`\`

## 複雜度追蹤

> 僅在憲法檢核有需要說明的違規時填寫

| 違規項目 | 為何必要 | 拒絕更簡單方案的原因 |
|---------|---------|-------------------|
```

### 步驟 3：填寫技術背景

從現有 repo 檔案偵測技術堆疊：
- `package.json` → Node.js；查 `dependencies` 確認框架
- `pyproject.toml` / `setup.py` → Python
- `go.mod` → Go
- `Cargo.toml` → Rust
- `*.csproj` / `*.sln` → .NET
- `build.gradle` / `pom.xml` → Java/Kotlin

無法解析的項目標記為「待釐清」。

### 步驟 4：憲法檢核

讀取 `.specify/memory/constitution.md`（若存在）。評估每條原則的關卡，標記 通過 / 失敗 / 不適用。若失敗且在複雜度追蹤中未說明：ERROR。

### 步驟 5：第 0 階段 — 研究

針對技術背景中每個「待釐清」項目，進行研究並解析。

寫入 `{FEATURE_DIR}/research.md`：

```markdown
# 研究報告：{功能名稱}

**日期**：{今天}

## 決策

### {決策主題}

- **決定**：{選擇的選項}
- **理由**：{為什麼}
- **考量的替代方案**：{評估了什麼}

## 技術選型

{解析後的技術堆疊摘要}

## 關鍵發現

{限制條件、模式或風險}
```

### 步驟 6：第 1 階段 — 設計

**前提條件**：`research.md` 已完成。

**a. 資料模型** — 寫入 `{FEATURE_DIR}/data-model.md`：

```markdown
# 資料模型：{功能名稱}

## 實體

### {實體名稱}

**說明**：{代表什麼}

**欄位**：
- `{欄位}` ({型別})：{說明}

**關聯**：
- {關聯說明}

**驗證規則**：
- {規則}

**狀態轉換**（若適用）：
- {狀態A} → {狀態B}：{觸發條件}
```

**b. 介面合約** — 僅在專案對外暴露介面時建立。

依專案類型決定格式：
- Web 服務 → REST/GraphQL 端點文件放在 `contracts/`
- 函式庫 → 公開 API 簽名放在 `contracts/api.md`
- CLI 工具 → 指令 schema 放在 `contracts/cli.md`
- 純內部工具 → 跳過

**c. Agent 環境更新** — 偵測當前 AI agent 並更新其 context 檔案：

```bash
ls CLAUDE.md 2>/dev/null                               # → Claude Code
ls .cursor/rules/ 2>/dev/null                          # → Cursor
ls .github/copilot-instructions.md 2>/dev/null         # → GitHub Copilot
ls .windsurfrules 2>/dev/null                          # → Windsurf
ls .roo/rules/ 2>/dev/null                             # → Roo Code
ls AGENTS.md 2>/dev/null                               # → 通用 fallback
```

只新增當前計畫的新技術，保留現有內容。

### 步驟 7：更新 plan.md

用解析後的值填寫所有佔位符。更新憲法檢核為實際通過/失敗狀態。

### 步驟 8：回報結果

- 分支：`{BRANCH}`
- 計畫：`{IMPL_PLAN}`
- 已產生：`research.md` ✅、`data-model.md` ✅（或 N/A）、`contracts/` ✅（或 N/A）
- 下一步：使用 speckit-tasks skill
