# 團隊 AI SDLC 技能地圖

> **版本**：v1.0  
> **最後更新**：2025-04-12  
> **適用對象**：使用 Claude Code / Cline 進行日常開發的全體團隊成員

---

## 總覽

以下是團隊在 AI 輔助軟體開發生命週期（AI SDLC）中的完整技能地圖。每個階段列出對應可用的 Skill、使用時機，以及各 Skill 之間的協作關係。

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          AI SDLC 技能全景圖                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Phase 0           Phase 1           Phase 2           Phase 3              │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐           │
│  │ 環境安裝   │───▶│ 需求獲取   │───▶│ 需求確認   │───▶│ 規格產出   │           │
│  │           │    │ 與分析     │    │ 與設計     │    │ (SDD)     │           │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘           │
│   team-skill-      ado-devops      依規模選工具：    openspec               │
│   installer        legacy-code     小→直接描述                              │
│                    -analyzer       中→openspec                              │
│                    ado-pr-         大→brainstorm                             │
│                    knowledge                                                 │
│                                                                              │
│  Phase 4           Phase 5           Phase 6           Phase 7              │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐           │
│  │ 計畫撰寫   │───▶│ 實作與測試 │───▶│ Review    │───▶│ PR 與收尾  │           │
│  │           │    │           │    │ 與修復     │    │           │           │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘           │
│   write-plan       subagent-        ado-pr-review    ado-devops             │
│   openspec         driven-dev       ado-pr-knowledge superpowers            │
│                     TDD             npe-guardian     -workflow              │
│                     superpowers                      verification           │
│                     -workflow                        -before-completion     │
│                                                                              │
│  Phase 8                        跨階段工具                                    │
│  ┌───────────┐                  ┌─────────────────────┐                     │
│  │ 知識沉澱   │                  │ 快速查詢 / 分析      │                     │
│  │ 與文件化   │                  │ legacy-code-analyzer│                     │
│  └───────────┘                  │ tech-article-writer │                     │
│   Obsidian                      │ prometheus          │                     │
│   Draw.io                       │ skill-creator       │                     │
│   Wiki                          └─────────────────────┘                     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 階段 0：環境與技能安裝

### 目的
確保每位團隊成員的開發環境具備完整的 AI 技能工具鏈。

### 可用 Skill

| Skill | 用途 | 必要性 |
|:------|:-----|:------:|
| **team-skill-installer** | 一鍵安裝、更新、管理所有團隊共用 AI Skill | 必要 |

### 使用時機
- 新成員加入團隊
- 技能版本更新（`git pull` 後執行「Update skills」）
- 需要檢查目前安裝了哪些 Skill

### 操作方式
```
# 1. Clone 團隊 repo
git clone <repo-url> && cd clinewithADO

# 2. 啟動 AI Agent（Claude Code 或 Cline），然後說：
#    "幫我安裝技能" 或 "Help me install skills"

# 3. installer 會自動引導：
#    - 環境檢查（Python 3、Node.js）
#    - 基礎套件安裝（Superpowers、OpenSpec）
#    - 選擇性安裝其他 Skill
#    - 雙路徑安裝（~/.claude/skills/ + ~/.cline/skills/）
```

### 產出
- `~/.claude/skills/` — Claude Code 可用的 Skill
- `~/.cline/skills/` — Cline 可用的 Skill
- `~/.claude/plugins/superpowers/` — Superpowers 插件

---

## 階段 1：需求獲取與分析

### 目的
從 Azure DevOps 取得工單、理解需求背景，並對既有系統進行必要的程式碼盤點。

### 可用 Skill

| Skill | 用途 | 優先級 |
|:------|:-----|:------:|
| **ado-devops** | 從 ADO 查詢工單、閱讀 Description、查看 Sprint、確認 Branch | 必要 |
| **legacy-code-analyzer** | 盤點舊系統（VB6/C#/VB.NET）、追蹤函式關聯、產出移轉分析 | 視專案 |
| **ado-pr-knowledge** | 從團隊歷史 PR 提煉 Code Review 規則，供後續 Review 使用 | 建議 |

### 工作流程

