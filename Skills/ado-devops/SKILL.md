---
name: ado-devops
description: |
  通用 Azure DevOps 操作技能。當使用者提到查工單、看 PR、更新狀態、搜尋 Branch、查看 Commit、修改工作項目、列出 Repository 等 ADO 相關操作時，立即使用此技能。
  觸發情境包含（但不限於）：
  - 「幫我查工單 #123」、「看一下這個 task」、「有哪些 To Do 的 bug」
  - 「更新工單狀態到 Active」、「把這個 assign 給 xxx」
  - 「列出 feature branch」、「看 main branch 的 commit」
  - 「有哪些 active PR」、「查一下 PR #45」
  - 「ADO 上有什麼工單」、「這個 sprint 有哪些任務」
  - 「我們有哪些 project」、「這個 team 有哪些人」、「現在的 sprint 是什麼時候」
  - 「誰的 PAT 是這個」、「確認一下 ADO 連線」
  - 「搜尋 ADO 裡有沒有用到 xxx」、「在 repo 裡找 ConnectionString」、「wiki 上有沒有部署文件」
  即使使用者沒有明說 Azure DevOps，只要情境涉及工單管理、程式碼儲存庫或專案/團隊查詢，也應觸發此技能。
---

# Azure DevOps 通用操作技能

透過 ADO REST API（Python `urllib`，無需 az CLI 或 SDK）查詢並管理 Azure DevOps 的工單與 Repository。

## 初次設定（首次使用必讀）

### 0. 偵測作業系統與 Python 指令

**在執行任何指令前，先偵測使用者的作業系統**，以決定後續指令的語法：

```bash
python -c "import platform, sys; print(platform.system(), sys.version)"
# 或
python3 -c "import platform, sys; print(platform.system(), sys.version)"
```

根據輸出決定後續使用的 Python 指令與路徑分隔符：

| 作業系統輸出 | Python 指令 | 路徑分隔符 | 路徑引號 |
|---|---|---|---|
| `Windows` | `python` | `\` | `"..."` (CMD) 或 `"..."` (PowerShell) |
| `Linux` / `Darwin` | `python3` | `/` | `"..."` |

> **Windows 注意**：若 `python` 無法執行，嘗試 `py -3`。腳本路徑中的 `/` 請改為 `\`。

以下文件範例均使用 Unix 語法（`python3` + `/`）。Windows 執行時請自行替換。

---

**每次執行任何指令前，先呼叫 `setup.py status` 確認設定狀態：**

```bash
python3 "$SCRIPT_DIR/setup.py" status
```

根據回傳的 `ready` 欄位決定下一步：

### 情況一：`"ready": true`

設定完整，檢查 `proxy` 欄位：

- 若 `proxy.effective` 為 `null` 且使用者所在環境需要 Proxy，詢問：
  > 「您目前沒有設定 HTTP Proxy。若公司環境需要透過 Proxy 連線，請提供 Proxy 網址（例如 `http://proxy.corp:8080`），否則直接略過。」
- 若使用者提供 Proxy，執行：
  ```bash
  python3 "$SCRIPT_DIR/setup.py" save --proxy "http://proxy.corp:8080"
  ```
- 確認完 Proxy 後，直接執行使用者要求的操作，無需其他提示。

### 情況二：`"ready": false`（有缺少的憑證）

依序引導使用者完成設定，**對每個缺少的值詢問一次**：

#### ADO_ORG（組織名稱）
若未設定，詢問使用者：
> 「ADO 組織名稱（ADO_ORG）未設定。預設值為 **tsmcit**，請問要使用預設值，還是輸入其他名稱？」

#### ADO_PROJECT（專案名稱）
若未設定，詢問使用者：
> 「ADO 專案名稱（ADO_PROJECT）未設定。預設值為 **AI Operation Center**，請問要使用預設值，還是輸入其他名稱？」

#### ADO_PAT（Personal Access Token）
若未設定，詢問使用者：
> 「請提供您的 Azure DevOps Personal Access Token（PAT）。PAT 需要 **Work Items (Read & Write)** 與 **Code (Read)** 權限。」

