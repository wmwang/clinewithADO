# ado-devops — 技術手冊

> **一句話摘要**：透過自然語言直接操作 Azure DevOps，涵蓋工單管理、Repository、PR、Wiki 與全文搜尋，零依賴、跨平台、企業環境就緒。

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
| **技能名稱** | `ado-devops` |
| **觸發關鍵字** | 查工單、看 PR、更新狀態、搜尋 Branch、查看 Commit、修改工作項目、列出 Repository、讀寫 Wiki、ADO 相關操作 |
| **主要功能** | 透過 ADO REST API 查詢並管理 Azure DevOps 的工單、Repository、Wiki 與搜尋，無需安裝任何額外套件。 |
| **前置條件** | Python 3（標準函式庫）、ADO PAT、組織名稱（ADO_ORG）、專案名稱（ADO_PROJECT） |
| **產出物** | JSON 格式的查詢結果（工單詳情、PR 清單、Branch 清單、Commit 歷史、搜尋結果等），以及 Wiki 的 Markdown 內容 |
| **技術依賴** | Python 3 標準函式庫：`urllib`、`ssl`、`json`、`base64`；Azure DevOps REST API v7.1；Search API（`almsearch.dev.azure.com`） |

### 這個 Skill 做什麼

ado-devops 是一個讓 Claude 能夠直接操作 Azure DevOps 的技能，設計目標是讓使用者不需要打開瀏覽器或記住 ADO 指令，直接用中文（或英文）說出需求，Claude 就能完成對應的 ADO 操作。

技術上，這個 Skill 透過純 Python `urllib` 呼叫 ADO REST API，完全不依賴 `az` CLI、ADO SDK 或任何第三方套件，在任何有 Python 3 的環境（包括 Windows、Linux、macOS）都能直接執行。憑證管理透過 `setup.py` 統一處理，設定一次後儲存到 `~/.ado-devops.env`，跨 session 永久生效。

功能面涵蓋工單（Work Items）的完整 CRUD、Repository 瀏覽、Branch 管理、Pull Request 建立與 Review、Wiki 讀寫，以及跨 Repo 的全文搜尋，是一個可以完整替代日常 ADO 瀏覽器操作的技能。

---

## 架構圖

```
ado-devops/
├── SKILL.md              # Claude 載入的執行指引與觸發條件
├── README.md             # 使用者快速上手文件
└── scripts/
    ├── ado_client.py     # 共用 HTTP 客戶端（所有腳本共享）
    │                       ─→ 讀取 ~/.ado-devops.env
    │                       ─→ ADO REST API (dev.azure.com)
    ├── setup.py          # 憑證設定與狀態檢查（初次設定入口）
    │                       ─→ 寫入 ~/.ado-devops.env
    ├── work_items.py     # 工單操作（get / list / create / update / mine / sprint-items / comment / children / link）
    │                       ─→ 使用 ado_client.py
    ├── repos.py          # Repository / PR / Branch 操作（list / ls / prs / pr / create-pr / update-pr / branches / create-branch / commits / threads / comment-pr / reply / resolve-thread）
    │                       ─→ 使用 ado_client.py
    ├── wiki.py           # Wiki 讀寫（list / pages / get / create / update / delete）
    │                       ─→ 使用 ado_client.py
    ├── search.py         # 全文搜尋（code / workitem / wiki）
    │                       ─→ 使用 ado_client.py
    │                       ─→ Search API (almsearch.dev.azure.com)
    └── core.py           # 組織 / 專案 / 團隊（whoami / projects / project / teams / members / sprints）
                            ─→ 使用 ado_client.py

元件關係：
┌─────────────┐  觸發   ┌──────────────────────────────┐
│  SKILL.md   │ ──────→ │  Claude 解析使用者意圖         │
└─────────────┘         └──────────────┬───────────────┘
                                       │ 執行腳本
               ┌───────────────────────┼──────────────────────┐
               ▼               ▼               ▼              ▼
        work_items.py      repos.py         wiki.py       search.py / core.py
               │               │               │              │
               └───────────────┴───────────────┴──────────────┘
                                       │ 全部呼叫
                               ┌───────▼────────┐
                               │  ado_client.py  │
                               │  (共用 HTTP)    │
                               └───────┬────────┘
                         ┌────────────┴──────────────┐
                         ▼                           ▼
              ~/.ado-devops.env          ADO REST API
              (憑證設定檔)                dev.azure.com /
                                         almsearch.dev.azure.com
```

