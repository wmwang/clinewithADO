---
name: ado-pr-review
description: |
  針對 Azure DevOps PR 進行 AI Code Review，並可將 review 結果以 inline 留言形式發布到 ADO PR。
  主要用於 Java Spring Boot 專案，依據 CA 規則、Security、Performance、測試覆蓋率等面向審查。
  支援 Auto-fix：當 PR 作者在 review 留言下回覆「fix it」類指令，可自動修改程式碼並 commit 到 source branch。

  觸發情境包含（但不限於）：
  - 「幫我 review PR #123」、「看一下這個 PR 的程式碼」、「code review PR 45」
  - 「審查 repo xxx 的 PR #56」、「這個 PR 有沒有問題」
  - 「檢查 PR 的 security issue」、「看看有沒有 N+1 問題」
  - 「把 review 結果留言到 ADO」、「發 inline comment 到 PR」
  - 「review 完發 BLOCKER 留言」、「幫我貼 review 結果」
  - 「幫我 fix review 的建議」、「自動修 review 留言的問題」、「apply fix」
  - 「有哪些 review 留言說要修的」、「scan PR 有沒有 fix it 的回覆」

  即使使用者只說「看一下這個 PR」或「幫我 review 一下」，只要情境涉及 ADO PR，就應觸發此技能。
---

# ADO PR AI Code Review 技能

對 Azure DevOps PR 進行自動化 AI Code Review，涵蓋 CA 規範、Security、Performance、Spring Boot 最佳實踐與測試覆蓋。
支援兩個階段：
- **Phase 1 — Review**：分析程式碼，發布 inline review 留言到 ADO PR
- **Phase 2 — Auto-fix**：掃描 PR threads 中的「fix it」回覆，自動修改程式碼並 commit 回 source branch

---

## 設定（首次使用必讀）

憑證儲存於 `~/.ado-devops.env`。若已安裝並設定過 `ado-devops` 技能，設定會自動沿用，無需重新輸入。若未安裝 `ado-devops`，此技能內建的 `setup.py` 可獨立完成設定。

**Step 0：偵測 Python 指令**

```bash
python3 -c "import platform, sys; print(platform.system(), sys.version)"
```

| 系統 | 使用指令 |
|------|---------|
| Linux / macOS | `python3` |
| Windows | `python`（或 `py -3`） |

**Step 1：確認憑證設定**

```bash
python3 "$SCRIPT_DIR/setup.py" status
```

若 `"ready": false`，引導使用者執行：

```bash
python3 "$SCRIPT_DIR/setup.py" save \
  --org "tsmcit" \
  --project "AI Operation Center" \
  --pat "使用者提供的 PAT"
```

PAT 需要的權限：**Code (Read)**、**Pull Request Threads (Read & Write)**。

設定完成後，之後的操作不需重複。

---

## 工作流程

### Step 1：取得 PR 概覽

先快速列出變更的檔案，讓使用者確認範圍：

```bash
SCRIPT_DIR="<此 SKILL.md 所在目錄>/scripts"
python3 "$SCRIPT_DIR/pr_fetch.py" <repo> <pr_id> --files-only
```

輸出範例：
```json
{
  "pr": { "id": 45, "title": "feat: add payment service", "source_branch": "feature/payment" },
  "changed_files": [
    { "path": "/src/main/java/.../PaymentService.java", "change_type": "add" },
    { "path": "/src/main/java/.../PaymentController.java", "change_type": "edit" }
  ]
}
```

告知使用者本次將審查哪些檔案，詢問是否繼續或排除特定檔案。

---

### Step 2：取得完整檔案內容

```bash
python3 "$SCRIPT_DIR/pr_fetch.py" <repo> <pr_id>
```

若 PR 非常大（>10 個可審查檔案），可分批：

```bash
python3 "$SCRIPT_DIR/pr_fetch.py" <repo> <pr_id> --file "/src/main/java/.../PaymentService.java"
```

---

### Step 3：執行 AI Code Review

取得檔案內容後，**仔細讀取 `references/java_springboot_ca.md`**，然後逐一審查每個檔案。

**審查面向**（依重要性排序）：

1. **Security** — SQL Injection、Secret 硬編碼、輸入驗證、權限控制
2. **CA 規範** — 命名、分層、依賴注入、Transactional 使用
3. **Spring Boot 特定** — Bean lifecycle、AOP 代理陷阱、Lombok 使用
4. **Performance** — N+1 query、無分頁的 findAll、迴圈中的資源浪費
5. **例外處理** — 空 catch、事務回滾條件、對外暴露內部細節
6. **Logging** — System.out.println、字串拼接、敏感資訊
7. **測試覆蓋** — 新增功能是否有對應測試、測試類型是否合適
8. **程式碼品質** — 方法過長、巢狀過深、magic number、raw type

---

### Step 4：以結構化格式呈現 Review 結果

使用以下格式輸出 review（**先呈現給使用者確認，不直接發布**）：