```
ADO 工單 #123 (To Do, 有 Branch)
    │
    ├── 1. ado-devops：取得工單詳情
    │      python work_items.py get 123
    │
    ├── 2. ado-devops：確認 Branch 與 Repo
    │      python repos.py branches <repo> --filter "feature/"
    │
    ├── 3. （如為 legacy 移轉）legacy-code-analyzer：
    │      分析原有 VB6/C# 程式碼，產出 SA 說明 + Java CA API 規格
    │
    └── 4. ado-pr-knowledge：（首次或定期）
           從 PR 歷史提取團隊 review 規則，更新 CA 文件
```

### 典型指令
```
「幫我查工單 #123」
「這個 sprint 有哪些 To Do 的 Task？」
「幫我分析這個 VB6 子專案」
「整理一下我們團隊的 PR review 規則」
```

### 產出
- 工單需求摘要（來自 ADO）
- Legacy 分析報告（`.legacy-code-analyzer/` 或 `.legacy-analysis/`）
- 團隊 CA 規則庫（`ado-pr-knowledge/output/`）

---

## 階段 2：需求確認與設計

### 目的
釐清需求細節、探索方案、取得設計共識。依任務規模選擇適當的工具。

### 依規模選擇工具

| 任務規模 | 工具 | 說明 |
|:---------|:-----|:-----|
| **小型修改** | 直接描述 / 跳過 | Bug fix、小改動，直接在工單描述或對話中說明即可 |
| **中型功能** | OpenSpec 或直接描述 | 有一定複雜度、需要文件化的功能 |
| **大型功能** | Superpowers brainstorm | 跨模組、需要架構討論、多方案权衡的功能 |

### 工作流程

```
                    ┌──────────────────────┐
                    │  需求來源（階段 1 產出）│
                    └──────────┬───────────┘
                               │
              ┌────────────────┼──────────────────┐
              ▼                ▼                  ▼
     ┌──────────────┐  ┌──────────────┐   ┌──────────────┐
     │ 小型功能/修改  │  │ 中型功能開發  │   │ 大型產品功能  │
     │              │  │              │   │              │
     │ 直接描述需求  │  │ OpenSpec     │   │ Superpowers  │
     │ 或直接跳到   │  │ 或直接描述   │   │ brainstorm   │
     │ Phase 3/4    │  │              │   │              │
     └──────────────┘  └──────────────┘   └──────────────┘
              │                │                  │
              └────────────────┼──────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │   核准的設計/需求     │
                    └──────────────────────┘
```

### Superpowers Brainstorm 使用（大型功能）

```
觸發：「幫我 brainstorm 這個功能」
流程：
  1. AI 探索專案上下文（目錄結構、既有模式）
  2. 一次一個釐清問題（蘇格拉底式提問）
  3. 提出 2-3 個方案與取捨分析
  4. 分段呈現設計，讓使用者逐步確認
  5. 產出設計文件 → docs/superpowers/specs/
  6. 使用者審閱後核准
```

### OpenSpec 使用（中型功能）

```
觸發：「用 openspec 幫我產生規格」或 opsx-propose
流程：
  1. 一次產生 proposal + specs + design + tasks
  2. 產出在 openspec/changes/ 目錄
  3. 使用者審閱各文件
```

### 判斷規模的參考

| 特徵 | 小型 | 中型 | 大型 |
|:-----|:-----|:-----|:-----|
| 影響檔案數 | < 5 | 5-20 | > 20 |
| 涉及模組 | 單一模組 | 2-3 模組 | 跨系統 |
| 是否需要架構討論 | 否 | 視情況 | 是 |
| 預估工時 | < 4 小時 | 1-3 天 | > 3 天 |
| 範例 | 修正 API 回傳值 | 新增一組 CRUD API | 新增認證模組 |

### 產出
- 設計文件（`docs/superpowers/specs/` 或 `openspec/changes/`）
- 需求文件（含 User Story、Acceptance Criteria）
- 架構圖（Mermaid / ASCII）

---

## 階段 3：規格文件產出（SDD）

### 目的
將核准的需求轉化為結構化的規格文件，做為後續開發的契約。

### 可用 Skill

| Skill | 用途 | 產出格式 |
|:------|:-----|:--------:|
| **OpenSpec** (opsx-propose) | Proposal → Spec → Design → Tasks 一次產生 | `openspec/changes/` |