---

## 執行流程

### 主流程（初次使用）

```
使用者說出 ADO 相關需求
        │
        ▼
┌───────────────────────────────────┐
│  Claude 識別到觸發情境             │
│  載入 SKILL.md 指令               │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│  Step 1: 偵測作業系統              │
│  python -c "import platform..."   │
│  → 決定 python / python3 指令      │
│  → 決定路徑分隔符 / 或 \          │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│  Step 2: 執行 setup.py status     │
│  檢查 ~/.ado-devops.env 設定狀態  │
└───────────────┬───────────────────┘
                │
        ┌───────▼────────┐
        │  ready: true?  │
        └───┬────────┬───┘
       是   │        │  否（缺少憑證）
            ▼        ▼
   ┌──────────┐  ┌───────────────────────────────┐
   │ 檢查     │  │  引導設定流程                  │
   │ Proxy    │  │  1. 詢問 ADO_ORG（有預設值）   │
   │ 設定     │  │  2. 詢問 ADO_PROJECT（有預設值）│
   └────┬─────┘  │  3. 詢問 ADO_PAT              │
        │        │  4. 詢問是否需要 Proxy         │
        │        │  執行 setup.py save ...        │
        │        └──────────────┬────────────────┘
        └──────────────┬────────┘
                       │
                       ▼
┌───────────────────────────────────┐
│  Step 3: 執行使用者要求的操作      │
│  e.g. work_items.py list          │
│       repos.py prs my-repo        │
│       wiki.py get MyProject.wiki  │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│  Step 4: 解析 JSON 輸出            │
│  格式化後以自然語言回應使用者       │
└───────────────────────────────────┘
```

### 主流程（已設定後，日常使用）

```
使用者說出需求
        │
        ▼
┌───────────────────────────────────┐
│  setup.py status → ready: true   │
│  直接跳到操作步驟                  │
└───────────────┬───────────────────┘
                │
                ▼
   依需求選擇對應腳本執行
        │
   ┌────┴────────────────────────────────────┐
   │                                         │
   ▼                 ▼              ▼         ▼
work_items.py    repos.py       wiki.py   core.py / search.py
   │                │              │
   └───────────┬────┘              │
               ▼                  ▼
         ado_client.py ─→ ADO REST API
```

### 錯誤處理流程

```
腳本執行
        │
        ▼
┌───────────────┐
│  HTTP 回應    │
└───┬───────┬───┘
    │ 成功  │ 失敗
    │ 2xx   │ 4xx / 5xx
    ▼       ▼
格式化  ┌──────────────────────────────┐
輸出    │  輸出含 "error" 欄位的 JSON  │
        │  401 → PAT 失效             │
        │  403 → 權限不足             │
        │  404 → ID/repo 不存在       │
        │  400 → 欄位值不合法         │
        │  連線逾時 → Proxy 未設定     │
        └──────────────────────────────┘
```

---

## 元件說明

### 檔案清單

| 檔案 | 類型 | 功能說明 |
|------|------|---------|
| `SKILL.md` | 指令文件 | Claude 的執行指引、觸發條件、完整操作說明與 CLI 範例 |
| `README.md` | 使用者文件 | 快速上手指南、FAQ、支援操作總覽 |
| `scripts/ado_client.py` | 核心函式庫 | 共用 HTTP 客戶端，處理 PAT 認證、SSL bypass、Proxy 設定、設定檔載入 |
| `scripts/setup.py` | 設定工具 | 憑證的初始化、狀態查詢與持久化儲存 |
| `scripts/work_items.py` | 執行腳本 | 工單的完整 CRUD 與子母單操作 |
| `scripts/repos.py` | 執行腳本 | Repository、Branch、Commit、PR 與 Review 操作 |
| `scripts/wiki.py` | 執行腳本 | Wiki 頁面的讀寫與管理 |
| `scripts/search.py` | 執行腳本 | 程式碼、工單、Wiki 的全文搜尋 |
| `scripts/core.py` | 執行腳本 | 組織、專案、團隊、Sprint 查詢 |
| `evals/evals.json` | 評估資料 | Skill 的自動化評估測試案例 |