```
## 🔍 PR Code Review：#<id> — <title>

**Repo**：<repo>  |  **Branch**：<source> → <target>  |  **作者**：<author>

---

### 📝 整體評估

<2-4 句整體評語，點出最重要的問題或優點>

**問題統計**：🔴 <N> BLOCKER | 🟠 <N> MAJOR | 🟡 <N> MINOR | 💡 <N> SUGGESTION

---

### 📁 `src/main/java/.../PaymentService.java`

| # | 嚴重度 | 行數 | 問題描述 | 建議修正 |
|---|--------|------|---------|---------|
| 1 | 🔴 BLOCKER | 45 | 字串拼接建構 SQL 查詢，存在 SQL Injection 風險 | 改用 `@Query` 搭配 `:param` 命名參數 |
| 2 | 🟠 MAJOR | 78 | 多步驟 DB 操作缺少 `@Transactional` | 在方法上加 `@Transactional(rollbackFor = Exception.class)` |
| 3 | 🟡 MINOR | 12 | 變數名稱 `usrNm` 不符命名規範 | 改為 `userName` |

---

### 📁 `src/main/java/.../PaymentController.java`

| # | 嚴重度 | 行數 | 問題描述 | 建議修正 |
|---|--------|------|---------|---------|
| 4 | 💡 SUGGESTION | 22 | 直接回傳 Entity 物件，應使用 DTO 隔離 | 建立 `PaymentResponse` DTO |

---

## ✅ 確認後，請告訴我要發布哪些留言：

- `post all` — 發布所有留言
- `post blockers` — 只發 BLOCKER
- `post blockers and majors` — 發 BLOCKER + MAJOR
- `post 1 2 5` — 發指定編號
- `post summary only` — 只發整體總結留言
- `skip` — 不發布，只做參考
```

> **重要**：絕對不要在未經使用者確認前自動發布留言。

---

### Step 5：產生 Review JSON 並發布

使用者確認後，產生 review JSON 寫入暫存檔，再呼叫 `pr_comment.py`。

**JSON 格式範例**：

```json
{
  "summary": "整體評估：本次 PR 新增 PaymentService，邏輯清晰，但有以下需要修正的問題。",
  "comments": [
    {
      "id": 1,
      "severity": "BLOCKER",
      "file": "/src/main/java/com/example/PaymentService.java",
      "line": 45,
      "message": "字串拼接建構 SQL 查詢，存在 SQL Injection 風險。\n\n**建議**：改用 `@Query` 搭配 `:param` 命名參數，或 `JdbcTemplate` 的 `?` 佔位符。"
    },
    {
      "id": 2,
      "severity": "MAJOR",
      "file": "/src/main/java/com/example/PaymentService.java",
      "line": 78,
      "message": "多步驟 DB 操作缺少 `@Transactional`，資料不一致風險。\n\n**建議**：加上 `@Transactional(rollbackFor = Exception.class)`。"
    }
  ]
}
```

**發布指令**：

```bash
# 寫入暫存檔
cat > /tmp/ado_review_<pr_id>.json << 'EOF'
{ ... }
EOF

# 發布所有留言（含 summary）
python3 "$SCRIPT_DIR/pr_comment.py" <repo> <pr_id> \
  --from-file /tmp/ado_review_<pr_id>.json

# 只發 MAJOR 以上（含 BLOCKER）
python3 "$SCRIPT_DIR/pr_comment.py" <repo> <pr_id> \
  --from-file /tmp/ado_review_<pr_id>.json \
  --min-severity MAJOR

# 只發指定編號
python3 "$SCRIPT_DIR/pr_comment.py" <repo> <pr_id> \
  --from-file /tmp/ado_review_<pr_id>.json \
  --ids 1 3 5
```

**輸出範例**：

```json
{
  "posted_count": 3,
  "error_count": 0,
  "summary_status": "posted",
  "posted": [
    { "id": 1, "severity": "BLOCKER", "file": "/src/.../PaymentService.java", "line": 45, "status": "posted" }
  ]
}
```

---

## 嚴重度定義

| 等級 | 圖示 | 意義 | 處理原則 |
|------|------|------|---------|
| BLOCKER | 🔴 | 安全漏洞、資料損壞風險、會造成 runtime 錯誤 | **必須修正後才能 merge** |
| MAJOR | 🟠 | 重大 CA 違規、效能問題、事務/回滾隱患 | 強烈建議修正 |
| MINOR | 🟡 | 命名不符規範、小型 CA 違規 | 建議修正 |
| SUGGESTION | 💡 | 可讀性改善、最佳實踐建議 | 可選擇性採納 |

---

## Phase 2：Auto-fix 流程

PR 作者在 review 留言下回覆「fix it」（或類似語意），可觸發 Auto-fix。

### Auto-fix 觸發關鍵字（不分大小寫）

英文：`fix it`、`fix this`、`apply fix`、`apply the suggestion`、`go ahead`、`ok`、`sounds good`  
中文：`修一下`、`幫我修`、`修掉`、`修正`、`套用`、`好`、`同意`

### Step 1：掃描有「fix it」回覆的 threads