### 工作流程

```
核准的需求（階段 2 產出）
    │
    ├── 路徑 A：OpenSpec（一次產生所有文件）
    │   opsx-propose      → proposal + specs + design + tasks
    │   產出在 openspec/changes/ 目錄
    │   （若階段 2 已用 OpenSpec，此步已完成）
    │
    └── 路徑 B：小型修改，直接跳到 Phase 4
```

### 產出
- `openspec/changes/{change}/proposal.md` — 功能提案
- `openspec/changes/{change}/specs/` — 功能規格
- `openspec/changes/{change}/design.md` — 設計文件
- `openspec/changes/{change}/tasks.md` — 任務清單

---

## 階段 4：實作計畫撰寫

### 目的
將規格文件拆解為可執行、可驗證的小步驟。依專案規模選擇路徑。

### 依規模選擇路徑

| 專案規模 | 路徑 | 說明 |
|:---------|:-----|:-----|
| **小型 / 中型** | OpenSpec `opsx-apply` | 直接從 openspec tasks 實作，無需額外計畫 |
| **大型** | Superpowers `write-plan` | 產生精確 TDD 步驟計畫，交由 subagent 執行 |

### 工作流程

```
規格文件（階段 3 產出）
    │
    ├── 路徑 A：小型/中型專案
    │   直接使用 OpenSpec 的 tasks.md
    │   → 跳到階段 5 用 opsx-apply 執行
    │
    └── 路徑 B：大型專案
        ▼
    Superpowers write-plan
        │
        ├── 計畫品質要求：
        │   ✓ 假設實作者不了解專案上下文
        │   ✓ 使用精確檔案路徑
        │   ✓ 拆成 2-5 分鐘的小步驟
        │   ✓ 合適時採用 TDD 型步驟（先寫 failing test）
        │   ✓ 包含精確指令與預期結果
        │   ✓ 無 placeholder
        │
        └── 自我審查：
            1. Spec coverage 檢查
            2. 移除 placeholders
            3. 型別與命名一致性
```

### 產出
- 路徑 A：`openspec/changes/{change}/tasks.md`（已在階段 3 產出）
- 路徑 B：`docs/superpowers/plans/YYYY-MM-DD-<feature>.md`

---

## 階段 5：程式碼實作與測試

### 目的
依計畫逐步實作，每一個步驟都經過測試驗證。依專案規模選擇實作模式。

### 依規模選擇模式

| 專案規模 | 實作模式 | 說明 |
|:---------|:---------|:-----|
| **小型 / 中型** | OpenSpec `opsx-apply` | 輕量級，直接從 openspec changes 實作 |
| **大型** | Superpowers `subagent-driven-development` | 重度管控，每個 task 獨立 subagent + 雙階段 review |

### 可用 Skill

| Skill | 用途 | 適用規模 |
|:------|:-----|:--------:|
| **OpenSpec opsx-apply** | 從 openspec/changes/ 實作任務 | 小/中型 |
| **Superpowers subagent-driven-development** | 每個 task 派出獨立 subagent，雙階段 review | 大型 |
| **Superpowers TDD** | 強制 RED-GREEN-REFACTOR 循環 | 大型 |
| **Superpowers verification-before-completion** | 完成前必須最新驗證通過 | 通用 |
| **Superpowers systematic-debugging** | 遇到 bug 時的系統化除錯流程 | 失敗時觸發 |
| **npe-guardian** | Java NullPointerException 偵測與修復 | Java 專案 |

### 工作流程 A：OpenSpec 模式（小型/中型專案）

```
OpenSpec tasks.md（階段 3/4 產出）
    │
    ▼
opsx-apply：實作變更
    │
    ├── 1. 讀取 openspec/changes/{change}/ 下的所有文件
    ├── 2. 依序實作每個 task
    ├── 3. 每個 task 完成後驗證
    └── 4. 全部完成 → 可用 opsx-archive 歸檔

完成後 → 跳到階段 6（Code Review）
```

### 工作流程 B：Superpowers Subagent 模式（大型專案）

