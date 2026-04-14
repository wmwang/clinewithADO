# 把 PRD 與 QA 補進團隊 AI SDLC — 規劃書

> **版本**：v0.1 (draft)
> **定位**：補齊 [team-ai-sdlc-guide](team-ai-sdlc-guide.md) 目前缺的 Phase 1.5（PRD）與 Phase 5.5（QA）
> **對象**：PM、RD、QA、Tech Lead

---

## 問題診斷

現況盤點後發現兩個缺口：

1. **需求規格長期鬆散**：PRD 格式不統一，RD 拿到的是聊天截圖／口頭說明／JIRA 一句話，AI 在 Phase 2–3（需求確認／SDD）花大量 token 補洞，最後還是常常做錯方向。
2. **QA 被長期忽略**：沒有系統化 test plan、沒有驗收標準（AC），測試只靠 RD 自測，regression 靠運氣。

這兩者對 AI SDLC 的殺傷力特別大 —— **AI 只會放大輸入的模糊度**。需求越糊，AI 產出的計畫、程式、PR 就越失焦；沒有 AC，AI 連自己寫的東西對不對都無法驗證。

---

## 目標

在**不打破現有 Phase 0–8** 的前提下：

- 訂一份**最小可行的 PRD 格式**（不是 30 頁大文件，是 AI 讀得懂、PM 寫得動）
- 讓 PRD 直接餵進 Phase 2（需求確認）與 Phase 3（SDD），**格式對齊 openspec / brainstorming**
- 補 **Phase 5.5 — QA 策略**，把 AC（驗收準則）綁進 PR 驗證
- 為 PM 開發兩個 skill，讓他們自己用 AI 寫 PRD，不用 RD 代筆

---

## Phase 1.5：PRD 格式

### 設計原則

1. **AI-first**：Markdown 單檔，AI 能一次讀完並自動抽取需求、AC、風險
2. **結構固定**：每份 PRD 都長一樣，AI 不用猜欄位
3. **可驗證**：每條需求都要有對應的 Acceptance Criteria（AC）
4. **版控**：PRD 進 git，放在 `docs/prd/YYYY-MM-<slug>.md`，跟 code review 一樣走 PR

### PRD 模板

```markdown
---
title: <一句話描述這個功能>
prd_id: PRD-2026-001
owner: <PM 姓名>
stakeholders: [<RD Lead>, <QA>, <設計>]
status: draft | review | approved | shipped
created: 2026-04-14
target_release: 2026-Q2
related_ado: [AB#12345, AB#12346]   # ADO work item
---

# 1. 背景與問題（Why）
- 使用者／業務目前遇到什麼問題？（1–3 句）
- 不做會怎樣？（量化：影響人數 / 成本 / 風險）

# 2. 目標與非目標（What / What Not）
## 目標
- [ ] G1：<可衡量的成果，例：把 XX 流程時間從 5 分鐘降到 1 分鐘>
- [ ] G2：...

## 非目標（明確排除）
- N1：<這次不做什麼，避免 scope creep>

# 3. 使用者與場景（Who）
| 角色 | 場景 | 目前痛點 | 期望結果 |
|------|------|----------|----------|
| 內部客服 | 每天處理 200 張工單 | 找資料要跨 3 個系統 | 一頁看完 |

# 4. 功能需求（Functional Requirements）
每條需求必須有唯一 ID，方便 RD 追蹤與 AI 拆解。

## FR-1：<需求標題>
- **描述**：...
- **優先級**：P0 / P1 / P2
- **驗收準則 (AC)**：
  - AC-1.1：Given <前提> When <動作> Then <結果>
  - AC-1.2：...
- **依賴**：FR-2, ADO-API

## FR-2：...

# 5. 非功能需求（NFR）
- 效能：P95 latency < 500ms
- 安全：僅 AD group `xxx-users` 可存取
- 可用性：99.5%
- 相容性：需支援 Edge 110+ / Chrome 110+

# 6. UX / 流程圖
- 貼 Figma / Draw.io 連結或圖片
- 關鍵使用流程用文字 bullet 列出：Step1 → Step2 → Step3

# 7. 風險與未決事項
| # | 風險 / 問題 | 影響 | 目前決策 | Owner |
|---|-------------|------|----------|-------|
| R1 | 第三方 API 尚未提供 | 高 | 先 mock | PM |

# 8. 里程碑
- M1 (YYYY-MM-DD)：PRD 定稿
- M2：SDD + 計畫完成
- M3：開發完成（內部可用）
- M4：上線

# 9. 參考資料
- 使用者訪談紀錄：<link>
- 競品分析：<link>
- 相關 ADO 工單：AB#...
```

### 為什麼長這樣

