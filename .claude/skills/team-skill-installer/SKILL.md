---
name: team-skill-installer
description: |
  團隊 AI 技能一鍵安裝與管理工具。引導同事安裝、更新、刪除團隊共用的 AI Skills，同時支援 Claude Code 和 Cline 兩種 AI Agent。
  觸發情境包含（但不限於）：
  - 「幫我安裝技能」、「安裝 skills」、「setup skills」、「install skills」
  - 「我剛 clone 下來，要怎麼開始」、「怎麼設定 AI 工具」
  - 「更新技能」、「刪除技能」、「我想看有哪些技能可以用」
  - 「skill installer」、「技能安裝」、「技能管理」
  - 「幫我裝 superpowers」、「安裝 openspec」
  即使使用者只是說「我是新來的，要怎麼用你們的 AI 工具」或「幫我設定開發環境的 AI 部分」也要觸發。
---

# Team Skill Installer — 團隊 AI 技能安裝引導

這個技能的目標是引導團隊同事完成 AI 技能的安裝。你的角色是一個友善的助手，用繁體中文與使用者互動，語氣親切但不囉嗦。

## 重要原則

- 使用者可能對 AI 技能、命令列、Node.js 完全不熟悉，所有步驟都要解釋清楚
- 每個階段結束後確認使用者狀態，不要一口氣跑完所有步驟
- 遇到錯誤時先診斷原因，給出明確的解決方案
- 安裝過程要保留使用者既有的設定，不能覆蓋他們已有的東西

## 跨平台須知

所有腳本都用 **Python 3** 撰寫，Windows / macOS / Linux 皆可直接執行。
執行前先偵測系統的 Python 指令名稱：

```bash
python3 --version 2>/dev/null || python --version 2>/dev/null
```

以下文件中以 `python3` 為例，如果使用者的系統只有 `python`，請自行替換。

## 執行流程

### Phase 0: 偵測本專案路徑與作業系統

先確認使用者是在本 git repo 的目錄中執行，並偵測作業系統：

```bash
git rev-parse --show-toplevel
```

```python
import platform, os; print(platform.system(), os.name)
```

用回傳的路徑設定 `REPO_ROOT`，並確認 `Skills/` 目錄存在。
如果不在 repo 中或找不到 Skills/，提醒使用者先 `cd` 到正確的目錄。

### Phase 1: 環境檢查

依序執行以下檢查，每一項失敗就引導使用者修復後再繼續：

#### 1.1 Python 環境

```bash
python3 --version 2>/dev/null || python --version 2>/dev/null
```

如果沒有 Python 3：
- **Windows**: 建議到 https://www.python.org/downloads/ 下載，安裝時務必勾選「Add to PATH」
- **macOS**: 建議用 `brew install python3` 或到 https://www.python.org/downloads/ 下載
- 安裝完後請使用者重新開啟終端機

#### 1.2 Node.js 環境（僅 OpenSpec npm 安裝時需要）

```bash
node --version 2>/dev/null && npm --version 2>/dev/null
```

如果沒有 Node.js 但使用者想用 npm 安裝 OpenSpec：
- **Windows**: 建議到 https://nodejs.org 下載 LTS 版本
- **macOS**: 建議用 `brew install node` 或到 https://nodejs.org 下載
- 沒有 Node.js 也不影響其他技能的安裝，OpenSpec 可以用本地技能檔替代

#### 1.3 npm Registry 設定（僅需要 npm 安裝時）

公司內部可能使用私有 npm registry。檢查目前設定：

```bash
npm config get registry
```

如果需要設定公司內部 registry，引導使用者：

```bash
npm config set registry <公司內部 registry URL>
```

> **詢問使用者**：「你們公司有自己的 npm registry 嗎？如果有的話請提供 URL，沒有的話我們就用預設的。」

#### 1.4 Claude Code CLI（僅安裝 Superpowers plugin 時有加分）

```bash
claude --version 2>/dev/null
```

如果沒有 `claude` CLI：不影響安裝，離線安裝腳本會直接寫入 plugin 檔案。

### Phase 2: 安裝基礎套件（Superpowers & OpenSpec）

這兩個是獨立的工具套件。因為公司內部網路可能無法直接存取外部 plugin marketplace，所以我們採用**離線安裝**方式——套件已預先打包在 repo 的 `Skills/` 目錄中。

先詢問使用者要安裝哪些：