---

### 核心腳本說明

#### `scripts/ado_client.py`

**功能**：所有腳本共用的 HTTP 客戶端基礎層，封裝認證、SSL 設定與 Proxy 路由。

**主要函式**：

| 函式 | 說明 |
|------|------|
| `get_client()` | 從環境變數或設定檔建立 ADOClient，缺少憑證時輸出 JSON 錯誤並退出 |
| `ADOClient.__init__()` | 初始化 PAT 認證、Base URL、SSL context（verify=False）、Proxy handler |
| `ADOClient.request()` | 執行 HTTP 請求，回傳 parsed JSON |

**輸入/輸出**：
- 輸入：`ADO_PAT`、`ADO_ORG`、`ADO_PROJECT`（環境變數或 `~/.ado-devops.env`）、`HTTP_PROXY`/`HTTPS_PROXY`（選填）
- 輸出：ADOClient 物件，供各腳本呼叫 REST API

---

#### `scripts/setup.py`

**功能**：憑證設定的入口腳本，提供狀態查詢、儲存與清除功能。

**主要指令**：

| 指令 | 說明 | 範例 |
|------|------|------|
| `status` | 顯示目前設定狀態（來源：env / file / missing）及 `ready` 布林值 | `python3 setup.py status` |
| `save` | 將憑證寫入 `~/.ado-devops.env`（Unix 自動設 600 權限） | `python3 setup.py save --org myorg --project MyProj --pat TOKEN --proxy http://proxy:8080` |
| `clear` | 刪除設定檔 | `python3 setup.py clear` |

**輸入/輸出**：
- 輸入：`--org`、`--project`、`--pat`、`--proxy`（均選填，可單獨更新）
- 輸出：`status` 回傳 JSON，包含 `platform`、`python`、`ready`、各憑證來源、proxy 狀態

---

#### `scripts/work_items.py`

**功能**：工單的完整 CRUD 操作，支援子母單階層管理與 Sprint 查詢。

**主要指令**：

| 指令 | 說明 | 範例 |
|------|------|------|
| `get <id>` | 取得工單詳情（含 parent_id、child_ids） | `python3 work_items.py get 123` |
| `list` | 查詢工單清單（支援多重篩選） | `python3 work_items.py list --state "Active" --type "Bug"` |
| `create` | 建立工單 | `python3 work_items.py create --type "Task" --title "實作 API" --parent 100` |
| `mine` | 查詢指派給自己的工單 | `python3 work_items.py mine --include-closed` |
| `sprint-items` | 查詢目前 Sprint 的工單 | `python3 work_items.py sprint-items --team "Backend Team"` |
| `update <id>` | 更新工單欄位 | `python3 work_items.py update 123 --state "In Progress" --priority 2` |
| `comment <id> <text>` | 新增 Discussion 留言 | `python3 work_items.py comment 123 "已確認原因"` |
| `comments <id>` | 查看所有留言 | `python3 work_items.py comments 123` |
| `children <id>` | 列出母單的所有子單 | `python3 work_items.py children 100` |
| `link <id> --parent <pid>` | 把現有工單掛到母單 | `python3 work_items.py link 456 --parent 100` |

**輸入/輸出**：
- 輸入：工單 ID、各種篩選參數（`--state`、`--type`、`--assignee`、`--sprint`、`--title`、`--top`）
- 輸出：JSON（工單物件或工單陣列），包含 `id`、`title`、`state`、`type`、`assignee`、`parent_id`、`child_ids` 等欄位

