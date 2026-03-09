---
name: speckit-taskstoissues
description: 將 tasks.md 中的任務轉換為遠端儲存庫上的 GitHub Issues。不需安裝任何 CLI。需要 GitHub MCP server。
---
> **重要**：所有檔案讀寫操作均相對於使用者的 **project root（當前工作目錄）**，不是 skill 檔案所在路徑。如有疑慮，先執行 `pwd` 確認再操作。


## 使用者輸入

請考慮使用者在對話中提供的額外說明（如 Issue 標籤、負責人指定等）。

## 流程說明

### 步驟 1：找到當前 feature 與任務清單

```bash
git branch --show-current
```

- 分支符合 `[0-9]+-[a-z0-9-]+` → `FEATURE_DIR` = `specs/{BRANCH}`
- 否則：掃描 `specs/` 或詢問使用者

任務檔案：`{FEATURE_DIR}/tasks.md`（絕對路徑）。若不存在：請使用者先使用 speckit-tasks skill。

### 步驟 2：確認 GitHub 遠端

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> **只有在遠端為 GitHub URL 時才繼續**（URL 包含 `github.com`）。
> 若遠端不是 GitHub，立即停止。

### 步驟 3：建立 GitHub Issues

對 `tasks.md` 中的每個任務，使用 GitHub MCP server 在符合遠端 URL 的儲存庫中建立新 Issue。

> [!CAUTION]
> **絕對不可在不符合遠端 URL 的儲存庫中建立 Issues。**