#### HTTP Proxy（企業網路必填）
詢問使用者：
> 「您的環境是否需要透過 HTTP Proxy 連線？若有請提供網址（例如 `http://proxy.corp:8080`），否則直接略過。」

取得所有值後，執行儲存（無 Proxy 則省略 `--proxy` 參數）：

```bash
python3 "$SCRIPT_DIR/setup.py" save \
  --org "使用者提供的組織名稱" \
  --project "使用者提供的專案名稱" \
  --pat "使用者提供的 PAT" \
  --proxy "使用者提供的 Proxy URL（若有）"
```

設定會儲存到 `~/.ado-devops.env`（Windows 為 `%USERPROFILE%\.ado-devops.env`），**之後不需重複設定**，所有腳本都會自動載入。

> **Proxy 讀取優先順序**：環境變數（`HTTP_PROXY`、`http_proxy`、`HTTPS_PROXY`、`https_proxy`）> `~/.ado-devops.env`。腳本同時支援大小寫，Linux/macOS 上的 `http_proxy`（小寫）亦可正確讀取。

---

## 腳本路徑

此 skill 的腳本位於 **SKILL.md 同層的 `scripts/` 子目錄**。執行前，先取得 SKILL.md 的絕對路徑，再組出腳本的完整路徑。

### Unix / macOS

```bash
SCRIPT_DIR="<SKILL.md 所在目錄>/scripts"

python3 "$SCRIPT_DIR/work_items.py" get 123
python3 "$SCRIPT_DIR/repos.py" list
python3 "$SCRIPT_DIR/core.py" whoami
python3 "$SCRIPT_DIR/search.py" code "keyword"
```

### Windows（PowerShell）

```powershell
$SCRIPT_DIR = "<SKILL.md 所在目錄>\scripts"

python "$SCRIPT_DIR\work_items.py" get 123
python "$SCRIPT_DIR\repos.py" list
python "$SCRIPT_DIR\core.py" whoami
python "$SCRIPT_DIR\search.py" code "keyword"
```

> Windows CMD 使用 `%SCRIPT_DIR%\work_items.py`，PowerShell 使用 `$SCRIPT_DIR\work_items.py`。

以下文件中的腳本路徑均以 `$SCRIPT_DIR` 代稱。Claude 執行時應自動解析 SKILL.md 的實際位置（無論是專案層級的 `.cline/skills/` 或全域的 `~/.cline/skills/`），並根據作業系統選擇正確語法，不要寫死路徑。

## 前置條件

憑證優先透過 `~/.ado-devops.env` 設定檔管理（由 `setup.py save` 寫入），也可使用環境變數覆蓋。

**環境變數方式（選擇性）：**

```bash
# Unix/macOS
export ADO_PAT="your_personal_access_token"    # 必填
export ADO_ORG="your-organization"             # 必填
export ADO_PROJECT="your-project"              # 必填
export HTTP_PROXY="http://proxy.corp:8080"     # 選填，企業 proxy（大小寫均支援）
```

```powershell
# Windows PowerShell
$env:ADO_PAT = "your_personal_access_token"
$env:ADO_ORG = "your-organization"
$env:ADO_PROJECT = "your-project"
$env:HTTP_PROXY = "http://proxy.corp:8080"
```

> **建議做法**：使用 `setup.py save` 將設定寫入 `~/.ado-devops.env`，跨 session 永久生效，不受 shell 重啟影響。

> 腳本自動 bypass SSL 驗證（`verify=False`），支援自簽憑證與企業 proxy 環境。Proxy 同時讀取 `HTTP_PROXY`、`http_proxy`、`HTTPS_PROXY`、`https_proxy`（大小寫皆支援）。

若憑證未設定，腳本會輸出含 `"error"` 欄位的 JSON 並退出。請引導使用者執行 `setup.py save` 完成設定，而非直接要求設定環境變數。

---

## 工單操作（Work Items）


### 取得工單詳情

```bash
python "$SCRIPT_DIR/work_items.py" get <id>
```

範例：
```bash
python "$SCRIPT_DIR/work_items.py" get 123
```

### 查詢工單清單

```bash
python "$SCRIPT_DIR/work_items.py" list [options]
```