---

#### `scripts/repos.py`

**功能**：Repository 的完整操作，涵蓋目錄瀏覽、Branch 管理、Commit 查詢、PR 建立與 Code Review。

**主要指令**：

| 指令 | 說明 | 範例 |
|------|------|------|
| `list` | 列出所有 Repository | `python3 repos.py list` |
| `ls <repo>` | 瀏覽目錄結構 | `python3 repos.py ls my-repo --path "/src" --recursive` |
| `branches <repo>` | 列出 Branch | `python3 repos.py branches my-repo --filter "feature/"` |
| `create-branch <repo>` | 建立 Branch（兩步驟：先查 commit ID 再建立） | `python3 repos.py create-branch my-repo --name "feature/login" --from main` |
| `commits <repo>` | 查看 Commit 歷史 | `python3 repos.py commits my-repo --branch main --top 50` |
| `prs <repo>` | 查詢 PR 清單 | `python3 repos.py prs my-repo --status all --top 30` |
| `pr <repo> <id>` | 取得 PR 詳情 | `python3 repos.py pr my-repo 45` |
| `create-pr <repo>` | 建立 PR | `python3 repos.py create-pr my-repo --source "feature/login" --target main --title "feat: 登入"` |
| `update-pr <repo> <id>` | 更新 PR（標題、草稿狀態、關閉） | `python3 repos.py update-pr my-repo 45 --undraft` |
| `threads <repo> <pr_id>` | 列出 PR 的所有 comment threads | `python3 repos.py threads my-repo 45` |
| `comment-pr <repo> <pr_id>` | 新增 PR 留言（支援 inline） | `python3 repos.py comment-pr my-repo 45 "LGTM" --file "/src/api.py" --line 42` |
| `reply <repo> <pr_id> <thread_id>` | 回覆 thread | `python3 repos.py reply my-repo 45 3 "已修正"` |
| `resolve-thread <repo> <pr_id> <thread_id>` | 標記 thread 已解決 | `python3 repos.py resolve-thread my-repo 45 3` |

**輸入/輸出**：
- 輸入：repo 名稱、PR ID、Branch 名稱、各種選項
- 輸出：JSON（repo/PR/branch/commit 物件或陣列）

---

#### `scripts/wiki.py`

**功能**：Wiki 頁面的完整讀寫操作，支援從字串或檔案提供內容。

**主要指令**：

| 指令 | 說明 | 範例 |
|------|------|------|
| `list` | 列出所有 Wiki | `python3 wiki.py list` |
| `pages <wiki>` | 瀏覽頁面目錄 | `python3 wiki.py pages MyProject.wiki --recursive` |
| `get <wiki> <path>` | 讀取頁面內容（Markdown） | `python3 wiki.py get MyProject.wiki "/Architecture/Overview"` |
| `create <wiki> <path>` | 建立頁面 | `python3 wiki.py create MyProject.wiki "/New/Page" --content "# 標題"` |
| `update <wiki> <path>` | 更新頁面（完整覆寫，無需 ETag） | `python3 wiki.py update MyProject.wiki "/Existing/Page" --content-file ./new.md` |
| `delete <wiki> <path>` | 刪除頁面（不可還原） | `python3 wiki.py delete MyProject.wiki "/Old/Page"` |

---

#### `scripts/search.py`

**功能**：透過 ADO Search API（`almsearch.dev.azure.com`）進行跨 Repo 全文搜尋，支援程式碼、工單、Wiki 三種搜尋類型。

**主要指令**：

| 指令 | 說明 | 範例 |
|------|------|------|
| `code <keyword>` | 搜尋程式碼內容 | `python3 search.py code "ConnectionString" --repo my-repo --branch main` |
| `workitem <keyword>` | 搜尋工單（標題、描述、留言） | `python3 search.py workitem "payment" --type "Bug" --state "Active"` |
| `wiki <keyword>` | 搜尋 Wiki 頁面 | `python3 search.py wiki "部署流程" --wiki "my-project.wiki"` |

