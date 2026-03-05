# AI Assets Manager

公司 AI 工具共同資產管理 Repo — 一鍵安裝 Superpower、BMAD Method、OpenSpec、Spec Kit

## 快速開始

### 方法一：`npx skills`（推薦，有 npm 環境者）

```bash
# 安裝到目前專案（互動式選擇 agents）
npx skills add /path/to/this-repo/ai-assets/superpower

# 安裝並指定 agents
npx skills add /path/to/this-repo/ai-assets/superpower -a cline -a opencode
```

安裝完成後 skills 會出現在各 agent 的命令清單中。

### 方法二：install.sh（無 npm 環境、或需要 BMAD/OpenSpec/Spec Kit）

```bash
git clone <this-repo>
cd <repo>
./install.sh
```

按照互動式選單選擇：
1. 要安裝哪些套件（Superpower / BMAD / OpenSpec / Spec Kit）
2. 使用的 AI 引擎（Cline / OpenCode / 兩者）
3. 安裝範圍（專案 / 全域）

> **差異**：`npx skills` 只支援 Superpower Skills。BMAD Method、OpenSpec、Spec Kit 需用 `install.sh`。

## 包含的套件

| 套件 | 說明 | 適用情境 |
|------|------|---------|
| **Superpower Skills** | AI 技能集：brainstorm、TDD、debugging、planning | 日常 coding |
| **BMAD Method** | 產品開發角色：analyst、PM、architect、dev、SM | 新功能規劃到實作 |
| **OpenSpec** | Spec-first 輕量開發流程 | 功能規格管理 |
| **Spec Kit** | GitHub 規格驅動開發方法論 | 嚴謹規格流程 |

## 支援的 AI 引擎

| 引擎 | 安裝位置（專案） | 安裝位置（全域） |
|------|-----------------|-----------------|
| **Cline** | `.clinerules/` | `~/.cline/rules/` |
| **OpenCode** | `.opencode/command/` | `~/.config/opencode/commands/` |

## 套件詳細說明

### Superpower Skills

技能文件放在 `.clinerules/superpower-skills/` 或 `.opencode/command/superpower/`。

AI 工具會自動讀取，使用方式：
```
"用 Brainstorming skill 來探索這個問題"
"用 TDD skill 來實作這個功能"
"用 Systematic Debugging skill 來找這個 bug"
```

**Skills 列表：**
- `brainstorming` — 結構化問題探索
- `writing-plans` — 建立實作計畫
- `finishing-a-development-branch` — 分支完成前的品質檢核
- `subagent-driven-development` — 平行 subagent 開發
- `executing-plans` — 計畫執行與進度追蹤
- `systematic-debugging` — 根因分析優先
- `root-cause-tracing` — 追蹤 bug 真正根源
- `defense-in-depth` — 多層驗證防禦
- `when-stuck` — 突破思考瓶頸
- `inversion-exercise` — 逆向思考找解法
- `test-driven-development` — Red-Green-Refactor

### BMAD Method

角色文件放在 `.clinerules/bmad/` 或 `.opencode/command/bmad/`。

呼叫方式：
```
"Mary, 幫我分析這個功能的需求"
"John, 請為這個功能建立 user stories"
"Winston, 設計這個系統的架構"
"Amelia, 請實作 Story 3: 使用者登入"
"Bob, 幫我規劃這個 sprint"
```

**角色：**
- `Mary` — Business Analyst（需求、研究）
- `John` — Product Manager（PRD、user stories）
- `Winston` — Architect（系統設計、技術決策）
- `Amelia` — Developer（TDD 實作、code review）
- `Bob` — Scrum Master（sprint 規劃、blockers）
- `Sally` — UX Designer（使用者體驗設計）

### OpenSpec

安裝後在專案根目錄建立：
```
openspec/
├── changes/    ← 進行中的功能
└── specs/      ← 系統規格（真實資料來源）
AGENTS.md       ← AI 操作說明
```