```
實作計畫（階段 4 產出）
    │
    ▼
superpowers-workflow：執行計畫
    │
    ┌─── 每個 Task 的流程 ─────────────────────────────┐
    │                                                     │
    │  1. 派出 implementer subagent                       │
    │     └── 帶完整 task 文字 + 上下文（不讓它自己讀 plan）│
    │  2. 處理問題、阻塞與澄清                             │
    │  3. 要求測試與 self-review                           │
    │  4. 🔒 Spec Compliance Review（不可跳過）            │
    │  5. 修正 spec 缺口                                   │
    │  6. 🔒 Code Quality Review                          │
    │  7. 修正品質問題                                     │
    │  8. ✅ 標記 task 完成                                │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    │
    ▼
內建紀律自動觸發：
    - TDD：新行為必須先寫 failing test
    - Verification：完成聲明前必須最新驗證
    - Debugging：失敗時進入系統化除錯（不猜測）
```

### TDD 鐵律（Superpowers 內建）

```
沒有先看到 failing test → 不能寫 production code

循環：
  1. 🔴 寫一個 failing test（只測一行為）
  2. 執行，確認因正確原因 fail
  3. 🟢 寫最小可通過的實作
  4. 執行，確認 pass
  5. 🔵 在綠燈狀態下重構
```

### Java 專案特殊工具

```
npe-guardian 工作流程：
  1. 偵測 build tool（Maven / Gradle）
  2. 執行 SpotBugs 掃描
  3. Source-aware triage（判斷 true/false positive）
  4. 最小安全修復
  5. 驗證修復結果
  6. 準備 PR
```

### 產出
- 通過測試的實作程式碼
- 對應的單元/整合測試
- SpotBugs 掃描報告（Java 專案）

---

## 階段 6：Code Review 與修復

### 目的
在 PR 合併前進行 AI 輔助的 Code Review，並自動修復發現的問題。

### 可用 Skill

| Skill | 用途 | 產出 |
|:------|:-----|:-----|
| **ado-pr-review** | AI Code Review + inline 留言 + Auto-fix | ADO PR comments |
| **ado-pr-knowledge** | 提供團隊 CA 規則做為 review 依據 | CA 規則文件 |
| **npe-guardian** | Java null-safety 偵測與修復 | PR with fixes |

### 工作流程

```
PR 建立後
    │
    ▼
ado-pr-review Phase 1：Review
    │
    ├── Step 1：取得 PR 概覽（檔案清單）
    │   python pr_fetch.py <repo> <pr_id> --files-only
    │
    ├── Step 2：取得完整檔案內容
    │   python pr_fetch.py <repo> <pr_id>
    │
    ├── Step 3：AI Code Review（依據 CA 規則）
    │   審查面向：
    │   1. 🔴 Security（SQL Injection、Secret、權限）
    │   2. 🟠 CA 規範（命名、分層、DI、Transactional）
    │   3. 🟡 Spring Boot 特定問題
    │   4. 🟡 Performance（N+1、無分頁）
    │   5. 🟡 例外處理
    │   6. 💡 Logging
    │   7. 💡 測試覆蓋
    │   8. 💡 程式碼品質
    │
    ├── Step 4：結構化呈現 Review 結果
    │   （先給使用者確認，不自動發布）
    │
    └── Step 5：使用者確認後發布 inline comments
        python pr_comment.py <repo> <pr_id> --from-file ...

PR 作者回覆「fix it」後
    │
    ▼
ado-pr-review Phase 2：Auto-fix
    │
    ├── 掃描有 fix-it 回覆的 threads
    ├── 理解 review comment 的修改意圖
    ├── 修改程式碼（只改指出的問題）
    ├── Commit 到 source branch
    └── 回覆並 resolve thread
```

### Review 嚴重度定義

| 等級 | 圖示 | 意義 | 處理原則 |
|:-----|:----:|:-----|:---------|
| BLOCKER | 🔴 | 安全漏洞、資料損壞 | 必須修正才能 merge |
| MAJOR | 🟠 | 重大 CA 違規、效能問題 | 強烈建議修正 |
| MINOR | 🟡 | 命名不符、小型違規 | 建議修正 |
| SUGGESTION | 💡 | 可讀性改善 | 可選擇採納 |

---

## 階段 7：PR、合併與收尾

### 目的
完成 PR 流程、合併分支、清理工作區。

### 可用 Skill