> **基礎AI Coding開發工具流程套件（建議全裝）：**
>
> 1. **Superpowers** — AI 進階工作流程插件，提供 brainstorming、TDD、debugging、計畫撰寫等結構化開發流程。讓 AI 在寫程式前先思考、先規劃，品質大幅提升。
>    - 支援：Claude Code（plugin 方式）、Cline（規則檔方式）
>
> 2. **OpenSpec** — 規格驅動開發框架，從提案 → 規格 → 設計 → 任務清單，適合中大型功能開發。讓需求不再模糊，開發有跡可循。
>    - 支援：Claude Code、Cline（透過 skills 目錄安裝）
>
> 輸入 `1`、`2`、或 `all` 選擇要安裝的套件，輸入 `skip` 跳過此步驟。

#### 2A. Superpowers 離線安裝

repo 已內建 Superpowers 的完整 plugin 包，路徑為 `$REPO_ROOT/Skills/superpowers-plugin/`。
用 `scripts/install_superpowers.py` 執行離線安裝：

```bash
python3 "$REPO_ROOT/Skills/team-skill-installer/scripts/install_superpowers.py" "$REPO_ROOT/Skills/superpowers-plugin"
```

腳本會做以下事情：
1. **Claude Code 使用者**：複製到 `~/.claude/plugins/cache/` 並註冊到 `~/.claude/plugins/installed_plugins.json`，效果等同 `claude plugins install`
2. **Cline 使用者**：把 Superpowers 的 skills/ 目錄下的 SKILL.md 檔案複製到 `~/.cline/rules/superpowers/`，讓 Cline 可以讀取

如果 `superpowers-plugin/` 目錄不存在，代表 repo 還沒有打包 superpowers。此時可以走線上安裝的備用方案：
- Claude Code：`claude plugins install superpowers@claude-plugins-official`
- 手動：請有網路的同事先安裝，再從 `~/.claude/plugins/cache/claude-plugins-official/superpowers/` 複製整包進 repo

#### 2B. OpenSpec 安裝

OpenSpec 是 npm 套件，安裝方式依環境決定：

**如果有 Node.js 且可存取 npm registry（公司內部或外部）：**
```bash
npm install -g @fission-ai/openspec
```

**如果沒有 Node.js 或 npm 受限：**
OpenSpec 的核心技能已包含在 `$REPO_ROOT/Skills/openspec/` 中，可以直接用 Phase 4 的方式安裝為本地技能，不需要 npm。功能上只差 CLI 指令（`opsx`），但透過 AI agent 呼叫 skill 的方式一樣能用。

**npm 權限問題處理（如果需要 npm 安裝）：**
```bash
# macOS/Linux 遇到 EACCES
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
# 提醒使用者將 ~/.npm-global/bin 加入 PATH（寫進 ~/.zshrc 或 ~/.bashrc）
export PATH="$HOME/.npm-global/bin:$PATH"
```

**公司內部 npm registry：**
```bash
npm config set registry <公司內部 registry URL>
```
> 詢問使用者：「公司有自己的 npm registry 嗎？如果有請提供 URL，沒有的話用預設的就好。」

### Phase 3: 掃描並展示可用技能

執行 `scripts/scan_skills.py` 來取得技能清單：

```bash
python3 "$REPO_ROOT/Skills/team-skill-installer/scripts/scan_skills.py" "$REPO_ROOT/Skills"
```

這個腳本會輸出 JSON 格式的技能清單。用這份清單向使用者展示可安裝的技能。

展示格式範例：

> **可安裝的團隊技能：**
>
> | # | 技能名稱 | 說明 | 狀態 |
> |---|---------|------|------|
> | 1 | ado-devops | Azure DevOps 工單/PR/Repo 全方位操作 | 未安裝 |
> | 2 | legacy-code-analyzer | VB6/C#/VB.NET 舊系統分析報告產生器 | 已安裝 (v1) |
> | 3 | tech-article-writer | 繁體中文科技文章撰寫 | 需更新 |
> | ... | ... | ... | ... |
>
> **推薦安裝：** ado-devops, legacy-code-analyzer, skill-creator
>
> 輸入技能編號（可多選，用逗號分隔）、`all` 全裝、`recommended` 只裝推薦的，或 `skip` 跳過。

### Phase 4: 安裝選定的技能

對每個選定的技能，同時安裝到 Claude Code 和 Cline 兩個環境：

#### 安裝原理

每個技能會同時複製到兩個位置：
- **Claude Code**：`~/.claude/skills/<技能名稱>/`（Claude Code 自動讀取）
- **Cline**：`~/.cline/rules/<技能名稱>/`（Cline 透過全域規則讀取）

放在家目錄下，所以不管開哪個專案都能用，只要安裝一次就好。
如果已安裝過同名技能，腳本會先備份再覆蓋。

> **注意**：Cline 的全域規則需要在 VS Code 的 Cline 設定中啟用 `~/.cline/rules/` 路徑。安裝完成後提醒使用者。

#### 安裝腳本