使用方式：
```
/opsx:propose <功能名稱>   ← 建立 proposal + specs + design + tasks
/opsx:apply                ← 實作待辦任務
/opsx:archive              ← 歸檔完成的變更
```

### Spec Kit

安裝後在專案建立：
```
.specify/
├── memory/constitution.md  ← 專案治理原則
└── templates/              ← 規格、計畫、任務模板
```

使用方式：
```
/speckit.specify  ← 建立規格文件
/speckit.plan     ← 建立技術計畫
/speckit.tasks    ← 產生實作任務清單
```

## 目錄結構

```
ai-assets/
├── superpower/
│   ├── README.md
│   └── skills/
│       ├── collaboration/
│       │   ├── brainstorming/SKILL.md
│       │   ├── writing-plans/SKILL.md
│       │   ├── finishing-a-development-branch/SKILL.md
│       │   ├── subagent-driven-development/SKILL.md
│       │   └── executing-plans/SKILL.md
│       ├── debugging/
│       │   ├── systematic-debugging/SKILL.md
│       │   ├── root-cause-tracing/SKILL.md
│       │   └── defense-in-depth/SKILL.md
│       ├── problem-solving/
│       │   ├── when-stuck/SKILL.md
│       │   └── inversion-exercise/SKILL.md
│       └── testing/
│           └── test-driven-development/SKILL.md
├── bmad-method/
│   ├── README.md
│   └── .bmad-core/
│       └── agents/
│           ├── analyst.md
│           ├── pm.md
│           ├── architect.md
│           ├── architect-ux.md
│           ├── dev.md
│           └── sm.md
├── openspec/
│   ├── README.md
│   ├── AGENTS.md
│   └── schemas/spec-driven/templates/
│       ├── proposal.md
│       ├── spec.md
│       ├── design.md
│       └── tasks.md
└── spec-kit/
    ├── README.md
    └── templates/
        ├── spec-template.md
        ├── plan-template.md
        ├── tasks-template.md
        ├── constitution-template.md
        └── commands/
            ├── specify.md
            ├── plan.md
            └── tasks.md
```

## 手動安裝（不使用 install.sh）

如果需要手動複製文件：

**Cline 專案安裝 Superpower：**
```bash
mkdir -p .clinerules/superpower-skills
cp -r ai-assets/superpower/skills/. .clinerules/superpower-skills/
```

**OpenCode 專案安裝 BMAD：**
```bash
mkdir -p .opencode/command/bmad
cp ai-assets/bmad-method/.bmad-core/agents/*.md .opencode/command/bmad/
```

**安裝 OpenSpec：**
```bash
cp ai-assets/openspec/AGENTS.md ./AGENTS.md
mkdir -p openspec/changes openspec/specs
cp -r ai-assets/openspec/schemas/spec-driven/templates ./openspec/.templates
```

**安裝 Spec Kit：**
```bash
mkdir -p .specify/memory .specify/templates/commands
cp ai-assets/spec-kit/templates/constitution-template.md .specify/memory/constitution.md
cp ai-assets/spec-kit/templates/*.md .specify/templates/
cp ai-assets/spec-kit/templates/commands/*.md .specify/templates/commands/
```

## Cline 全域安裝說明

Cline 全域規則需在 VS Code 設定中手動加入：

1. 打開 VS Code
2. `Cmd/Ctrl + Shift + P` → "Open User Settings (JSON)"
3. 加入：
```json
{
  "cline.customInstructions": "請參閱以下技能文件：~/.cline/rules/"
}
```

或在每個專案的 `.clinerules` 中直接引用。

## 授權

各套件保留其原始授權：
- Superpower: MIT (obra/superpowers-skills)
- BMAD Method: MIT (bmad-code-org/BMAD-METHOD)
- OpenSpec: MIT (Fission-AI/OpenSpec)
- Spec Kit: MIT (github/spec-kit)