```bash
python3 "$SCRIPT_DIR/pr_autofix.py" scan <repo> <pr_id>
```

輸出範例：
```json
{
  "pr_id": 45,
  "fixable_count": 2,
  "fixable_threads": [
    {
      "thread_id": 12,
      "file": "/src/main/java/com/example/PaymentService.java",
      "line": 45,
      "review_comment": "🔴 **[BLOCKER]**\n\n字串拼接建構 SQL...",
      "fix_reply": "fix it",
      "fix_reply_by": "偉民 王"
    },
    {
      "thread_id": 15,
      "file": "/src/main/java/com/example/User.java",
      "line": 15,
      "review_comment": "🟡 **[MINOR]**\n\nEmail 驗證過於寬鬆...",
      "fix_reply": "好",
      "fix_reply_by": "偉民 王"
    }
  ]
}
```

僅回傳狀態為 `active`（未 resolved）的 threads，已 resolve 的不重複處理。

### Step 2：閱讀 review_comment，理解修改意圖

對每個 fixable thread：
1. 讀取 `review_comment` 的完整建議
2. 若有 `file` 欄位，用 `pr_fetch.py --file` 取得現在的完整檔案內容
3. 根據建議修改程式碼，**確保只改動 review 指出的問題，不動其他部分**
4. 修改前先向使用者確認修改方向（除非使用者說「自動全部 fix」）

> 有些 thread 沒有 `file`（PR-level 留言，如「請加 .gitignore」），無法直接改程式碼，改以文字說明引導使用者手動處理。

### Step 3：寫出修改後的檔案，commit 到 source branch

```bash
# 1. 把修改後的內容寫到本機暫存檔
cat > /tmp/fix_Foo.java << 'EOF'
<修改後的完整檔案內容>
EOF

# 2. Commit 到 source branch
python3 "$SCRIPT_DIR/pr_autofix.py" push <repo> <source_branch> \
  --file "/src/main/java/com/example/Foo.java" \
  --content-file /tmp/fix_Foo.java \
  --message "fix: apply review suggestion — correct email validation in User.java"
```

**注意**：`--file` 是 repo 內的路徑（以 `/` 開頭），`--content-file` 是本機暫存檔路徑。

多個檔案須分別 push（每次 push 都是一個 commit）。

### Step 4：回覆並 resolve thread

每個 fix 完成後，回覆該 thread 並 resolve：

```bash
# 回覆 commit 資訊
python3 "$SCRIPT_DIR/pr_autofix.py" reply <repo> <pr_id> <thread_id> \
  "已修正，commit: abc1234 — 改用 regex 驗證 email 格式。"

# 將 thread 標記為已解決
python3 "$SCRIPT_DIR/pr_autofix.py" resolve <repo> <pr_id> <thread_id>
```

### Step 5：向使用者報告結果

```
## ✅ Auto-fix 完成

| Thread | 檔案 | 行數 | 處理結果 |
|--------|------|------|---------|
| #12 | PaymentService.java | 45 | ✅ Commit abc1234 — 改用 @Query 參數化查詢 |
| #15 | User.java | 15 | ✅ Commit def5678 — 改用 regex 驗證 email |
| #8  | (PR-level) | — | ⚠️ 需手動處理：請新增 .gitignore 並執行 git rm -r --cached out/ |
```

---

## 腳本說明

此技能的腳本位於 **SKILL.md 同層的 `scripts/` 子目錄**。執行前先取得 SKILL.md 的絕對路徑：

```bash
SCRIPT_DIR="<此 SKILL.md 所在目錄>/scripts"
```

| 腳本 | 用途 |
|------|------|
| `pr_fetch.py` | 取得 PR 資訊與變更檔案的完整內容 |
| `pr_comment.py` | 將 review 結果批次發布到 ADO PR |
| `pr_autofix.py` | 掃描 fix it 回覆、commit 修改、reply/resolve threads |
| `ado_client.py` | 共用 ADO HTTP client |
| `setup.py` | 設定憑證（`~/.ado-devops.env`） |

CA 規則參考：`references/java_springboot_ca.md`

---

## 錯誤處理

| 錯誤 | 原因 | 處理方式 |
|------|------|---------|
| `Missing credentials` | PAT/ORG/PROJECT 未設定 | 執行 `setup.py save ...` |
| `HTTP 401` | PAT 失效或過期 | 請使用者重新產生 PAT |
| `HTTP 403` | PAT 缺少 Code 或 Thread 寫入權限 | 確認 PAT 包含 **Code (Read & Write)** 與 **Pull Request Threads (Read & Write)** |
| `HTTP 404` | PR ID 或 repo 不存在 | 確認 repo 名稱與 PR ID |
| `[truncated]` | 檔案超過預設 1000 行 | 加 `--max-lines 2000` 或分段用 `--file` 讀取 |
| inline comment 失敗 | 行號超出實際檔案範圍 | 重新確認 PR 中的實際行號 |
| push HTTP 409 | Branch 已被其他 push 更新（objectId 不符） | 重新執行 `push`（腳本會重新取得最新 HEAD） |
