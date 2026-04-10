---
name: ado-pr-knowledge
description: |
  從 Azure DevOps repo 的歷史 PR review 留言中，提煉出團隊專屬的 Code Review 規則庫。
  輸出繁體中文 Markdown 文件，可直接供 ado-pr-review skill 作為 CA 規則依據。

  觸發情境包含（但不限於）：
  - 「幫我分析 repo 的 PR 歷史」、「整理出我們團隊的 code review 規則」
  - 「從過去的 PR 提煉規則」、「建立我們自己的 CA 文件」
  - 「分析 ADO 的 review 留言」、「看看哪些問題最常出現」
  - 「更新 team rules」、「重新跑一次 PR 知識提煉」

  即使使用者只說「整理一下我們的 PR 規則」或「看看大家都在 review 什麼」，只要涉及從歷史 PR 學習，就應觸發此技能。
---

# ADO PR 知識提煉技能

從 ADO repo 過去所有 PR 的 review threads，分批撈取、聚類分析，輸出團隊專屬的繁體中文規則庫文件。

---

## 設定

### 1. 修改 `config.json`

`config.json` 位於 **SKILL.md 同層目錄**，控制要分析的 repo 與參數：

```json
{
  "repo": "javademo",
  "max_prs": 800,
  "include_wont_fix": true,
  "output_language": "zh-TW",
  "output_file": "output/team_rules.md"
}
```

| 欄位 | 說明 |
|------|------|
| `repo` | ADO repo 名稱，**要換 repo 只改這裡** |
| `max_prs` | 最多撈幾個 PR，建議略大於實際總數 |
| `include_wont_fix` | 是否納入 `wontFix` threads（建議 true，有參考價值） |
| `output_language` | 輸出語言（`zh-TW` / `en`） |
| `output_file` | 規則文件輸出路徑（相對於 SKILL.md 目錄） |

### 2. 確認憑證

```bash
python3 "$SCRIPT_DIR/setup.py" status
```

PAT 需要 **Code (Read)** 與 **Pull Request Threads (Read)** 權限。

---

## 選擇工作模式

| 模式 | 適用場景 | 說明 |
|------|---------|------|
| **標準模式**（單 agent） | PR 總數 < 200 | 全部 threads 一次分析，簡單快速 |
| **Sub-agent 模式**（Map-Reduce） | PR 總數 ≥ 200 | 每批交給獨立 sub-agent，避免 context 爆炸 |

> **判斷規則**：Step 1 確認 PR 數量後，若 PR > 200 自動改用 Sub-agent 模式；否則走標準模式。

---

## 標準模式工作流程

```bash
SKILL_DIR="<此 SKILL.md 所在目錄>"
SCRIPT_DIR="$SKILL_DIR/scripts"
WORK_DIR="/tmp/pr_knowledge_$(date +%Y%m%d)"
mkdir -p "$WORK_DIR"
```

---

### Step 1：快速確認 PR 總數

```bash
ADO_PROJECT="<project>" python3 "$SCRIPT_DIR/pr_history_fetch.py" --no-threads 2>/dev/null \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'共 {d[\"pr_count\"]} 個 PR')"
```

告知使用者共有幾個 PR，預估分析批次數（每批 50 個），讓使用者確認繼續。

---

### Step 2：分批撈取 PR threads

每批輸出一個 JSON 檔案：

```bash
TOTAL_PRS=780   # 用 Step 1 取得的數字
BATCH_SIZE=50
TOTAL_BATCHES=$(( (TOTAL_PRS + BATCH_SIZE - 1) / BATCH_SIZE ))

for i in $(seq 0 $((TOTAL_BATCHES - 1))); do
  echo "Fetching batch $i / $((TOTAL_BATCHES - 1))..."
  ADO_PROJECT="<project>" python3 "$SCRIPT_DIR/pr_history_fetch.py" \
    --batch-size $BATCH_SIZE --batch $i \
    > "$WORK_DIR/batch_${i}.json"
done
```

> 每批約 50 個 PR，撈取速度依 ADO 網速而定（通常每批 10–30 秒）。
> 若網路不穩，可單獨重跑某個 batch：`--batch 3`。

---

### Step 3：查看統計摘要

```bash
python3 "$SCRIPT_DIR/pr_knowledge_build.py" \
  --input-dir "$WORK_DIR" \
  --stats-only
```