- **Frontmatter**：讓 skill 可以用 `yaml.safe_load` 直接抓元資料做索引
- **FR-x / AC-x.y 編號**：AI 寫計畫、寫測試時可以 1:1 對應
- **Given/When/Then**：直接可以轉成 QA 的 test case 與 TDD 的測試名
- **非目標欄位**：最常被忽略，但**對 AI 最重要**——告訴它別亂延伸

---

## 融入現有流程

PRD 定稿後就是 AI SDLC 的「輸入燃料」。對齊你現有的 Phase：

```
PM 寫 PRD (Phase 1.5) ──┐
                       ▼
Phase 2 需求確認  ── AI 讀 PRD frontmatter + FR 清單，產出疑問清單回 PM
                       ▼
Phase 3 SDD      ── openspec 把 FR-1..N 轉成 spec/<id>.md
                       ▼
Phase 4 計畫      ── write-plan 按 FR 拆任務，每個任務綁對應 AC
                       ▼
Phase 5 實作      ── TDD：每條 AC-x.y → 一條 test case
                       ▼
Phase 5.5 QA      ── 按 PRD 的 AC 跑完整驗收（下一節）
                       ▼
Phase 6 Review   ── ado-pr-review 檢查 PR 是否覆蓋所有 AC
                       ▼
Phase 7 PR       ── PR description 附 PRD 連結 + AC 勾選清單
```

**具體改動**：

| 階段 | 現況 | 加了 PRD 之後 |
|------|------|---------------|
| Phase 2 | 直接問 AI「我要做 X」 | `/prd-review PRD-2026-001`，AI 拿 PRD 做確認、找漏洞 |
| Phase 3 | openspec 從零開始 | openspec 讀 PRD FR 區塊，一鍵產 spec skeleton |
| Phase 4 | write-plan 靠對話 | plan 的每個 task title = `FR-x: <title>` |
| Phase 7 | PR 描述自由發揮 | PR 模板強制貼 AC checklist |

---

## Phase 5.5：QA 策略

### 核心原則

- **AC 即 Test**：PRD 的 AC-x.y 直接對應一條測試，不再讓 QA 從零寫 test plan
- **三層測試金字塔**：
  - **L1 自動化單元/整合測試**：RD 在 Phase 5 用 TDD 寫，對應 P0 AC
  - **L2 E2E / 驗收測試**：QA 寫，對應 FR 級別的主流程
  - **L3 探索式測試**：QA 人工，專注邊界、UX、安全
- **所有測試產物進 git**：`docs/qa/<prd_id>/test-plan.md` + 自動化腳本

### QA 工作流程

```
1. PRD approved
   ↓
2. QA 參與 Phase 3 SDD review（把關可測性：每條 FR 是否都有 AC？）
   ↓
3. QA 產 test-plan.md（用 skill qa-test-planner，見下節）
   - 從 PRD 抽所有 AC
   - 補 L3 探索式測試項目
   - 標註風險優先級
   ↓
4. RD Phase 5 實作時，L1 測試必須 pass
   ↓
5. QA 執行 L2 + L3（dev / staging 環境）
   ↓
6. 回填 test-plan.md 的執行結果
   ↓
7. PR 必須包含：通過的 AC 勾選 + QA sign-off 記錄
```

### test-plan.md 模板

```markdown
---
prd_id: PRD-2026-001
qa_owner: <QA 姓名>
env: dev | staging | prod
---

# Test Plan: <feature name>

## Coverage Matrix
| AC ID | 測試類型 | 自動化? | Owner | 狀態 |
|-------|----------|---------|-------|------|
| AC-1.1 | Unit    | Y | RD | ✅ |
| AC-1.2 | E2E     | Y | QA | ⏳ |
| AC-2.1 | 探索式  | N | QA | ⏸ |

## L2 E2E 案例
### TC-001：<對應 AC-1.2>
- 前置：...
- 步驟：1... 2... 3...
- 預期：...
- 實際：（QA 填）

## L3 探索式測試 Charter
- C-01：測試邊界輸入（最大字元、特殊符號）
- C-02：權限越界（切換角色）
- C-03：弱網 / 斷線恢復

## Regression Scope
- 列出本次可能影響的既有功能
- 關聯測試案例（舊 PRD 的 test-plan）

## Sign-off
- [ ] 所有 P0 AC 通過
- [ ] Regression 通過
- [ ] QA Lead：<name> <date>
```

### 要搭配的技術建置

| 層 | 建議工具 | 整合點 |
|----|---------|--------|
| L1 | 專案既有框架 (pytest/jest/xUnit) | CI 強制 coverage ≥ 70% for changed lines |
| L2 | Playwright / Cypress | 每晚跑，結果貼回 ADO |
| L3 | 無工具，產出 bug 寫 ADO work item | 連結回 PRD |

