
# Agent Skill Hub

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                 │
  │              A G E N T    S K I L L    H U B                    │
  │                                                                 │
  │              一個 Repo，團隊所有 AI 技能的家。                      │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

> **Claude Code** 和 **Cline** 的共享技能庫 — 讓你的 AI coding agent 擁有企業級能力，只需一次 `git clone`。

[English](../README.md) | **繁體中文**

---

## 痛點

團隊每天都在用 AI coding agent。但 AI 出廠不會查你的 Azure DevOps 工單、不懂怎麼 review 你的 PR、也無法分析你的 VB6 舊系統。每個人各自寫 prompt，品質參差不齊，好用的技巧也無法分享。

**Agent Skill Hub** 把團隊知識轉化為可安裝的 AI 技能 — 有版控、有 code review、幾分鐘就能部署到每個人的電腦上。

---

## 專案內容

```
clinewithADO/
├── Skills/                         # 13+ 可安裝的 AI 技能
│   ├── ado-devops/                 # ADO 工單/PR/Repo/Wiki 操作
│   ├── ado-pr-review/              # AI Code Review（ADO PR）
│   ├── ado-pr-knowledge/           # 從 PR 歷史提煉 review 規則
│   ├── legacy-code-analyzer/       # VB6/C#/VB.NET 舊系統分析
│   ├── superpowers-plugin/         # Superpowers 離線安裝包
│   └── ...
│
├── .claude/skills/
│   └── team-skill-installer/       # 一鍵安裝引導技能
│       ├── SKILL.md
│       └── scripts/                # 跨平台 Python 腳本
│
└── Docker/                         # Cline + ADO MCP Docker 方案
    └── cline/
```

---

## 快速開始

### 1. Clone 專案

```bash
git clone <repo-url>
cd clinewithADO
```

### 2. 開啟 AI Agent

打開 **Claude Code** 或 **Cline**，確認工作目錄在 `clinewithADO/`。

### 3. 安裝技能

對 AI 說：

> 「幫我安裝技能」

**team-skill-installer** 會自動啟動，引導你完成：

1. 環境檢查（需要 Python 3，Node.js 可選）
2. 基礎套件安裝（Superpowers、OpenSpec）
3. 從完整目錄中選擇要安裝的技能
4. 雙路徑安裝到 `~/.claude/skills/` + `~/.cline/skills/`
5. 安裝摘要

完成。技能安裝在家目錄下，跨專案都有效，不會汙染任何單一 repo。

---

## 可安裝的技能

### Azure DevOps 整合

| 技能 | 說明 | 推薦 |
|:-----|:-----|:----:|
| **ado-devops** | 查工單、看 PR、管 Repo、搜 Wiki — ADO 全方位操作 | 必裝 |
| **ado-pr-review** | AI 自動 Code Review，在 ADO PR 上留 inline 意見 | 推薦 |
| **ado-pr-knowledge** | 從歷史 PR review 提煉團隊 Code Review 規則 | 推薦 |

### 開發流程

| 技能 | 說明 | 推薦 |
|:-----|:-----|:----:|
| **superpowers-workflow** | 完整開發流程：brainstorming → 計畫 → 實作 → review | 推薦 |
| **kiro-skill** | 互動式需求釐清 → 設計文件 → 任務清單 | 推薦 |
| **bmad-method** | 多代理人開發框架（PM / Architect / Dev 角色分工） | 進階 |
| **spec-kit-skill** | 憲章驅動開發（9 個子指令） | 進階 |

### 舊系統與特定領域

| 技能 | 說明 | 推薦 |
|:-----|:-----|:----:|
| **legacy-code-analyzer** | VB6 / C# / VB.NET 舊系統深度分析與報告產生器 | 推薦 |
| **npe-guardian** | Java NullPointerException 偵測與自動修復 | Java 專案 |
| **prometheus** | 用自然語言查 Prometheus 指標 | K8s 環境 |

### 文件與工具

| 技能 | 說明 | 推薦 |
|:-----|:-----|:----:|
| **tech-article-writer** | 繁體中文科技文章 / AI 教學文撰寫 | 推薦 |
| **skill-creator** | 開發並測試新的 AI 技能 | 進階 |
| **skill-manual-writer** | 為技能自動產生操作手冊 | 進階 |

### 基礎套件（建議全裝）

| 套件 | 說明 |
|:-----|:-----|
| **Superpowers** | AI 結構化工作流程 — brainstorming、TDD、debugging、計畫撰寫。離線安裝包已內建。 |
| **OpenSpec** | 規格驅動開發 — 提案 → 規格 → 設計 → 任務清單。 |

---

## 運作架構

```
┌──────────────────────────────────────────────────┐
│              Git Repo（唯一來源）                   │
│                                                  │
│  Skills/              ← 技能原始碼                │
│  .claude/skills/      ← 安裝器（自動觸發）         │
└──────────────┬───────────────────────────────────┘
               │  git clone / git pull
               ▼
┌──────────────────────────────────────────────────┐
│              同事的電腦                            │
│                                                  │
│  ~/.claude/skills/    ← Claude Code 讀取          │
│  ~/.cline/skills/     ← Cline 讀取                │
│  ~/.claude/plugins/   ← Superpowers plugin        │
└──────────────────────────────────────────────────┘
```

### 設計決策

| 決策 | 原因 |
|:-----|:-----|
| **離線安裝** | 公司內網可能無法存取外部 plugin marketplace |
| **Python 腳本** | 跨平台（Windows + macOS + Linux），不需額外安裝 |
| **雙路徑安裝** | 部分 Cline 版本不讀 `~/.claude/skills/`，需分開放 |
| **扁平目錄結構** | Cline 只讀第一層子目錄，不支援巢狀 |
| **更新前備份** | 覆蓋前保留舊版，降低風險 |
| **Git 版控散布** | 有變更歷史、`git pull` 同步、PR review 把關新技能品質 |

---

## 更新技能

```bash
git pull
```

然後跟 AI 說「更新技能」。安裝器會比對檔案 hash，只更新有變動的技能。

---

## 開發新技能

任何團隊成員都能貢獻技能：

```
Skills/my-new-skill/
├── SKILL.md          # AI agent 的指令文件
└── scripts/          # 選配的輔助腳本
    └── helper.py
```

寫一份含 YAML frontmatter（`name`、`description`）的 `SKILL.md`，加上逐步指令。發 PR，review 通過後全團隊就能安裝使用。

安裝 **skill-creator** 技能可以獲得引導式開發體驗。

---


## 系統需求

| 工具 | 必要 | 備註 |
|:-----|:----:|:-----|
| Git | 是 | Clone 及更新 repo |
| Python 3 | 是 | 安裝腳本使用（跨平台） |
| Claude Code 或 Cline | 是 | 至少一個 AI agent |
| Node.js | 選配 | 僅 OpenSpec npm 安裝需要 |

---

## 貢獻方式

1. 在 `Skills/your-skill-name/` 建立技能目錄    
2. 撰寫 `SKILL.md`，清楚描述觸發條件與執行步驟
3. 本機測試通過
4. 發 PR

可使用 [skill-creator](../Skills/skill-creator/) 技能取得引導式開發流程。

---

## 授權

內部使用。請依照貴組織的政策。