**注意**：Search API 使用不同 hostname（`almsearch.dev.azure.com`），需確認企業防火牆/Proxy 白名單已開放此域名。Search body 需使用 `$top`/`$skip`，非標準的 `top`/`skip`。

---

#### `scripts/core.py`

**功能**：組織、專案、團隊與 Sprint 的查詢操作，可用於驗證連線設定。

**主要指令**：

| 指令 | 說明 | 範例 |
|------|------|------|
| `whoami` | 確認 PAT 對應的使用者身份與連線狀態 | `python3 core.py whoami` |
| `projects` | 列出組織內所有 Projects | `python3 core.py projects` |
| `project [name]` | 查看專案詳情（Process、版控類型） | `python3 core.py project "MyOtherProject"` |
| `teams` | 列出 Project 內所有 Teams | `python3 core.py teams` |
| `members <team>` | 查看 Team 成員 | `python3 core.py members "Backend Team"` |
| `sprints` | 列出所有 Sprints（含時間區間） | `python3 core.py sprints --team "Backend Team" --current` |

---

## 使用指南

### 快速開始

**場景 1：查詢指派給自己的工單**

```
使用者說：「幫我列出指派給我的 Active 工單」

Claude 會執行：
1. python3 setup.py status  ← 確認設定
2. python3 work_items.py mine  ← 查詢我的工單
3. 格式化 JSON 結果，以表格或清單回應使用者
```

**場景 2：查看目前 Sprint 進度**

```
使用者說：「這個 sprint 有哪些任務還沒做完」

Claude 會執行：
1. python3 setup.py status  ← 確認設定
2. python3 work_items.py sprint-items  ← 取得目前 Sprint 工單
3. 篩選 state 不是 Closed/Done 的工單後回應
```

**場景 3：初次設定並查詢**

```
使用者說：「查一下 PR #45 的內容」

Claude 會執行：
1. python3 setup.py status → ready: false（ADO_PAT 未設定）
2. 詢問 ADO_ORG（預設 tsmcit）
3. 詢問 ADO_PROJECT（預設 AI Operation Center）
4. 詢問使用者的 PAT
5. 詢問是否需要 Proxy
6. python3 setup.py save --org ... --project ... --pat ... --proxy ...
7. python3 repos.py pr <repo> 45
8. 回傳 PR 的標題、描述、狀態、Reviewer 清單
```

**場景 4：搜尋程式碼**

```
使用者說：「在 ADO 上搜尋有沒有用到 ConnectionString」

Claude 會執行：
1. python3 setup.py status
2. python3 search.py code "ConnectionString"
3. 顯示匹配的檔案路徑、行號、程式碼片段
```

---

### 指令參考

```bash
# ── 工單 ──
python3 scripts/work_items.py get 123
python3 scripts/work_items.py list --state "Active" --type "Bug" --sprint current
python3 scripts/work_items.py create --type "Task" --title "標題" --parent 100
python3 scripts/work_items.py update 123 --state "In Progress" --priority 2
python3 scripts/work_items.py mine
python3 scripts/work_items.py sprint-items --team "Backend Team"
python3 scripts/work_items.py comment 123 "留言內容"
python3 scripts/work_items.py children 100
python3 scripts/work_items.py link 456 --parent 100

# ── Repository ──
python3 scripts/repos.py list
python3 scripts/repos.py ls my-repo --path "/src" --recursive
python3 scripts/repos.py branches my-repo --filter "feature/"
python3 scripts/repos.py commits my-repo --branch main --top 50
python3 scripts/repos.py prs my-repo --status all
python3 scripts/repos.py create-pr my-repo --source "feature/x" --target main --title "feat: X"
python3 scripts/repos.py threads my-repo 45
python3 scripts/repos.py comment-pr my-repo 45 "LGTM"

# ── Wiki ──
python3 scripts/wiki.py list
python3 scripts/wiki.py pages MyProject.wiki --recursive
python3 scripts/wiki.py get MyProject.wiki "/Architecture/Overview"
python3 scripts/wiki.py create MyProject.wiki "/New/Page" --content "# 標題"
python3 scripts/wiki.py update MyProject.wiki "/Existing/Page" --content-file ./file.md
python3 scripts/wiki.py delete MyProject.wiki "/Old/Page"

# ── 搜尋 ──
python3 scripts/search.py code "keyword" --repo my-repo
python3 scripts/search.py workitem "payment" --type "Bug"
python3 scripts/search.py wiki "部署文件"

# ── 組織 / 團隊 ──
python3 scripts/core.py whoami
python3 scripts/core.py projects
python3 scripts/core.py teams
python3 scripts/core.py sprints --current
python3 scripts/core.py members "Backend Team"

# ── 設定 ──
python3 scripts/setup.py status
python3 scripts/setup.py save --org myorg --project "My Project" --pat TOKEN
python3 scripts/setup.py save --proxy http://proxy.corp:8080
python3 scripts/setup.py clear
```