| 參數 | 說明 | 範例 |
|------|------|------|
| `--state STATE` | 篩選狀態 | `--state "Active"` |
| `--type TYPE` | 工單類型 | `--type "Bug"` / `"Task"` / `"User Story"` |
| `--assignee` | 指派對象 | `--assignee me` 或 `--assignee "John"` |
| `--title KEYWORD` | 標題關鍵字 | `--title "login"` |
| `--sprint` | Sprint | `--sprint current` 或 `--sprint "Sprint 5"` |
| `--top N` | 最多幾筆（預設 50） | `--top 20` |

可組合使用：

```bash
# 本 Sprint 所有 To Do 的 Bug
python "$SCRIPT_DIR/work_items.py" list --sprint current --state "To Do" --type "Bug"

# 指派給自己的所有 Active 工單
python "$SCRIPT_DIR/work_items.py" list --assignee me --state "Active"

# 標題包含 "payment" 的工單
python "$SCRIPT_DIR/work_items.py" list --title "payment"
```

### 建立工單

```bash
python "$SCRIPT_DIR/work_items.py" create \
  --type "Bug" --title "登入頁面 500 錯誤" \
  --assign "dev@company.com" --priority 1 \
  --description "重現步驟：..."
```

支援 `--type` 值：`Bug` / `Task` / `User Story` / `Feature` / `Epic`（依 Project Process 而定）。加 `--field` 可設定任意自訂欄位。

### 查看自己的工單

```bash
# 查自己所有未關閉的工單
python "$SCRIPT_DIR/work_items.py" mine

# 含已關閉
python "$SCRIPT_DIR/work_items.py" mine --include-closed
```

### 查看 Sprint 工單

```bash
# 目前進行中的 sprint（@CurrentIteration）
python "$SCRIPT_DIR/work_items.py" sprint-items

# 指定 team（多 team 的 project 才需要）
python "$SCRIPT_DIR/work_items.py" sprint-items --team "Backend Team"

# 指定 sprint 路徑
python "$SCRIPT_DIR/work_items.py" sprint-items --sprint "MyProject\\Sprint 5"
```

### 更新工單

```bash
python "$SCRIPT_DIR/work_items.py" update <id> [options]
```

| 參數 | 說明 |
|------|------|
| `--state STATE` | 更新狀態（需符合該 Project Process 的有效值） |
| `--title TITLE` | 更新標題 |
| `--assign EMAIL` | 指派給其他人（使用 email 或 display name） |
| `--priority 1-4` | 設定優先級（1 = 最高） |
| `--field "Field.Name" "value"` | 更新任意欄位（可重複） |

範例：

```bash
# 更新狀態
python "$SCRIPT_DIR/work_items.py" update 123 --state "In Progress"

# 指派並設定優先級
python "$SCRIPT_DIR/work_items.py" update 123 --assign "dev@company.com" --priority 2

# 更新自訂欄位
python "$SCRIPT_DIR/work_items.py" update 123 --field "System.Tags" "hotfix;urgent"
```

### 新增 / 查看 Discussion 留言

```bash
# 新增留言
python "$SCRIPT_DIR/work_items.py" comment 123 "這個問題已確認，原因是..."

# 查看留言（含 HTML 轉純文字）
python "$SCRIPT_DIR/work_items.py" comments 123
```

### 子母單關聯操作

ADO 工單支援階層關係（Epic → Feature → User Story → Task），以下指令處理子母單的建立與查詢。

#### 建立工單時直接掛到母單

```bash
# 在母單 #100（Feature）底下建立一個子 Task
python "$SCRIPT_DIR/work_items.py" create \
  --type "Task" --title "實作登入 API" \
  --parent 100
```

#### 列出母單的所有子單

```bash
python "$SCRIPT_DIR/work_items.py" children 100
```

回傳子單清單（type、title、state、assignee 等欄位），可用來瞭解某個 Feature / User Story 底下的任務進度。

#### 把現有工單掛到母單

```bash
# 把工單 #456 設為工單 #100 的子單
python "$SCRIPT_DIR/work_items.py" link 456 --parent 100
```

#### 查看工單的母子關係

使用 `get` 取得工單詳情時，輸出中會包含：

```json
{
  "parent_id": 100,
  "child_ids": [201, 202, 203]
}
```

