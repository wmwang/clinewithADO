---
name: speckit-implement
description: 依序執行 tasks.md 中定義的所有任務，完成 feature 實作。不需安裝任何 CLI。
---
> **重要**：所有檔案讀寫操作均相對於使用者的 **project root（當前工作目錄）**，不是 skill 檔案所在路徑。如有疑慮，先執行 `pwd` 確認再操作。


## 使用者輸入

請考慮使用者在對話中提供的額外指示（如只實作特定階段、跳過某些任務等）。

## 執行前：Extension Hooks

檢查 `.specify/extensions.yml` 中的 `hooks.before_implement`。對每個已啟用且無 `condition` 的 hook：
- `optional: true` → 顯示並詢問是否執行
- `optional: false` → 顯示 `EXECUTE_COMMAND: {command}` 並等待結果後再繼續

若檔案不存在或無法解析則靜默跳過。

## 流程說明

### 步驟 1：找到當前 feature

```bash
git branch --show-current
```

- 分支符合 `[0-9]+-[a-z0-9-]+` → `FEATURE_DIR` = `specs/{BRANCH}`
- 否則：掃描 `specs/` 或詢問使用者

列出可用文件：
```bash
ls specs/{BRANCH}/
```

確認 `{FEATURE_DIR}/tasks.md` 存在。若不存在：請使用者先使用 speckit-tasks skill。

### 步驟 2：Checklist 關卡

若 `{FEATURE_DIR}/checklists/` 存在，掃描其中每個 `.md` 檔案：

```
| Checklist    | 總計 | 已完成 | 未完成 | 狀態     |
|--------------|------|--------|--------|----------|
| ux.md        | 12   | 12     | 0      | ✓ 通過   |
| security.md  | 8    | 5      | 3      | ✗ 未通過 |
```

- 全部通過 → 自動繼續
- 有未完成 → **停止**並詢問：*「部分 checklist 未完成，仍要繼續實作嗎？（是/否）」*
  - `否` / `等等` / `停止` → 停止執行
  - `是` / `繼續` → 繼續

### 步驟 3：載入實作背景

- **必要**：`tasks.md` — 完整任務清單與執行計畫
- **必要**：`plan.md` — 技術堆疊、架構、檔案結構
- **若存在**：`data-model.md`、`contracts/`、`research.md`、`quickstart.md`

### 步驟 4：確認專案設定

依 `plan.md` 中偵測到的技術堆疊，檢查並建立 ignore 檔案：

```bash
git rev-parse --git-dir 2>/dev/null   # → 需要 .gitignore？
ls Dockerfile* 2>/dev/null             # → 需要 .dockerignore？
ls .eslintrc* eslint.config.* 2>/dev/null  # → 需要 .eslintignore？
ls .prettierrc* 2>/dev/null            # → 需要 .prettierignore？
ls package.json 2>/dev/null            # → 需要 .npmignore？
```

各語言常用模式：
- **Node.js/TS**：`node_modules/`、`dist/`、`build/`、`*.log`、`.env*`
- **Python**：`__pycache__/`、`*.pyc`、`.venv/`、`venv/`、`dist/`、`*.egg-info/`
- **Java**：`target/`、`*.class`、`*.jar`、`.gradle/`、`build/`
- **C#/.NET**：`bin/`、`obj/`、`*.user`、`packages/`
- **Go**：`*.exe`、`*.test`、`vendor/`、`*.out`
- **Rust**：`target/`、`debug/`、`release/`、`*.rs.bk`
- **Swift**：`.build/`、`DerivedData/`、`*.swiftpm/`
- **通用**：`.DS_Store`、`Thumbs.db`、`*.tmp`、`*.swp`

若檔案已存在：僅補充缺少的關鍵模式。若不存在：建立完整內容。

### 步驟 5：依階段執行任務

從 `tasks.md`：
1. 解析所有階段、任務、依賴關係、`[P]` 標記
2. **逐階段執行**：每個階段完成後才進入下一個
3. **循序任務**：依序執行；失敗則停止
4. **平行任務 `[P]`**：可並行執行（不同檔案，無共享依賴）
5. 每個任務完成後：在 `tasks.md` 中標記 `[x]`
6. 每個任務完成後回報進度

每個階段內的執行順序：
1. 設定 / 專案結構
2. 測試（若有 TDD 需求）
3. 模型 / 資料層
4. 服務 / 商業邏輯
5. 端點 / CLI / UI
6. 整合 / 中介層

### 步驟 6：完成驗證

- 所有必要任務已標記 `[x]`
- 實作符合 spec.md 需求
- 測試通過（若適用）
- 回報最終狀態與已完成工作摘要

## 執行後：Extension Hooks

檢查 `.specify/extensions.yml` 中的 `hooks.after_implement`，處理方式同執行前。