---

## 給 PM 的兩個 Skill

### Skill 1：`prd-writer`

**定位**：PM 自己跟 AI 對話就能寫出一份合格 PRD。

**觸發**：
- 「幫我寫 PRD」
- 「我有個新需求要寫規格」
- 「幫我整理這份會議紀錄成 PRD」

**執行流程**：
1. **收集階段**：AI 按 PRD 模板逐區訪談 PM（不是一次問 30 題，是分階段）
   - Round 1：背景 + 目標 + 非目標
   - Round 2：使用者 + 場景
   - Round 3：功能需求（每條都強制問 AC）
   - Round 4：NFR + 風險
2. **品質檢查**：AI 跑 checklist
   - [ ] 每條 FR 都有至少一條 AC？
   - [ ] AC 是否用 Given/When/Then？
   - [ ] 有無量化的成功指標？
   - [ ] 非目標有無列出？
3. **輸出**：寫到 `docs/prd/YYYY-MM-<slug>.md`，開 PR，tag stakeholders

**skill 檔案結構**：
```
Skills/prd-writer/
├── SKILL.md                 # 主入口，訪談流程
├── templates/
│   └── prd-template.md      # 上面的模板
├── checklists/
│   ├── quality-check.md     # 品質檢查清單
│   └── ac-format-guide.md   # Given/When/Then 範例
└── scripts/
    └── extract_frontmatter.py  # 給下游 skill 用的抽取工具
```

### Skill 2：`prd-review`

**定位**：PM 寫完 PRD 後，RD/QA/Tech Lead 用這個 skill 做審查，產出結構化回饋。

**觸發**：
- 「review PRD-2026-001」
- 「這份 PRD 有什麼問題？」

**執行流程**：
1. 讀 PRD，檢查格式合規（必要欄位、frontmatter）
2. **四個視角**平行分析（用 subagent 並行）：
   - **RD 視角**：技術可行性、依賴是否明確、NFR 是否合理
   - **QA 視角**：每條 AC 是否可測、邊界是否涵蓋
   - **安全視角**：有無 PII、權限、稽核需求
   - **Scope 視角**：是否過大該拆、非目標是否清楚
3. 產出 `docs/prd/<prd_id>-review.md`，列出 blocker / major / minor 問題
4. PM 修正後再跑一次，直到 0 blocker 才標 `status: approved`

### Skill 3（加碼）：`qa-test-planner`

**定位**：QA 拿到 approved PRD，一鍵產 test-plan.md 骨架。

**執行流程**：
1. 解析 PRD，抽出所有 FR 與 AC
2. 建 coverage matrix（每條 AC 對應測試類型建議）
3. 依產品領域（ADO MCP / Cline / 前端）套用對應的**探索式測試 charter 範本庫**
4. 產出 test-plan.md，QA 再補充情境細節

---

## 推動落地計畫

| 週次 | 工作項 | 負責 | 產出 |
|------|--------|------|------|
| W1 | 本文件 review + 定稿 | Tech Lead | prd-and-qa-plan.md v1.0 |
| W1 | 挑 1 個正在規劃的小功能當 pilot | PM + RD | 第一份 PRD |
| W2 | 開發 `prd-writer` skill | (你) | Skills/prd-writer |
| W2 | 用 pilot PRD 跑完整 Phase 2–7 | 團隊 | 驗證流程可行 |
| W3 | 開發 `prd-review` + `qa-test-planner` | (你) | 兩個 skill |
| W3 | QA 試跑 test-plan 模板 | QA | 第一份 test-plan.md |
| W4 | retrospective + 調整模板 | 全員 | v1.1 |
| W5+ | 新需求強制走 PRD 流程 | PM | — |

---

## 成功指標

3 個月後回看應達到：

- **100%** 新功能開發前有 approved PRD
- **≥ 80%** PR description 包含 AC checklist
- **≥ 70%** P0 AC 有自動化測試覆蓋
- **需求反覆次數下降**：RD 在 Phase 2 對 PM 提問次數 / PRD 減少 50%
- **Regression bug 季度下降**：相較上一季 -30%

---

## 附錄：與 GitAgent 概念對齊

這份計畫其實也補足了你上次提到的 GitAgent-style 架構中兩塊：

- **PRD 作為 agent 的輸入規格**：對應 GitAgent 的 `knowledge/` + `workflows/`
- **AC 作為 agent 的 RULES**：對應 GitAgent 的 `RULES.md`，讓 AI 知道「做完算數」的邊界
- **PR review checklist**：對應 Human-in-the-Loop 機制