---

### 使用技巧

- **設定一次即可**：第一次使用時 Claude 會引導設定，之後不需要再輸入憑證。設定儲存在 `~/.ado-devops.env`，比環境變數更可靠，不受 shell 重啟影響。
- **多條件篩選工單**：`list` 指令支援多個篩選參數同時使用，例如 `--sprint current --state "To Do" --type "Bug"` 可快速鎖定本 Sprint 未開始的 Bug。
- **全文搜尋 vs WIQL 搜尋的差異**：`search.py workitem` 是全欄位全文搜尋，`work_items.py list --title` 只搜尋標題，兩者用途不同。
- **子母單查詢**：`get` 指令輸出的 `child_ids` 只包含直接子單 ID，若需要子單詳細資訊請接著用 `children` 指令。
- **Wiki 頁面識別符**：執行 Wiki 操作前先用 `wiki.py list` 取得正確的 wiki 名稱（如 `MyProject.wiki`），頁面路徑需以 `/` 開頭。
- **Windows 使用者**：Claude 會自動偵測 OS 並選擇正確的 `python` 指令與路徑分隔符，無需手動調整。

---

## 開發者指南

### 如何擴充這個 Skill

#### 新增工單操作（以「批次更新」為例）

```
想要新增「批次更新多個工單狀態」時，需要修改：
1. scripts/work_items.py → 新增 cmd_batch_update() 函式，在 main() 中加入 subparser
2. SKILL.md → 在「工單操作」章節補充新指令說明與範例
```

#### 新增 API 模組（以「Pipeline」為例）

```
想要新增 ADO Pipeline 操作時：
1. scripts/ 下新增 pipelines.py，import ado_client 並用 get_client() 取得 HTTP 客戶端
2. 參考 work_items.py 或 repos.py 的結構（subparser + cmd_xxx 函式模式）
3. SKILL.md → 新增「Pipeline 操作」章節
```

#### 修改觸發條件

SKILL.md 的 `description` 欄位控制 Claude 何時使用這個 skill：

```yaml
description: |
  通用 Azure DevOps 操作技能。當使用者提到查工單、看 PR、更新狀態...
  新增觸發情境：查看 Pipeline 執行狀態、觸發建置
```

---

### 設計決策記錄

| 決策 | 選擇 | 原因 |
|------|------|------|
| HTTP 客戶端 | `urllib`（標準函式庫） | 零依賴，任何有 Python 3 的環境都能直接執行，不需 pip install |
| SSL 驗證 | 強制 bypass（`verify=False`） | 企業環境常見自簽憑證，避免連線失敗 |
| 憑證管理 | `~/.ado-devops.env` 設定檔 + 環境變數 | 設定一次永久生效，不受 shell session 影響；環境變數可覆蓋用於 CI/CD |
| 跨平台支援 | SKILL.md 明確說明 OS 偵測步驟 | Windows 的 `python` vs `python3`、路徑分隔符差異需要 Claude 自動處理 |
| Search API | 獨立腳本（`search.py`），不併入其他腳本 | Search API 使用不同 hostname，邏輯獨立較易維護與測試 |
| Wiki 更新 | 使用 `If-Match: *` 強制覆寫 | 避免需要先 GET 取得 ETag 才能 PUT 的兩步驟流程 |
| 子母單 | `get` 輸出含 `parent_id`/`child_ids`，`children` 提供詳細欄位 | 分離「ID 關係」（快速）與「詳細資訊」（較慢）的查詢需求 |