輸出範例：
```json
{
  "total_prs": 156,
  "prs_with_threads": 89,
  "total_threads": 412,
  "by_status": { "fixed": 210, "active": 98, "wontFix": 54, "byDesign": 50 },
  "top_files": {
    "UserService.java": 34,
    "OrderController.java": 28,
    "PaymentInteractor.java": 21
  }
}
```

向使用者報告統計結果，確認資料量符合預期再進行分析。

---

### Step 4：產生 Claude 分析 Prompt

```bash
python3 "$SCRIPT_DIR/pr_knowledge_build.py" \
  --input-dir "$WORK_DIR" \
  > /tmp/analysis_prompt.txt

cat /tmp/analysis_prompt.txt
```

此指令會：
- 從所有 batch JSON 聚合所有 threads
- 輸出一份結構化的分析 prompt（含所有 thread 清單 + 統計 + 輸出格式要求）

---

### Step 5：執行 AI 分析

讀取 `/tmp/analysis_prompt.txt` 的內容，**按照其中的 prompt 指示**，對所有 thread 進行分析：

- 將相似問題歸類合併
- 計算每類問題的出現頻率
- 依頻率分為「高頻規則 / 中頻規則 / 單次重要問題」
- 整理 WONTFIX threads 為「團隊刻意不強制」清單
- 列出高風險檔案清單（最常被留言的檔案）

分析時要注意：
- FIXED threads 是最可信的訊號（雙方認可的問題）
- WONTFIX 是團隊風格選擇，不是問題，要如實記錄
- 避免把無關的留言強行歸類到規則，寧可遺漏也不要誤報

---

### Step 6：輸出規則文件

分析完成後，將結果寫入設定檔指定的 `output_file`（預設 `output/team_rules.md`）：

```bash
# 確認輸出目錄存在
mkdir -p "$SKILL_DIR/output"

# 寫入文件（Claude 直接生成內容後寫入）
```

**team_rules.md 輸出格式**：

```markdown
# {repo} 團隊 Code Review 規則庫
> 從 N 個 PR（M 則 review 留言）自動提煉
> 生成日期：YYYY-MM-DD

## 📌 高頻問題規則（出現 3 次以上）

### 規則 1：{規則標題}
- **出現次數**：N 次（佔 FIXED threads 的 X%）
- **反例**：...
- **正例**：...
- **嚴重度建議**：MAJOR

...

## ⚠️ 中頻問題（出現 2 次）
...

## 🔍 單次重要問題
...

## 🤝 團隊刻意不強制的事項
...

## 📁 高風險檔案清單
| 檔案 | 被留言次數 |
|------|----------|
| UserService.java | 34 |
...
```

---

### Step 7：整合至 ado-pr-review

生成的 `team_rules.md` 可直接複製到 `ado-pr-review/references/` 目錄，作為客製化 CA 規則，讓未來的 PR review 更貼近這個團隊的實際習慣。

```bash
cp "$SKILL_DIR/output/team_rules.md" \
   "<ado-pr-review 路徑>/references/team_rules.md"
```

在 `ado-pr-review` 的 review 過程中（Step 3），除了讀取 `java_springboot_ca.md`，也要讀取 `team_rules.md`，且 **team_rules.md 的規則優先級高於通用 CA 規則**（因為它反映的是這個團隊的實際決定）。

---

## Sub-agent 模式工作流程（Map-Reduce，PR ≥ 200）

整體架構：

```
Main agent
  ├── Step 1: 確認 PR 數量 → 決定批次數
  ├── Step 2: 分批 fetch → batch_0.json ... batch_N.json
  ├── Step 3: 同時 spawn N 個 sub-agents（Map）
  │     每個 sub-agent 獨立分析一批，回傳 JSON pattern summary
  │     → 儲存為 summaries/batch_summary_0.txt ... batch_summary_N.txt
  └── Step 4: main agent 執行 Reduce merge → team_rules.md
```

```bash
SKILL_DIR="<此 SKILL.md 所在目錄>"
SCRIPT_DIR="$SKILL_DIR/scripts"
WORK_DIR="/tmp/pr_knowledge_$(date +%Y%m%d)"
SUMMARIES_DIR="$WORK_DIR/summaries"
mkdir -p "$WORK_DIR" "$SUMMARIES_DIR"
```

---

### Sub-agent Step 1–2：確認數量、分批 Fetch（同標準模式）

