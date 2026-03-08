# Spec-Kit Skills 使用手冊

> **格式**：[Agent Skills 開放標準](https://agentskills.io/specification)（由 Anthropic 創建，跨平台社群維護）
> **相容性**：Claude Code、Cursor、GitHub Copilot、Windsurf、Roo Code 及其他 26+ 平台

---

## 什麼是 Agent Skills？

Agent Skills 是一個輕量的開放格式，讓 AI agent 可以載入專門的知識與工作流程。每個 skill 是一個**資料夾**，資料夾內有一個 `SKILL.md` 檔案描述能力與執行步驟。

### Skill 的標準結構

```
skill-name/          ← 資料夾名稱 = skill 名稱
└── SKILL.md         ← 必要：指令 + 元資料
```

`SKILL.md` 使用 YAML frontmatter：

```markdown
---
name: skill-name
description: 這個 skill 做什麼（agent 用來判斷何時啟用）
---

## 使用方式
...
```

### Skill 如何被啟動？

**不是透過 slash command**。Agent 會掃描所有 `SKILL.md` 的 `description` 欄位，根據使用者的對話內容**自動判斷**啟用哪個 skill。使用者只需自然語言描述需求即可。

---

## Spec-Kit Skills 清單

| Skill 資料夾 | 用途 |
|-------------|------|
| `speckit-specify/` | 從描述建立 feature spec 與 git 分支 |
| `speckit-clarify/` | 釐清 spec 中的歧義（最多 5 個問題） |
| `speckit-plan/` | 產生實作計畫（research.md、data-model.md、contracts/） |
| `speckit-tasks/` | 從計畫產生依賴排序的任務清單 |
| `speckit-implement/` | 依序執行任務清單 |
| `speckit-analyze/` | 跨文件一致性分析（唯讀） |
| `speckit-checklist/` | 產生需求品質 checklist |
| `speckit-constitution/` | 建立/更新專案治理憲法 |
| `speckit-taskstoissues/` | 將任務清單轉為 GitHub Issues |

---

## 安裝方式

### 方式一：純 Skills 版本（本目錄，無需安裝）

將 skill 資料夾複製到你的 AI agent 對應的目錄：

| Agent | 目錄 |
|-------|------|
| Claude Code | `.claude/skills/` |
| Cursor | `.cursor/skills/` |
| GitHub Copilot | `.github/skills/` |
| Windsurf | `.windsurf/skills/` |
| Roo Code | `.roo/skills/` |

**複製指令範例（Claude Code）**：

```bash
# 複製單一 skill
cp -r skills/speckit-specify .claude/skills/

# 複製全部 skills
cp -r skills/speckit-* .claude/skills/
```

複製後，agent 在下次啟動時會自動掃描並載入。

### 方式二：CLI 版本（需安裝 specify-cli）

```bash
pip install specify-cli
specify init
```

CLI 版本提供額外功能：`specify new`、`specify plan`、`specify tasks` 等指令，以及 CI/CD 整合。

---

## 標準 SDD 工作流程

```
使用者描述需求
      ↓
[speckit-specify]  建立 spec.md + git 分支
      ↓
[speckit-clarify]  （選用）釐清歧義
      ↓
[speckit-plan]     建立 plan.md + research.md + data-model.md
      ↓
[speckit-tasks]    建立 tasks.md（依賴排序）
      ↓
[speckit-analyze]  （選用）跨文件一致性檢查
      ↓
[speckit-implement] 執行任務清單
```

---

## Pure Skills vs CLI 版本比較

| 面向 | Pure Skills | CLI 版本 |
|------|-------------|---------|
| **安裝需求** | 無（複製資料夾即可） | `pip install specify-cli` |
| **跨平台** | ✅ 26+ AI agents | ✅ 任何終端機 |
| **啟動方式** | 自然語言 → agent 自動偵測 | `specify new "功能描述"` |
| **Spec 位置** | `specs/{BRANCH}/spec.md` | `specs/{BRANCH}/spec.md`（相同） |
| **模板** | 內嵌在 SKILL.md 中 | 獨立模板檔案（可自訂） |
| **Extension Hooks** | ✅ 支援 `.specify/extensions.yml` | ✅ 支援 |
| **憲法系統** | ✅ `.specify/memory/constitution.md` | ✅ 相同 |
| **CI/CD 整合** | ❌ 需手動 | ✅ `specify check` 指令 |
| **GitHub Issues** | ✅（需 GitHub MCP server） | ✅（內建） |
| **客製化模板** | 直接修改 SKILL.md | 修改 `.specify/templates/` |

---

## 產出的文件結構

每個 feature 的文件儲存在 `specs/{分支名稱}/`：

```
specs/
└── 1-user-auth/
    ├── spec.md              ← speckit-specify 產出
    ├── plan.md              ← speckit-plan 產出
    ├── research.md          ← speckit-plan 產出
    ├── data-model.md        ← speckit-plan 產出
    ├── tasks.md             ← speckit-tasks 產出
    ├── contracts/           ← speckit-plan 產出（視需要）
    └── checklists/
        ├── requirements.md  ← speckit-specify 產出
        ├── ux.md            ← speckit-checklist 產出
        └── security.md      ← speckit-checklist 產出
```

專案治理文件：

```
.specify/
└── memory/
    └── constitution.md      ← speckit-constitution 產出
```

---

## 常見問題

**Q：Skills 會自動啟動嗎？**
A：是的。Agent 掃描所有 `SKILL.md` 的 description，根據你的對話自動決定使用哪個 skill。你不需要記住任何指令。

**Q：可以同時使用 CLI 和 Pure Skills 嗎？**
A：可以。兩個版本產出的文件格式完全相同，可以混用。

**Q：如何更新 skills？**
A：重新從本目錄複製最新版本的資料夾即可。

**Q：skills 支援哪些語言？**
A：所有 skill 指令使用繁體中文撰寫，但 SDD 工作流程本身語言無關——你的 spec、plan、tasks 可以用任何語言撰寫。
