# ado-devops Skill

透過自然語言操作 Azure DevOps 的 Claude Code Skill。工單查詢、PR 管理、Branch 搜尋、全文搜尋，直接用說的就好。

---

## 特色

- **零依賴**：純 Python 標準函式庫（`urllib`），無需安裝任何套件
- **跨平台**：Windows / Linux / macOS 均適用
- **企業環境就緒**：自動 bypass SSL 驗證，支援 HTTP Proxy
- **設定一次即可**：憑證儲存在 `~/.ado-devops.env`，之後不需重複輸入
- **子母單支援**：建立、查詢、連結工單階層關係

---

## 快速開始

### 1. 安裝 Skill

將此資料夾放入 Cline 的 skills 目錄：

```
# 專案層級（僅此專案可用）
<project>/.cline/skills/ado-devops/

# 全域（所有專案皆可用）
~/.cline/skills/ado-devops/
```

### 2. 第一次使用

直接對 Claude 說出需求，Skill 會自動偵測設定狀態並引導你完成設定：

```
你：幫我查 ADO 上指派給我的工單
Claude：偵測到 ADO_PAT 尚未設定，請提供你的 Personal Access Token...
（引導完成後，之後就不需要再輸入）
```

### 3. 取得 Personal Access Token（PAT）

1. 登入 Azure DevOps → 右上角頭像 → **Personal access tokens**
2. 點擊 **New Token**，設定以下權限：
   - **Work Items**：Read & Write
   - **Code**：Read
3. 複製產生的 Token，貼給 Claude 即可

---

## 支援的操作

### 工單（Work Items）

| 操作 | 說明 |
|------|------|
| 查看工單詳情 | 含母子單關係、狀態、指派對象 |
| 查詢工單清單 | 依狀態、類型、指派對象、Sprint、標題關鍵字篩選 |
| 建立工單 | 支援直接指定母單 |
| 更新工單 | 狀態、標題、指派、優先級、自訂欄位 |
| 查我的工單 | 列出指派給自己的所有工單 |
| 查 Sprint 工單 | 支援 @CurrentIteration |
| 新增 / 查看留言 | Discussion 留言 |
| 子母單操作 | 建立子單、列出子單、把現有工單掛到母單 |

### Repository

| 操作 | 說明 |
|------|------|
| 列出所有 Repo | |
| 瀏覽目錄結構 | 支援遞迴列出 |
| Branch 管理 | 列出、篩選、建立 Branch |
| Commit 歷史 | 依 Branch 查詢 |
| Pull Request | 建立、更新、查詢（active / completed / abandoned） |
| PR Review | 列出 threads、新增留言、inline comment、回覆、標記已解決 |

### 全文搜尋

| 操作 | 說明 |
|------|------|
| 搜尋程式碼 | 跨所有 Repo 搜尋檔案內容 |
| 搜尋工單 | 標題、描述、留言全文搜尋 |
| 搜尋 Wiki | Wiki 頁面內容搜尋 |

### 組織 / 專案 / 團隊

| 操作 | 說明 |
|------|------|
| whoami | 確認 PAT 連線與使用者身份 |
| 列出 Projects | 組織內所有專案 |
| 列出 Teams | 專案內所有團隊與成員 |
| 列出 Sprints | 含目前 Sprint 篩選 |

---

## 憑證設定

憑證優先順序：**環境變數 > `~/.ado-devops.env` 設定檔**

| 變數 | 必填 | 預設值 | 說明 |
|------|------|--------|------|
| `ADO_PAT` | 是 | — | Personal Access Token |
| `ADO_ORG` | 是 | `tsmcit` | ADO 組織名稱 |
| `ADO_PROJECT` | 是 | `AI Operation Center` | 專案名稱（允許空格） |
| `HTTP_PROXY` | 否 | — | 企業 Proxy，e.g. `http://proxy:8080` |
| `HTTPS_PROXY` | 否 | — | 同上，HTTPS 版本 |

設定檔位於 `~/.ado-devops.env`，檔案權限自動設為 `600`（僅擁有者可讀）。

若要重新設定，對 Claude 說「重新設定 ADO 憑證」或手動刪除 `~/.ado-devops.env`。

---

## 檔案結構

```
ado-devops/
├── SKILL.md              # Skill 主定義（Claude 讀取此檔）
├── README.md             # 本文件
└── scripts/
    ├── ado_client.py     # 共用 HTTP 客戶端（所有腳本共享）
    ├── setup.py          # 憑證設定與狀態檢查
    ├── work_items.py     # 工單操作
    ├── repos.py          # Repository / PR / Branch 操作
    ├── search.py         # 全文搜尋（代碼、工單、Wiki）
    └── core.py           # 組織 / 專案 / 團隊操作
```

---

## 常見問題

**Q：第一次使用要設定什麼？**
只需要提供 PAT，組織與專案有預設值，確認或修改後即完成。

**Q：PAT 過期怎麼辦？**
對 Claude 說「更新我的 ADO PAT」，重新輸入新的 Token 即可。

**Q：公司有 Proxy / 自簽憑證，可以用嗎？**
可以。設定 `HTTP_PROXY` 或 `HTTPS_PROXY` 環境變數，SSL 驗證已自動 bypass。

**Q：工單狀態更新失敗（HTTP 400）？**
狀態值需符合該 Project 的 Process 設定。先查詢工單取得目前狀態值，再確認可用的轉換值。

**Q：`whoami` 回傳 404？**
部分 ADO 組織不開放 `connectionData` API。改用 `python core.py projects` 驗證連線是否正常。