| Skill | 用途 |
|:------|:-----|
| **ado-devops** | 建立 PR、更新工單狀態 |
| **Superpowers finishing-a-branch** | 驗證測試 → 提出合併選項 → 清理 worktree |
| **Superpowers verification-before-completion** | 最終驗證 |

### 工作流程

```
實作完成（階段 5 + 6 通過）
    │
    ▼
Superpowers：完成開發分支
    │
    ├── 1. 跑完整測試集
    ├── 2. 確認正確的 base branch
    │
    └── 3. 提出選項：
        ├── 本地 merge 回 base branch
        ├── Push 並建立 Pull Request（ado-devops）
        ├── 保留目前 branch 不動
        └── 丟棄這份工作（需 typed confirmation）

PR 建立後（如選擇建立 PR）：
    │
    ├── ado-devops：建立 PR
    │   python repos.py create-pr <repo> \
    │     --source "feature/xxx" --target main \
    │     --title "feat: ..." --work-items 123
    │
    └── 更新工單狀態
        python work_items.py update 123 --state "Resolved"
```

---

## 階段 8：知識沉澱與文件化

### 目的
將開發過程中的發現、決策與學習記錄下來，供團隊未來參考。

### 可用工具

| 工具 | 用途 | 適用場景 |
|:-----|:-----|:--------:|
| **Obsidian** | 個人知識庫、開發筆記 | 日常記錄 |
| **Draw.io** | 架構圖、流程圖 | 設計文件 |
| **ado-devops (Wiki)** | 團隊共用文件 | 正式文件 |
| **tech-article-writer** | 技術文章撰寫（繁體中文） | 技術分享 |

### 可記錄的內容

```
知識沉澱項目：
├── 架構決策記錄（ADR）
│   └── 為什麼選 A 不選 B？取捨是什麼？
├── 踩坑記錄
│   └── 遇到什麼問題？Root cause？怎麼解的？
├── 學習筆記
│   └── 新技術/框架/模式的學習心得
├── 開發流程改進
│   └── Skill 使用體驗、改進建議
└── 技術文章
    └── tech-article-writer 產出正式文章
```

---

## 跨階段工具

### 快速程式碼查詢與分析

| Skill | 用途 | 什麼時候用 |
|:------|:-----|:----------:|
| **legacy-code-analyzer** | 深度分析 VB6/C#/VB.NET 舊系統 | 需要理解 legacy code 時 |
| **ado-devops (Search)** | 全文搜尋程式碼、工單、Wiki | 找特定關鍵字時 |
| **prometheus** | 自然語言轉 PromQL 查詢 | K8s 監控場景 |

### Skill 維護工具

| Skill | 用途 | 什麼時候用 |
|:------|:-----|:----------:|
| **skill-creator** | 建立、測試、改進新 Skill | 需要新 Skill 時 |
| **skill-manual-writer** | 自動產生 Skill 使用手冊 | Skill 需要文件時 |

---

## 建議補充的 Skill

以下是目前技能庫尚未涵蓋，但對團隊 AI SDLC 有價值的功能：

### 🔴 高優先級（建議儘速補充）

| 建議 Skill | 用途 | 理由 |
|:-----------|:-----|:-----|
| **commit-lint** | 強制 conventional commits 格式 | 統一 commit 訊息格式，方便自動產生 changelog |
| **changelog-generator** | 從 commit 歷史自動產生 CHANGELOG | 版本發布時必要，目前完全手動 |
| **security-scanner** | 依賴性弱點掃描 + SAST | 目前缺乏自動化安全掃描 |
| **env-setup** | 新專案環境一鍵設定 | 新人 onboard 或新專案啟動時的標準化 |

### 🟠 中優先級（建議逐步補充）

| 建議 Skill | 用途 | 理由 |
|:-----------|:-----|:-----|
| **api-doc-generator** | 從程式碼自動產生 API 文件 | API 文件容易過時，自動化可保持同步 |
| **adr-recorder** | 架構決策記錄（ADR）範本與管理 | 重要決策需要記錄理由，否則會遺失 context |
| **db-migration-helper** | 資料庫 schema 變更管理 | DB 變更容易出錯，需要結構化流程 |
| **incident-postmortem** | 事故後檢討文件產出 | 事故發生後需要結構化記錄原因與改善措施 |
| **dependency-updater** | 自動檢查並更新依賴版本 | 保持依賴最新，減少安全風險 |