執行方式與標準模式的 Step 1–2 完全相同。

---

### Sub-agent Step 3：Map — 並行 spawn sub-agents

**在同一則訊息中一次 spawn 所有 sub-agents**（並行執行，互相不等待）：

對每個 batch_N.json，為它產生一份分析 prompt：

```bash
# 為 batch 0 產生 per-batch prompt
python3 "$SCRIPT_DIR/pr_knowledge_build.py" \
  --input-file "$WORK_DIR/batch_0.json" \
  --per-batch-prompt \
  --batch-index 0 \
  --total-batches 16 \
  > /tmp/prompt_batch_0.txt
```

然後以這份 prompt 的內容啟動 sub-agent，指示如下：

```
請根據以下 prompt 分析這批 PR review threads，
輸出 JSON pattern summary（不要輸出其他文字），
完成後將輸出儲存到：$SUMMARIES_DIR/batch_summary_0.txt

[貼上 /tmp/prompt_batch_0.txt 的內容]
```

**重要**：所有 batch 的 sub-agent 在同一則訊息中一起 spawn，讓它們並行執行。
對 780 個 PR（16 批），等同 16 個 sub-agents 同時跑，總時間約等於單批時間。

---

### Sub-agent Step 4：Reduce — 合併所有批次結果

等所有 sub-agents 完成後（summaries 目錄有 16 個 .txt），main agent 執行 Reduce：

**1. 先統計總量（從所有 batch JSON 累加）：**

```bash
python3 "$SCRIPT_DIR/pr_knowledge_build.py" \
  --input-dir "$WORK_DIR" \
  --stats-only 2>/dev/null \
  | python3 -c "
import json,sys
s=json.load(sys.stdin)
print(f'total_prs={s[\"total_prs\"]} total_threads={s[\"total_threads\"]}')
"
```

**2. 產生 merge prompt：**

```bash
python3 "$SCRIPT_DIR/pr_knowledge_build.py" \
  --merge-prompt \
  --summaries-dir "$SUMMARIES_DIR" \
  --total-prs 780 \
  --total-threads 3120 \
  > /tmp/merge_prompt.txt
```

**3. Main agent 讀取 `/tmp/merge_prompt.txt`，執行分析**，跨批次合併相同 pattern、加總 occurrences，輸出最終 `team_rules.md`。

**4. 寫入輸出檔：**

```bash
mkdir -p "$SKILL_DIR/output"
# Claude 將分析結果寫入：
# $SKILL_DIR/output/team_rules.md
```

---

### Sub-agent 模式 context 預估

| 角色 | 每次 context | 說明 |
|------|------------|------|
| 每個 sub-agent | ~60K tokens | 50 PR × 8 threads × 150 tokens |
| Main agent (Reduce) | ~35K tokens | 16 summaries × ~2K tokens each |
| **合計峰值** | **~60K tokens** | Sub-agents 並行，互不干擾 |

相比標準模式直接跑 780 PR 的 ~936K tokens，**降低 94%**。

---

## 更換分析 Repo

只需修改 `config.json` 的 `repo` 欄位，其他步驟完全不變：

```json
{
  "repo": "backend-service",  // 改這裡
  ...
}
```

---

## 腳本說明

| 腳本 | 用途 |
|------|------|
| `pr_history_fetch.py` | 分批撈取 ADO PR threads，輸出 batch JSON |
| `pr_knowledge_build.py` | 聚合所有 batch，計算統計，產生 Claude 分析 prompt |
| `ado_client.py` | 共用 ADO HTTP client |
| `setup.py` | 憑證設定（共用 `~/.ado-devops.env`） |

---

## 錯誤處理

| 錯誤 | 原因 | 處理方式 |
|------|------|---------|
| `repo not specified` | `config.json` 未設定 repo | 修改 `config.json` 的 `repo` 欄位 |
| `HTTP 401` | PAT 過期 | 重新產生 PAT，執行 `setup.py save --pat ...` |
| `HTTP 403` | PAT 缺少 Code 或 Thread 讀取權限 | 確認 PAT 包含 **Code (Read)** + **Pull Request Threads (Read)** |
| 某個 batch 失敗 | 網路不穩 | 單獨重跑該 batch：`--batch N` |
| `config.json not found` | 設定檔路徑不對 | 確認 `config.json` 位於 SKILL.md 同層目錄 |