使用 `scripts/install_skill.py` 對每個選定的技能執行安裝：

```bash
python3 "$REPO_ROOT/Skills/team-skill-installer/scripts/install_skill.py" \
  --source "$REPO_ROOT/Skills/$SKILL_NAME" \
  --skill-name "$SKILL_NAME" \
  --claude-dir "$HOME/.claude/skills" \
  --cline-dir "$HOME/.cline/rules" \
  --action install
```

Windows 使用者的路徑會自動轉換（`~` = `%USERPROFILE%`），不需要特別處理。

### Phase 5: 安裝摘要

安裝完成後，輸出清晰的摘要表格：

> **安裝完成！以下是您目前的技能清單：**
>
> | 技能名稱 | Claude Code | Cline | 說明 |
> |---------|:-----------:|:-----:|------|
> | ado-devops | installed | installed | Azure DevOps 操作 |
> | tech-article-writer | installed | installed | 科技文章撰寫 |
> | legacy-code-analyzer | updated | updated | 舊系統分析 |
>
> **如何使用：**
> - **Claude Code**：直接對話即可，技能會根據你的問題自動觸發
> - **Cline**：在 VS Code 中使用 Cline，技能規則會自動載入
>
> **後續操作：**
> - 重新執行此安裝程式可以更新或新增技能
> - 輸入「管理技能」或「skill管理」可以更新或刪除已安裝的技能

### Phase 6: 管理模式（更新/刪除）

如果使用者要求管理已安裝的技能，進入管理模式：

#### 偵測已安裝技能

```bash
python3 "$REPO_ROOT/Skills/team-skill-installer/scripts/scan_skills.py" \
  "$REPO_ROOT/Skills" \
  --check-installed \
  --claude-dir "$HOME/.claude/skills" \
  --cline-dir "$HOME/.cline/rules"
```

#### 更新技能

比較 repo 中的版本與已安裝的版本（透過檔案 hash），列出有差異的技能供使用者選擇更新。

#### 刪除技能

```bash
python3 "$REPO_ROOT/Skills/team-skill-installer/scripts/install_skill.py" \
  --skill-name "$SKILL_NAME" \
  --claude-dir "$HOME/.claude/skills" \
  --cline-dir "$HOME/.cline/rules" \
  --action uninstall
```

刪除前一定要跟使用者確認，並告知會刪除哪些路徑。

## 技能目錄說明（供展示用）

以下是本 repo Skills/ 目錄中各技能的簡要說明，在向使用者介紹時使用：

| 技能名稱 | 一句話說明 | 推薦程度 |
|---------|----------|---------|
| ado-devops | 查工單、看 PR、管 Repo — ADO 全方位操作 | 必裝 (使用 ADO 的團隊) |
| ado-pr-review | AI Code Review，自動在 ADO PR 留 inline 意見 | 推薦 |
| ado-pr-knowledge | 從歷史 PR review 提煉團隊 Code Review 規則 | 推薦 |
| legacy-code-analyzer | VB6/C#/VB.NET 舊專案深度分析與報告 | 推薦 (有舊系統) |
| tech-article-writer | 繁體中文科技文章 / AI 教學文撰寫 | 推薦 |
| kiro-skill | 互動式需求釐清 → 設計 → 任務清單 | 推薦 |
| bmad-method | 多代理人開發框架 (PM/Architect/Dev) | 進階 |
| npe-guardian | Java NullPointerException 偵測與修復 | 適用 Java 專案 |
| prometheus | 自然語言查 Prometheus 指標 | 適用 K8s 環境 |
| skill-creator | 開發並測試新的 AI 技能 | 進階 |
| openspec | OpenSpec 規格驅動開發指令集 | 搭配 OpenSpec 套件 |
| spec-kit-skill | GitHub Spec-Kit 憲章驅動開發 | 進階 |
| superpowers-workflow | Superpowers 完整開發流程整合 | 搭配 Superpowers 套件 |
| skill-manual-writer | 為技能自動產生操作手冊 | 進階 |
| k8s-prometheus | K8s + Prometheus 指標查詢 | 適用 K8s 環境 |
| pdf-book-study-kit | PDF 書籍學習輔助 | 選裝 |

## 錯誤處理

- **Node.js 未安裝**：明確告知安裝方式，提供 macOS 和 Windows 兩種指引
- **npm 權限問題**：引導設定 npm prefix 到使用者目錄
- **claude CLI 未安裝**：告知只影響 Claude Code 技能安裝，Cline 部分仍可繼續
- **技能目錄不存在**：提醒使用者確認是否在正確的 repo 目錄中
- **已安裝的技能版本較新**：警告使用者，讓他選擇是否要覆蓋（回退）