- `parent_id`：該工單的母單 ID（若為頂層則為 `null`）
- `child_ids`：直接子單的 ID 清單（若無子單則為 `[]`）

> **注意**：`child_ids` 只包含直接子單 ID，若需要子單的詳細欄位，請使用 `children <id>` 指令。

---

## Repository 操作


### 列出所有 Repository

```bash
python "$SCRIPT_DIR/repos.py" list
```

### 瀏覽 Repository 目錄

```bash
# 列出根目錄
python "$SCRIPT_DIR/repos.py" ls my-repo

# 指定路徑和 branch
python "$SCRIPT_DIR/repos.py" ls my-repo --path "/src" --branch main

# 遞迴列出所有檔案
python "$SCRIPT_DIR/repos.py" ls my-repo --recursive
```

### 建立 Branch

```bash
python "$SCRIPT_DIR/repos.py" create-branch my-repo \
  --name "feature/new-login" --from main
```

### 建立 Pull Request

```bash
# 基本建立
python "$SCRIPT_DIR/repos.py" create-pr my-repo \
  --source "feature/new-login" --target main \
  --title "feat: 新增登入功能"

# 附說明、連結工單、草稿模式
python "$SCRIPT_DIR/repos.py" create-pr my-repo \
  --source "feature/new-login" --target main \
  --title "feat: 新增登入功能" \
  --description "實作 Azure AD SSO 登入" \
  --work-items 123 124 \
  --draft
```

### 更新 Pull Request

```bash
# 更新標題和描述
python "$SCRIPT_DIR/repos.py" update-pr my-repo 45 \
  --title "fix: 修正登入問題" --description "解決 #123 回報的問題"

# 改為草稿 / 發布草稿
python "$SCRIPT_DIR/repos.py" update-pr my-repo 45 --draft
python "$SCRIPT_DIR/repos.py" update-pr my-repo 45 --undraft

# 關閉 PR（abandoned）
python "$SCRIPT_DIR/repos.py" update-pr my-repo 45 --status abandoned
```

### PR 留言與 Review Threads

```bash
# 列出所有 comment threads
python "$SCRIPT_DIR/repos.py" threads my-repo 45

# 新增 PR 整體留言
python "$SCRIPT_DIR/repos.py" comment-pr my-repo 45 "LGTM，可以 merge"

# 針對特定檔案某一行留言（inline comment）
python "$SCRIPT_DIR/repos.py" comment-pr my-repo 45 \
  "這裡應該要 handle None" --file "/src/api.py" --line 42

# 回覆某個 thread（thread_id 從 threads 指令取得）
python "$SCRIPT_DIR/repos.py" reply my-repo 45 3 "已修正，請再看看"

# 將 thread 標記為已解決
python "$SCRIPT_DIR/repos.py" resolve-thread my-repo 45 3
```

### 查詢 Pull Request

```bash
# Active PR（預設）
python "$SCRIPT_DIR/repos.py" prs <repo>

# 指定狀態：active / completed / abandoned / all
python "$SCRIPT_DIR/repos.py" prs <repo> --status all --top 30

# 取得單一 PR 詳情
python "$SCRIPT_DIR/repos.py" pr <repo> <pr_id>
```

### 查詢 Branch

```bash
# 列出所有 branch
python "$SCRIPT_DIR/repos.py" branches <repo>

# 篩選 feature branch
python "$SCRIPT_DIR/repos.py" branches <repo> --filter "feature/"
```

### 查看 Commit 歷史

```bash
# 最近 20 筆 commit（預設）
python "$SCRIPT_DIR/repos.py" commits <repo>

# 指定 branch，最近 50 筆
python "$SCRIPT_DIR/repos.py" commits <repo> --branch main --top 50
```

---

## 全文搜尋（Search）


> Search API 使用不同的 hostname（`almsearch.dev.azure.com`），但同一組 PAT 即可認證。

### 搜尋程式碼

在所有 repository 的檔案內容中做全文搜尋：