---

### 測試方式

```bash
# 1. 確認設定正確
python3 scripts/setup.py status

# 2. 驗證 ADO 連線
python3 scripts/core.py whoami

# 3. 基本工單查詢（確認 ADO_PROJECT 正確）
python3 scripts/work_items.py list --top 5

# 4. 確認 Search API 可達（需確認防火牆白名單）
python3 scripts/search.py code "test" --top 1

# 5. Wiki 操作（需確認 wiki 名稱存在）
python3 scripts/wiki.py list
```

評估案例在 `evals/evals.json`，包含常見使用情境的輸入/輸出對，可用於驗證 Skill 的觸發行為是否符合預期。

---

## 注意事項與常見問題

### 已知限制

- Search API（`search.py`）使用不同 hostname `almsearch.dev.azure.com`，企業防火牆/Proxy 白名單需額外開放此域名。
- `wiki.py update` 為完整覆寫，不支援 partial update（patch）；若需追加內容，需先 `get` 取得現有內容再合併後 `update`。
- `work_items.py sprint-items` 的 `@CurrentIteration` 查詢在多 team 專案下須加 `--team` 才能精確對應正確的 Sprint。
- `core.py whoami` 在部分 ADO 組織不開放 `connectionData` API，此時改用 `projects` 驗證連線。
- SSL bypass（`verify=False`）為固定行為，無法針對特定域名選擇性啟用驗證。

### 常見錯誤

| 錯誤訊息 | 原因 | 解決方法 |
|---------|------|---------|
| `Missing credentials: ADO_PAT` | PAT 未設定 | 執行 `python3 setup.py save --pat TOKEN` |
| `HTTP 401` | PAT 失效或過期 | 在 ADO 重新產生 PAT，再執行 `setup.py save --pat NEW_TOKEN` |
| `HTTP 403` | PAT 缺少必要權限 | 確認 PAT 包含 Work Items (Read/Write)、Code (Read)、Wiki (Read/Write) |
| `HTTP 404` | 工單 ID、repo 名稱或 wiki 路徑不存在 | 確認 ID 正確，以及 `ADO_PROJECT` 是否匹配 |
| `HTTP 400` on update | 欄位值不合法（常見：state 拼字不符 Process 設定） | 先 `get <id>` 確認目前 state 值，再依 Process 模板調整 |
| `HTTP 409` on wiki create | 頁面已存在 | 改用 `wiki.py update` |
| `ProxyError` / 連線逾時 | 企業 Proxy 未設定或設定錯誤 | 執行 `setup.py save --proxy http://proxy.corp:8080` |
| `python3: command not found` | Windows 無 `python3` 指令 | 改用 `python` 或 `py -3` |
| `whoami` 回傳 HTTP 404 | 部分 ADO 組織不開放此 API | 改用 `core.py projects` 驗證連線 |

### 安全注意事項

- **PAT 保護**：`setup.py save` 在 Unix 系統上會將 `~/.ado-devops.env` 設為 `600` 權限（僅擁有者可讀）；Windows 沿用系統 ACL。請勿將 `.ado-devops.env` 或含 PAT 的環境變數提交到版本控制。
- **PAT 最小權限原則**：建議 PAT 只開放必要的 scope（Work Items Read/Write、Code Read、Wiki Read/Write），不要使用 Full Access Token。
- **SSL bypass**：腳本固定停用 SSL 驗證（`verify=False`）以支援企業自簽憑證，使用前請確認連線到的 ADO 端點確實是受信任的內部服務。
- **Wiki 刪除確認**：`wiki.py delete` 操作不可還原，Claude 在執行前應向使用者確認後再執行。