### 🟡 低優先級（有餘力時補充）

| 建議 Skill | 用途 | 理由 |
|:-----------|:-----|:-----|
| **perf-benchmark** | 自動化效能基準測試 | 防止效能退化 |
| **accessibility-checker** | 無障礙性檢查 | 確保符合 WCAG 標準 |
| **i18n-helper** | 國際化字串管理 | 多語系支援的標準化 |
| **cost-estimator** | 雲端資源成本估算 | 避免非預期的雲端費用 |

---

## 附錄：完整技能清單

### 基礎套件

| 套件 | 說明 | 安裝方式 |
|:-----|:-----|:---------|
| **Superpowers** | 結構化 AI 工作流程：brainstorming、TDD、debugging、planning | team-skill-installer 自動安裝 |
| **OpenSpec** | Spec-driven development：proposal → spec → design → tasks | team-skill-installer 自動安裝 |

### 已安裝 Skill 總覽

| 分類 | Skill 名稱 | 說明 |
|:-----|:-----------|:-----|
| ADO 整合 | ado-devops | ADO 工單、PR、Repo、Wiki 操作 |
| ADO 整合 | ado-pr-review | AI Code Review + Auto-fix |
| ADO 整合 | ado-pr-knowledge | PR 歷史規則提煉 |
| 開發流程 | superpowers-workflow | 完整開發流程控管 |
| 開發流程 | superpowers-plugin | Brainstorming、TDD、Debugging、Planning 等 |
| 領域分析 | legacy-code-analyzer | VB6/C#/VB.NET 舊系統分析 |
| 領域分析 | npe-guardian | Java NullPointerException 修復 |
| 領域分析 | prometheus | Prometheus 查詢產生 |
| 文件工具 | tech-article-writer | 繁體中文技術文章 |
| 工具維護 | skill-creator | Skill 建立與測試 |
| 工具維護 | skill-manual-writer | Skill 文件產生 |

---

## 快速參考：我的任務要跑什麼流程？

```
┌─────────────────────────────────────────────────────────────┐
│ Q：我的任務是什麼？                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ □ 新功能開發（小型，< 4hr）                                  │
│   → ado-devops → openspec → opsx-apply                      │
│     → ado-pr-review → PR                                    │
│                                                             │
│ □ 新功能開發（中型，1-3 天）                                 │
│   → ado-devops → openspec → opsx-apply                      │
│     → ado-pr-review → PR                                    │
│                                                             │
│ □ 新功能開發（大型，> 3 天）                                 │
│   → ado-devops → brainstorm → openspec → write-plan         │
│     → subagent-dev → ado-pr-review → PR                     │
│                                                             │
│ □ Bug 修復                                                  │
│   → ado-devops → (legacy-analyzer) → superpowers-debug      │
│     → TDD fix → ado-pr-review → PR                          │
│                                                             │
│ □ Legacy 移轉（小型/中型）                                   │
│   → legacy-code-analyzer → openspec → opsx-apply            │
│     → ado-pr-review → PR                                    │
│                                                             │
│ □ Legacy 移轉（大型）                                       │
│   → legacy-code-analyzer → openspec → write-plan            │
│     → subagent-dev → ado-pr-review → PR                     │
│                                                             │
│ □ Java NPE 修復                                             │
│   → npe-guardian → auto-fix → ado-pr-review → PR            │
│                                                             │
│ □ 快速查詢 / 理解程式碼                                      │
│   → legacy-code-analyzer 或 ado-devops search               │
│                                                             │
│ □ 日常維護（PR Review）                                     │
│   → ado-pr-review → auto-fix → resolve                     │
│                                                             │
│ □ 安裝/更新技能                                             │
│   → team-skill-installer                                    │
│                                                             │
│ □ 建立新 Skill                                              │
│   → skill-creator → 測試 → skill-manual-writer              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **記住**：Skill 是輔助工具，不是強制流程。根據任務的複雜度選擇合適的階段和 Skill，小任務不需要走完整流程。最重要的是：**讓 AI 做重複性的工作，讓人做判斷性的工作。**