```bash
# 搜尋所有 repo
python "$SCRIPT_DIR/search.py" code "ConnectionString"

# 限定 repo 和 branch
python "$SCRIPT_DIR/search.py" code "ConnectionString" --repo my-repo --branch main

# 限定路徑前綴
python "$SCRIPT_DIR/search.py" code "TODO" --path "/src/api"

# 分頁（每次 25 筆，取第二頁）
python "$SCRIPT_DIR/search.py" code "TODO" --top 25 --skip 25
```

### 搜尋工單

在工單的標題、描述、留言中做全文搜尋：

```bash
# 基本搜尋
python "$SCRIPT_DIR/search.py" workitem "登入失敗"

# 加篩選條件
python "$SCRIPT_DIR/search.py" workitem "payment" --type "Bug" --state "Active"
python "$SCRIPT_DIR/search.py" workitem "timeout" --assignee "dev@company.com"
```

> 注意：`search workitem` 是**全文搜尋**，找的是任何欄位含有該關鍵字的工單；`work_items.py list --title` 是 WIQL 的 title-only 查詢，兩者用途不同。

### 搜尋 Wiki

```bash
python "$SCRIPT_DIR/search.py" wiki "部署流程"
python "$SCRIPT_DIR/search.py" wiki "API 規格" --wiki "my-project.wiki"
```

---

## Core 操作（組織 / 專案 / 團隊）


### 確認身份（whoami）

確認目前 PAT 對應的使用者，也可驗證連線設定是否正確：

```bash
python "$SCRIPT_DIR/core.py" whoami
```

### 列出組織內所有 Projects

```bash
python "$SCRIPT_DIR/core.py" projects
```

### 查看 Project 詳情

```bash
# 使用 ADO_PROJECT 環境變數
python "$SCRIPT_DIR/core.py" project

# 指定其他 project
python "$SCRIPT_DIR/core.py" project "MyOtherProject"
```

輸出包含：Process Template（Scrum / Agile / CMMI / 自訂）、版控類型、預設 Team。

### 列出 Teams

```bash
python "$SCRIPT_DIR/core.py" teams
python "$SCRIPT_DIR/core.py" teams --project "OtherProject"
```

### 查看 Team 成員

```bash
python "$SCRIPT_DIR/core.py" members "Backend Team"
```

### 列出 Sprints / Iterations

```bash
# 列出所有 sprint（使用 project 預設 team）
python "$SCRIPT_DIR/core.py" sprints

# 只看目前進行中的 sprint
python "$SCRIPT_DIR/core.py" sprints --current

# 指定 team
python "$SCRIPT_DIR/core.py" sprints --team "Backend Team" --current
```

輸出的 `time_frame` 欄位為 `past` / `current` / `future`，可用來確認 sprint 時間區間。

---

## 常見狀態值參考

不同 Process 範本的狀態值不同，常見如下：

| Process | 常見狀態 |
|---------|---------|
| Scrum | New / Active / Resolved / Closed |
| Agile | Active / Resolved / Closed / New |
| CMMI | Proposed / Active / Resolved / Closed |
| 自訂 | 依 Project Settings → Process 為準 |

若 `update --state` 回傳 400 錯誤，通常是狀態值拼字不符，先用 `get <id>` 確認目前的狀態後再調整。

---

## 錯誤處理

| 錯誤訊息 | 原因 | 處理方式 |
|---------|------|---------|
| `Missing credentials` | 憑證未設定 | 執行 `setup.py save --org ... --project ... --pat ...` |
| `HTTP 401` | PAT 失效或過期 | 請使用者重新產生 PAT |
| `HTTP 403` | PAT 權限不足 | 確認 PAT 包含 Work Items (Read/Write) 及 Code (Read) |
| `HTTP 404` | 工單 ID 或 repo 不存在 | 確認 ID 與 ADO_PROJECT 是否正確 |
| `HTTP 400` on update | 欄位值不合法（如狀態值拼字錯誤） | 先 `get` 確認目前欄位值，再調整 |
| 連線逾時 / `ProxyError` | 企業 Proxy 未設定 | 執行 `setup.py save --proxy http://proxy.corp:8080` |
| `SSL` / `certificate verify failed` | 企業自簽憑證 | 腳本已預設 bypass SSL，若仍失敗請確認 Proxy 設定正確 |
| `python3: command not found` | Windows 無 `python3` | 改用 `python` 或 `py -3` |
