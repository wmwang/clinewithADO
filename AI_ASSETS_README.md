# AI Assets — 公司 AI 工具共同資產

公司共用的 AI Coding 資產，包含 Skills 技能包與 Spec 開發流程工具。

---

## 目錄結構

```
ai-assets/
├── skills/          # Superpower Skills 技能包（npx skills 格式）
│   ├── collaboration/
│   ├── debugging/
│   ├── problem-solving/
│   └── testing/
├── openspec/        # OpenSpec：proposal → spec → design → tasks 流程
└── spec-kit/        # Spec Kit：規格驅動開發框架
tools/
└── skills-1.4.4.tgz # Vendored skills CLI（離線安裝用）
install.sh           # OpenSpec / Spec Kit 安裝腳本
```

---

## Skills 技能包

### 安裝 skills CLI（一次性，需要 Node.js）

```bash
# 從本 repo 的 tools/ 安裝（不需外網）
npm install -g ./tools/skills-1.4.4.tgz
```

### 安裝 Skills 到你的專案

```bash
# clone 本 repo
git clone <this-repo> ai-assets-repo

# 安裝到目前工作的專案（互動選擇 agent）
cd your-project
skills add /path/to/ai-assets-repo/ai-assets/skills

# 或指定 agent
skills add /path/to/ai-assets-repo/ai-assets/skills -a cline
skills add /path/to/ai-assets-repo/ai-assets/skills -a opencode
```

### 包含的技能

| 分類 | 技能 | 說明 |
|------|------|------|
| **collaboration** | brainstorming | 開始新功能前的結構化探索 |
| **collaboration** | writing-plans | 撰寫任何工程師都能執行的實作計畫 |
| **collaboration** | executing-plans | 依計畫逐步實作，附進度回報 |
| **collaboration** | finishing-a-development-branch | 確保分支完整再 merge |
| **collaboration** | subagent-driven-development | 透過子 agent 平行執行複雜任務 |
| **debugging** | systematic-debugging | 假設驅動的結構化除錯流程 |
| **debugging** | root-cause-tracing | 找真正根因，不只修症狀 |
| **debugging** | defense-in-depth | 防禦性程式設計，防止 bug 擴散 |
| **problem-solving** | when-stuck | 卡住時的解法清單 |
| **problem-solving** | inversion-exercise | 反向思考：找失敗路徑再避開 |
| **testing** | test-driven-development | 先寫測試再實作的 TDD 循環 |

---

## OpenSpec / Spec Kit（工作流程工具）

這兩個不是 Skills 格式，透過 `install.sh` 安裝到專案目錄：

```bash
git clone <this-repo>
cd <repo>
./install.sh
```

互動選單選擇：
- 套件：OpenSpec 或 Spec Kit
- AI 引擎：Cline / OpenCode / 兩者
- 安裝範圍：專案（推薦）/ 全域

### OpenSpec 安裝後的目錄結構

```
your-project/
├── AGENTS.md                    # AI 指令
└── openspec/
    ├── changes/                 # 每個功能一個子目錄
    └── .templates/              # proposal / spec / design / tasks 模板
```

### Spec Kit 安裝後的目錄結構

```
your-project/
└── .specify/
    ├── memory/constitution.md   # 專案規範
    └── templates/               # spec / plan / tasks 模板
```

---

## BMAD Method

暫不納入，待官方轉為 Skills 格式後再整合。

---

## 更新 skills CLI

當 `skills` 有新版本時，在有外網的機器執行：

```bash
npm pack skills   # 產生 skills-x.x.x.tgz
# 將 tgz 複製到本 repo 的 tools/ 並更新 README 版本號
```
