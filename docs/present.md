# AI 導入半年 — 草稿內容（Markdown 版）

> **說明**：★=核心洞見（綠）  ▸=業界數據（黃）  ?=待解問題（紅）  →=行動建議（橙）  *斜體*=引言

---

## 第 1 頁｜AI 導入半年 — 成果與經驗分享（草稿）

**副標**：目的：全公司分享  ·  受眾：工程 + 非工程  ·  時間：30 分鐘

- *"software development is shifting from writing code to orchestrating agents that write code."*
  - — Anthropic, *2026 Agentic Coding Trends Report*

- ▸ Anthropic：teams can *"ship features in hours instead of days."*
- ▸ 84% 開發者已在用 AI，但真正部署 AI Agent 的企業只有 11%
- ★ AI 正在從「回答問題」走向「執行工作」
- ★ 從 Prompt / Chat，到 AI Coding Agent，再往更通用的 Agent 邁進
- ★ 真正的門檻已經不是會不會用 AI，而是能不能把 AI 從個人工具變成組織流程
- ★ 2026 很可能不是 AI 更會聊天的一年，而是 Agent 開始進入主流程的一年

- 我們這半年做了什麼
- 做出來了什麼效果
- 其他人可以怎麼用

- 從工具到方法論
- 從跟上到超前
- 我們不是在追一個新工具，而是在摸索下一代軟體開發流程

---

## 第 2 頁｜先定位我們在哪裡——OpenAI AI 五階段 × 業界現況

**副標**：用 OpenAI 的框架理解：技術在哪、企業在哪、我們在哪

### OpenAI AI 五階段（2024 年內部發布）

| Level | 定義 | 現況理解 |
| --- | --- | --- |
| 1. Chatbots | AI with conversational language | ChatGPT、Claude 問答；現在人人都在用，也是大多數企業的起點 |
| 2. Reasoners | Human-level problem solving | 模型能力已逼近；少數先進團隊開始實踐 |
| 3. Agents | Systems that can take actions | AI 自主行動、多步驟執行、跨工具協作；我們這半年主攻這裡 |
| 4. Innovators | AI that can aid in invention | AI 協助提出新方案，人類驗證 |
| 5. Organizations | AI that can do the work of an organization | 尚未實現；更像長期終點 |

- ★ **技術本身已在 Level 2→3，但大多數企業組織還在 Level 1**
- ★ **這個落差，就是我們這半年在努力縮短的距離**

---

## 第 3 頁｜為什麼「整個組織導入 AI」這麼難？

**副標**：真正困難的不是個人會不會用，而是怎麼讓 AI 進入組織主流程

| 對比 | 個人用 AI | 組織用 AI |
| --- | --- | --- |
| 改變範圍 | 改自己的習慣就好 | 流程、工具、文化、知識都要對齊 |
| 成功條件 | 一個人會用 | 可複製、可治理、可持續 |
| 常見結果 | 快，但不可重複 | 慢，但一旦成形就能複利 |

- ▸ **Deloitte 2025：只有 11% 企業真正部署 AI Agent**
- ▸ **Gartner：40% Agentic 專案預計 2027 年前被取消**
- ▸ **35% 企業連 Agentic AI 策略都還沒有**

### 三個根本障礙

| 障礙 | 問題本質 | 我們的應對 |
| --- | --- | --- |
| 1. Legacy 系統整合 | AI 很難插入現有流程 | Azure DevOps MCP 整合 |
| 2. 資料品質不足 | 垃圾進，垃圾出 | RAG + Knowledge Graph（下半年方向） |
| 3. 缺乏方法論 | 不知道從哪裡開始 | SDD + Skill + Agent Harness 體系 |

- ★ 其中最容易被低估的，其實是第三個：不是工具不夠，而是工作方法還沒換
- → 我們不只是在「用 AI 工具」
  - 我們在建立讓組織從 Level 1 走向 Level 3 的工程體系

---

## 第 4 頁｜思維轉換 (1/2)：從 Workflow AI 到 Agentic AI

**副標**：如果導入 AI 的難點是缺乏方法論，第一個要換的就是工作模型

- 前一頁講的是組織卡住的原因，這一頁講的是我們選擇用什麼方法跨過去

### Workflow AI 的本質

- 人設計每一個步驟，AI 執行
- 流程是固定的，AI 是可替換的零件
- 遇到例外狀況就卡住，需要人工介入

- 它的問題在哪裡？
  - 維護成本隨步驟數線性增長
  - 擴展性差，加新能力 = 重新設計流程
  - 過度依賴人的預測力——你預測不到所有狀況

- *You can't design workflows fast enough to match the complexity of reality.*

- 適合場景
  - 重複、高度結構化、邊界清楚的任務
  - 例：自動生成每日報表、固定格式的代碼補全

### Agentic AI 的本質

- 人給目標，AI 自己決定怎麼達成
- Agent 能使用工具、讀取環境、做決策、反覆修正
- 失敗了會自己重試，而不是等你來修

- Agentic 的四個核心能力
  - 規劃（Planning）：把大目標拆成小步驟
  - 工具使用（Tool Use）：呼叫 API、讀寫文件
  - 反思（Reflection）：觀察結果，調整策略
  - 記憶（Memory）：記住過去做過什麼

- 適合場景
  - 目標明確但路徑不固定的任務
  - 例：「把這個 bug 修掉」「幫我寫這個 feature 並通過所有測試」

- ★ **真正的 agentic 不是「AI 做更多事」，是「AI 開始負責任」**

> 📝 **筆記**：這頁最重要的論點：流程固定 vs 目標導向，是兩種根本不同的心智模型

---

## 第 5 頁｜思維轉換 (2/2)：工程師角色的轉變

**副標**：從「寫程式的人」到「管理一支 AI 團隊的人」

### 角色的三個階段

- 過去：寫程式的人
  - 打字速度、語法熟悉度是核心競爭力
  - 輸出 = 手寫的每一行 code

- 現在：審查 AI 輸出的人
  - 判斷 AI 說的對不對是核心競爭力
  - 輸出 = 經過你驗證的 AI 程式碼

- 未來：管理一支 AI 團隊的人
  - 系統設計、任務拆解、品質管控是核心競爭力
  - 輸出 = 多個 agent 協作的整體成果

- Addy Osmani（Google Chrome 工程 VP）：
- *The best software engineers won't be the fastest coders,*
  - but those who know when to distrust AI."

### 這意味著什麼？

- Critical thinking > coding speed
  - AI 擅長：syntax、boilerplate、重複模式
  - 人擅長：邊界條件、安全考量、業務邏輯判斷

- 建議：把 AI 的 PR 當成 junior 工程師的 PR 來審
  - 他寫的 code 可能沒問題，但你還是要看
  - 因為你是負責任的那個人

- ? 我們的 code review 流程有沒有因此改變？
- → 下半年：建立 AI 輸出的 review checklist（可以是一個 Skill）

- ★ **核心挑戰：如何讓資深工程師的判斷力可以傳承？**
  - 答案：寫成 RULES.md 和 Skill，讓 AI 也遵守同樣的標準

> 📝 **筆記**：這個角色轉變對非工程部門同樣重要：你的領域知識 × AI 執行力 = 真正的槓桿

---

## 第 6 頁｜個人用 AI vs 團隊用 AI——差在哪裡？

**副標**：這是整份簡報最重要的一個觀念

| 面向 | 個人使用 AI | 團隊使用 AI |
| --- | --- | --- |
| 知識來源 | 自己摸索 prompt | 共同 Skill 資產庫 |
| 上下文管理 | 每次重新解釋 | 標準化流程與共享規範 |
| 一致性 | 風格差異大 | 輸出可控、可 review |
| 傳承性 | 人走能力也走 | 知識留在 repo 裡 |
| 擴展性 | 快，但難複製 | 慢一點，但能複利 |

- 這不是個人的問題，這是缺乏基礎建設的問題
  - 就像每個人各自部署，沒有 CI/CD
  - 速度快，但不可靠、不可擴展、不可審計

- ▸ **哈佛研究：企業導入 AI 後，初級工程師**
  - 就業 6 季內下滑 9–10%；資深工程師幾乎不受影響

- 團隊 AI 的飛輪效應
  - 更多人用 → 更多 Skill 被貢獻
  - 更多 Skill → 每個人的 AI 更強
  - 每個人更強 → 更多成果 → 更多驗證
  - → 這是指數型成長，個人努力是線性的

- ★ **最危險的策略：讓所有人各自為政地用 AI**
  - 知識無法累積，優勢無法複製，能力不可傳承

> 📝 **筆記**：這頁給非工程人員的部分很重要，他們是全公司分享的多數受眾

---

## 第 7 頁｜Agent Runtime 選型：從框架導向到執行導向

**副標**：真正重要的不是工具名字，而是 AI 能不能直接進入工作環境做事

### 市場上其實有四種代表性路線

| 路線 | 代表 | 強項 | 代價 |
| --- | --- | --- | --- |
| 框架導向 | LangChain / LangGraph | 生態完整、抽象成熟、適合快速 POC | 抽象層多，debug 與維護成本高 |
| 多 Agent 編排框架 | Google ADK | 模組化強，Workflow / MCP / A2A 整合能力高 | 偏平台建設，不一定適合日常開發主流程 |
| 可執行的 Agent Runtime | Cline / Claude Code / OpenHands | CLI 直接操作環境，能讀檔、跑測試、改 code | 對工作環境與流程設計要求更高 |
| 產品化通用 Agent | DeepAgent | Browser + apps + coding + workflow 展示力強 | 較像完整產品能力，不完全等於可內化工程體系 |

### 框架導向的吸引力與限制

- 最初的吸引力
  - 以 LangChain 這類工具為代表
  - 豐富的整合生態、文件完整
  - Chain / Graph 抽象讓複雜流程可視化
  - 社群龐大，容易找到範例

- 踩過的坑
  - 版本破壞性更新頻繁，維護成本高
  - 過度抽象，出錯時 debug 很痛苦
  - Agent 能力還是需要大量手動組裝
  - 框架本身的複雜度掩蓋了業務邏輯

- ★ **核心洞見：當 LLM 本身已夠聰明，框架反而是負擔**
- → 適合：POC 探索、快速驗證概念

### 我們為什麼轉向可執行的 runtime

- 以 Cline / Claude Code 這類工具為代表
- 原生 Agentic，不需要框架包裝
- CLI 直接操作環境，AI 真的能「做事」
- Skill / MCP 生態成長快速
- Token 使用更可控，成本更透明

- 2025 業界共識
  - CLI-native 工具已成主流
  - AWS Kiro、Google Antigravity、JetBrains Junie 都走這條路

- ? 我們有沒有考慮過 OpenHands 或 SWE-agent？
  - → 可以補充我們評估過的替代方案

- ★ **現在要換框架的成本很低，但換 Skill 體系的成本很高**
  - → 把精力放在 Skill 比放在框架更值得
- ★ **Google ADK 跟 DeepAgent 很值得觀察，但它們提醒我們的是方向，不是要把主線變成追工具**
- → 適合：正式導入、長期維護、團隊協作

> 📝 **筆記**：工具選型的核心原則：選能讓 AI 直接操作環境的，而不是讓人幫 AI 搬運的

---

## 第 8 頁｜Agent Runtime 架構：模型層、執行層、介面層

**副標**：這不是工具競爭，而是分層組合；CLI 只是讓 AI 真正能動手的關鍵介面

### 三層運作架構

| 層級 | 代表 | 作用 | 適合何時用 |
| --- | --- | --- | --- |
| 模型層 | Claude SDK | 與模型 API 溝通，做基本 tool use | 需要高度客製化 API 整合 |
| 執行層 | Cline SDK | 構建 agent loop，管理工具執行與 context 策略 | 需要自動化任務執行 |
| 介面層 | OpenCode SDK | IDE 內嵌、程式碼感知、diff 顯示 | 開發者日常工作中使用 |

- ★ **這三層不是競爭關係，是組合關係**

### CLI 為什麼對 LLM 這麼重要？

| 沒有 CLI | 有 CLI |
| --- | --- |
| AI 只能看你貼給它的內容 | AI 能主動讀檔、執行、觀察結果 |
| 只能「說」 | 可以「做」 |
| 難以形成閉環 | 可讀 codebase、跑測試、看 diff、修 build error |

- 一個比喻
  - 沒有 CLI 的 AI = 只能「說」但不能「做」
  - 就像雇了一個員工，但不給他開電腦

- ? 我們的 CI/CD 有哪些可以接 CLI agent？

> 📝 **筆記**：工具選型的核心：選能讓 AI 直接操作環境的，而不是讓人幫 AI 搬運的

---

## 第 9 頁｜MCP vs Skill：最常被問到的問題

**副標**：兩個都是 AI 能力擴充，但解決的問題完全不同

### MCP 是什麼、做什麼

- MCP = Model Context Protocol（Anthropic 2024 年發布）
- 功能：讓 AI 能使用外部工具和服務

- MCP 能做到的事
  - 呼叫 Jira API，查詢或建立 issue
  - 讀取 GitHub PR，審查程式碼
  - 串接 Azure DevOps，取得 work item

- MCP 的安全風險（2025 年爆出）
  - 社群 MCP server 可能有後門或被棄用
  - 廣泛存取 email / CRM 成為安全漏洞
- ? 我們目前用了哪些 MCP？有沒有審查來源？
- → 建議：只用官方或自建的 MCP server

### Skill 是什麼、如何決定用哪個

- Skill = 預先提煉好的知識壓縮包
- 功能：讓 AI 按照你要的方式做事

- Skill 省 token 的原理
  - Without Skill：整份規範 ≈ 8,000 tokens
  - With Skill：精華摘要 ≈ 800 tokens  → 省 90%

- 如何決定用哪個？
  - 需要 runtime 資料或動作 → 用 MCP
  - 需要告訴 AI 怎麼做、做成什麼樣 → 用 Skill

- 最強組合：Skill 定義標準，MCP 執行動作
  - Skill 告訴 AI 怎麼寫 Jira ticket
  - MCP 讓 AI 真的去 Jira 建 ticket

- ★ **MCP 讓 AI 能力邊界擴大，Skill 讓 AI 在邊界內做得更好**

> 📝 **筆記**：MCP 是工具擴充，Skill 是知識壓縮。不衝突，搭配使用效果最好

---

## 第 10 頁｜Skill 資產庫：從個人走向團隊的關鍵機制

**副標**：Skill 庫是讓 AI 能力複利增長的工程基礎建設

### 沒有 Skill 庫的世界

- 小明花 3 小時調出一個很強的 coding Skill
- 小華完全不知道，自己重新弄了 2 小時
- 小李剛入職，他連有這件事都不知道
- 小明離職了，他的 Skill 消失了

- 這不是個人問題，這是制度問題
- 就像每個人各自管理自己的 library，沒有 npm

- Skill 庫解決的核心問題
  - 重複工作：同樣的問題只需要被解決一次
  - 品質一致：所有人用同一套最佳實踐
  - 知識傳承：人員異動不影響團隊能力
  - 新人上手：Skill 就是最好的 onboarding 文件

### 如何維護讓 Skill 庫保持活力

- 我們的目錄結構
  - skills/public/     ← 全公司共用
  - skills/team/       ← 團隊內部專用
  - skills/personal/   ← 個人實驗用

- 貢獻流程（任何人都可以）
  - 發現重複問題 → 寫成 Skill 草稿 → PR
  - 至少 2 人 review，附上使用範例
  - Merge 後在 team channel 公告

- 讓 Skill 庫有生命力的關鍵
  - 不要追求完美才提交，先提交再改
  - 每季 review：淘汰過時 Skill

- ★ **Skill 庫是團隊 AI 能力的複利引擎**
  - 每貢獻一個 Skill，全員同時受益

> 📝 **筆記**：建立 Skill 庫的心態轉換：從「我學到了什麼」到「我讓團隊學到了什麼」

---

## 第 11 頁｜GitAgent：Git Repo 就是你的 AI Agent

**副標**：最新開源專案 open-gitagent/gitagent — 你的直覺跟業界正在收斂到同一個答案

### GitAgent 解決什麼問題？

- 每個 AI 框架有自己的 agent 定義格式
  - Claude Code、OpenAI、LangChain、CrewAI 互不相容
  - 換框架就要重新定義 agent，非常痛苦

- GitAgent 的解法：開放標準
  - 你的 Git repo 就是你的 AI Agent
  - 把 agent 的定義全部用檔案存在 repo 裡
  - 用 git 管理，任何框架都能讀

- 關鍵特性
  - Framework-agnostic：同一個 repo，切 -a 就換框架
  - Git-native：版控、branch、diff、PR 天然支援
  - Composable：agent 可以 extends 繼承其他 agent

- ★ **這不只是工具，是一個像 HTTP 一樣的開放標準**
- ▸ **發布後迅速在 Hacker News 引發熱烈討論**

### GitAgent Repo 的結構

- agent.yaml    ← Manifest（名稱、版本、模型）
- SOUL.md       ← 身份、個性、溝通風格
- RULES.md      ← 硬性約束、must-always / must-never
- SKILL.md      ← 技能定義（跟我們的 SKILL.md 一樣！）
- MEMORY.md     ← 持久記憶、學習紀錄
- hooks/        ← bootstrap / teardown 鉤子
- workflows/    ← 常用工作流程定義

- 執行方式（一行指令）
  - $ npx gitagent run -r github.com/你的-agent -a claude
  - $ npx gitagent run -r github.com/你的-agent -a openai
  - → 同一個 repo，切換 -a 就換框架

- ★ **Agent 版本管理 = 程式碼版本管理，完全一致的心智模型**

> 📝 **筆記**：GitAgent 是 2025 年最值得關注的開源專案之一，它把我們一直在做的事標準化了

---

## 第 12 頁｜我們 vs GitAgent：我們的直覺是對的

**副標**：我們獨立走到了跟業界開源標準幾乎相同的地方

### 我們做了什麼 vs GitAgent 多了什麼

- 我們已經有的（核心 80%）
  - → Git repo 存放所有 SKILL.md
  - → PR review 才能 merge，品質控管
  - → 全團隊 clone 共用，知識不因人而異
  - → 按需讀入 skill，節省 token

- GitAgent 多了的（可以借鑑）
  - → SOUL.md：agent 的身份和行為準則
  - → RULES.md：硬性約束清單（AI 絕對不能做的事）
  - → gitagent validate：自動驗證 skill 格式
  - → extends：繼承鏈讓多層規則可組合

- ★ **我們的直覺是對的——Git + Skills + 版控 是正確答案**
- ★ **差別只是 GitAgent 把它做得更完整、更標準化**

### SOUL.md / RULES.md 分層管理

- 常見疑問：不同成員有不同設定，放 team repo 會限制大家嗎？

- 解答：分兩層管理
  - Team repo 放：工程紀律（不可逾越的邊界）
  - 例：不能 commit API key、必須有 rollback
  - 個人本地放：工作風格（個人偏好）
  - 例：AI 回應詳細程度、語言偏好

- RULES.md 只放「工程紀律」，不放「個人風格」
- SOUL.md 只放「大家都同意的工作方式」

- → 建議：先不加 SOUL.md 和 RULES.md
  - 等 Skill workflow 熟了，再討論是否標準化 agent 行為
- ★ **Skills 是最沒有爭議的起點，因為它只是「知識」，不是「約束」**

> 📝 **筆記**：這兩頁讓全公司看到：我們不是在跟風用 AI 工具，我們在建立跟業界最前沿接軌的 AI 工程體系

---

## 第 13 頁｜Agent Memory：原來我們前面都在解這個問題

**副標**：當 Skill 與 Git-native 資產逐漸成形，我們才更清楚看到：memory 其實是核心問題

### 預設的 LLM 是無記憶的

- 每次對話結束，一切歸零
- 同樣的事要反覆解釋給 AI 聽
- AI 不知道你上次踩了什麼坑
- AI 不知道你的專案有什麼規範

- 開發者最大的痛點（2025 業界調查）：
- *Agent forgets past decisions, fails to recognize past patterns*
- *I want agents to remember project history and my preferences*
- *Having to re-explain context every session is exhausting*

- ▸ **2026 年最多開發者回饋的需求 = 跨對話持久記憶**
- ★ **Skill 體系、Git-native 資產、可追溯工作流，本質上都在解 memory 問題**

### 四種記憶類型

| 類型 | 特性 | 適合存什麼 |
| --- | --- | --- |
| In-Context Memory | 最快，但有 token 上限 | 當前任務的即時工作記憶 |
| External Memory Store | 可跨對話持久化 | 大量歷史紀錄、檢索型知識 |
| Skill | 知識壓縮、讀入即用 | 規範、最佳實踐、固定流程 |
| File System / Code | 最直觀、可版控、可回溯 | 決策紀錄、程式碼狀態、產出物 |

- ★ **記憶的本質不是「AI 記得什麼」，而是「知識存在哪裡、誰管理」**

> 📝 **筆記**：這頁放在 Skill / Git 之後會更像總結：我們不是先想到 memory，反而是先做出了一套 memory 的工程解法

---

## 第 14 頁｜如果公司要做 AI Agent：建議的最小規格

**副標**：不是把 LLM 接上 API 就夠了；至少要把角色、編排、記憶、工具、規則、安全、評估定義清楚

### 一個 AI Agent 最低限度要定義的 7 個規格

| 規格面向 | 最少要回答的問題 |
| --- | --- |
| 1. Role | 這個 agent 負責什麼、不負責什麼？輸入、輸出、成功條件是什麼？ |
| 2. Orchestration | 單 agent 還是多 agent？哪些步驟可以自治，哪些地方必須有人類 checkpoint？ |
| 3. Memory | 要記什麼、記多久、存在哪裡？In-context、Skill、檔案、DB 各自負責哪一層？ |
| 4. Tools / Actions | 它能不能真的做事，而不是只回答問題？MCP、CLI、API、Browser 哪些能力要開、哪些不能開？ |
| 5. Rules / Skills | 它要遵守哪些規則？Skill 負責「怎麼做」，Rules 負責「不能怎麼做」 |
| 6. Safety / Audit | 權限怎麼控？錯了怎麼 rollback？誰可以審核？log 與 Git 紀錄怎麼留？ |
| 7. Evaluation | 怎麼知道它有用？成功率、成本、延遲、人工介入率怎麼量測？ |

- ★ **沒有規格的 agent，只是把 prompt 包成 service**
- ★ **真正的難點不是模型選型，而是 orchestration、memory、tools、rules、audit 能不能一起成立**
- → 建議起點：先做單 agent、少量工具、明確 Skill、可回滾，再逐步走向多 agent

> 📝 **筆記**：這頁的目的不是讓大家馬上做 agent，而是建立共同語言：未來不管是做服務 AI 化還是新 server agent 化，都先拿這 7 點來對齊

---

## 第 15 頁｜公司內部使用 LLM 的兩個落地限制

**副標**：不是模型能力問題，而是企業環境前面往往還有 proxy / gateway / 安控設備

### 在我們公司，如果要把 LLM 接進正式流程，至少要先注意兩件事

- 1. **回應串流要用 Streaming SSE 來設計**
  - 前端 / 服務端最好預設支援 Server-Sent Events
  - 不要假設一次 request 就能等到完整結果再回傳
  - Agent 任務一長，若沒有串流，使用者體感會很差，也更難做中途狀態呈現
  - 在經過公司內部 gateway 或 proxy 時，SSE 往往也是比較容易被既有通道接受的模式

- 2. **Prompt / Message 格式要盡量單純**
  - 先以最基本的 `system` / `user` 這種簡單 message 結構為主
  - 不要一開始就假設複雜的多層 metadata、特殊 role、客製欄位都能被完整透傳
  - 如果格式太花，容易在中間層被改寫、截斷，或直接不相容

### 為什麼會這樣？

- 很可能不是 LLM 本身有限制
- 而是 **我們公司的 LLM 前面還有一層類似 proxy 的裝置**
  - 可能負責審計、過濾、權限控管、流量治理或協定轉換
  - 這一層通常會偏好標準、簡單、容易解析的協定與 payload

### 對工程實作的建議

- → **先用最保守、最相容的方式接通**：SSE + 簡單 message 格式
- → **先驗證企業環境能不能穩定透傳**，再逐步增加 tool use、memory、複雜 context 結構
- → **若遇到「模型明明支援，但公司環境不能用」的情況，先檢查中間層，不要急著怪模型**

- ★ **企業導入 LLM，真正要整合的常常不是模型，而是模型前面的企業基礎設施**

> 📝 **筆記**：這頁很適合提醒同事——在公司環境做 AI，不是照官方文件串起來就好，還要先理解中間那層企業治理設備。

---

## 第 16 頁｜半年成果 + 下半年方向

**副標**：成果要量化、方向要具體、建議要可行動

### 半年關鍵成果（填入真實數字）

- ▸ **11 個核心技術主題系統性探索完成**
- ▸ **60%+ 重複性任務自動化比例（需確認實際數字）**
- ▸ **PR 產出效率提升 3x（需確認實際數字）**
- ▸ **20+ 個 Team Skill 資產已建立**

- 具體的 Before / After（填入真實案例）
  - Before：一個 feature PR 需要 X 天
  - After：使用 SDD + Agent，縮短到 Y 天

  - Before：新人 onboarding 需要 A 週才能獨立產出
  - After：Skill 庫輔助，B 週

- ★ **建議：找 1–2 個最有說服力的具體案例來講故事**
  - 數字是骨架，故事是血肉

### 下半年四個重點方向

- 1. AST + Knowledge Graph 導入評估
  - → Q3 評估工具，Q4 POC 驗證

- 2. CI/CD Pipeline AI 整合
  - → SonarQube 結果讓 AI 自動修復
  - → 把安全問題從 post-PR 移到 pre-commit

- 3. Skill 庫開放給其他團隊
  - → 制定貢獻指南，降低門檻
  - → 考慮往 GitAgent 標準靠攏

- 4. 更多 MCP 整合
  - → Jira、SonarQube、Azure DevOps 深度整合

- ? 哪一個方向對全公司最有感？
- → 分享後做問卷收集回饋

> 📝 **筆記**：結語建議：用 Karpathy 的話首尾呼應，讓聽眾帶著緊迫感和行動意願離開

---

## 第 17 頁｜給全公司的三個具體建議

**副標**：不需要懂技術，從今天就可以開始

### 建議 1：先用 Chat 試水溫，確認任務是否真的適合自動化

- Chat 是最低成本的 task decomposition 測試方式
- 如果連在對話層都很難把目標、輸入輸出、限制條件、例外情況講清楚，代表這件事還不適合直接做成 agent 或 service
- 先在 Chat 階段把任務邊界整理順，再決定要不要往 workflow automation 或 agent 化推進
- ★ **先驗證任務結構，再投入工程成本，成功率會高很多**

### 建議 2：從自己最熟悉的 Agent 入口開始，但累積的是可重用的資產

- 如果現在最習慣的是 IDE 介面的 agent，就先從那裡開始，不需要一開始就追所有新工具
- 真正應該沉澱的不是工具操作本身，而是 Skill、MCP 連接方式、規則、review 準則與工作習慣
- 未來當 agent 分散到 IDE、CLI、Browser、pipeline 甚至 service 端時，這些資產仍然可以跨入口重用
- ★ **工具是入口，Skill / MCP / rules 才是可遷移的核心能力**

### 建議 3：把個人經驗轉成團隊共享的 AI 資產

- AI 發展速度太快，單打獨鬥很容易重複踩坑；而且每個人接觸的場景都不一樣
- 有人懂開發，有人懂流程，有人懂領域知識；把這些經驗沉澱成共用資產，團隊的學習速度會遠高於個人各自摸索
- 分享的不只是 prompt，也包含 Skill、規範、踩坑紀錄、成功案例與可追溯決策
- ★ **AI 導入的複利來自資產共享，不來自個人偶發的高光表現**

> 📝 **筆記**：結語重點：行動 > 完美。今天開始用一個 Skill，比等到完全理解再開始更有價值

---

## 第 18 頁｜高手實戰：把 Coding Agent 用到極限的技巧

**副標**：不是只會下 prompt，而是把 agent 當成一支可編排、可隔離、可回滾的數位工程團隊

### 高手常用的 6 個技巧

- 1. **把大任務拆成 subagent，而不是讓一個 agent 硬做到底**
  - 主 agent 負責規劃、分派、整合
  - subagent 各自負責獨立子問題：測試修復、重構、文件更新、風險檢查
  - 好處：context 不會互相污染，失敗範圍也更小

- 2. **善用 Git Worktree，讓多個 agent 並行工作**
  - 同一個 repo 開多個 worktree，各自有獨立 branch 與工作目錄
  - 一個 agent 寫 feature，一個 agent 跑 migration，一個 agent 專門處理 test fix
  - 最後由人或主 agent 做 diff 比較與整合
  - ★ **這本質上是把「單執行緒 AI」升級成「可協作 AI 團隊」**

- 3. **要求 agent 先產出 plan / spec，再開始改 code**
  - 先讓它寫：問題理解、影響範圍、修改步驟、驗證方式
  - plan 經過你 review 後再進入實作
  - 這會大幅降低 agent 因誤解需求而大改一堆檔案的風險

- 4. **養成 checkpoint commit 習慣，讓 agent 可以安全探索**
  - 每完成一個可驗證的小步驟就 commit 一次
  - 出現錯誤時可以快速回退到上一個穩定點
  - 對長任務來說，checkpoint 比「一次做完」可靠太多

- 5. **把 reviewer agent 跟 builder agent 分開**
  - builder agent 專注產出
  - reviewer agent 專門找 bug、看 security、檢查邊界條件、比對 spec
  - 不同 agent 用不同角色與不同 context，通常比同一個 agent 自我反省更有效

- 6. **把 context 當成稀缺資源來管理**
  - 只給 agent 完成當前子任務所需的檔案、規範與 log
  - 長文件先摘要，歷史對話先壓縮，避免整包丟進去
  - 真正的高手不是給 agent 最多資訊，而是給它「剛好夠用」的資訊

### 一個更進階的心法

- 初學者：把 agent 當聊天機器人
- 進階者：把 agent 當 junior engineer
- 高手：把 agent 當 **可以切分、隔離、審核、回滾、並行化的工程系統**

- → 最強組合：**Subagent + Worktree + Spec + Checkpoint Commit + Reviewer Agent**
- ★ **當你開始設計 agent 的工作系統，而不是只寫 prompt，你就進入高手區了**

> 📝 **筆記**：這頁很適合給工程同事一個「馬上能升級」的方向：先從 worktree + checkpoint commit 開始，成熟後再往 subagent orchestration 走。

---

## 第 19 頁｜新觀點｜Agent Engineering：一個新的工程紀律

**副標**：來源：LangChain Blog（Dec 2025）— 跟我們在做的事完全呼應

### 什麼是 Agent Engineering？

- LangChain 的定義：
  - 把非確定性 LLM 系統，迭代精煉成可靠生產體驗的過程

- 核心循環：Build → Test → Ship → Observe → Refine → Repeat

- 最重要的觀點轉換：
  - "Shipping 不是終點，是你持續前進、獲取洞見的方式"
  - 停止「先做完美再上線」的思維
  - 改成「上線是學習的開始，不是學習的結束」

- 為什麼這個觀點重要？
  - 傳統軟體：inputs 已知，outputs 可定義
  - Agent：inputs 無限，behavior 非確定性
  - → 你無法在上線前「測試完所有情況」
  - → 生產環境才是你真正的老師

- ★ **我們的 SDD 流程，就是在落實這個循環**
  - Spec = 定義「測試什麼算通過」
  - 每次 merge 後 → 觀察 → 更新 Skill → 下次更好

### Agent Engineering 需要哪些技能？

- LangChain 認為是三個技能的交叉：

- 1. Product Thinking（產品思維）
  - 寫 prompt，定義 agent 的行為範圍
  - 深入理解「agent 要替代的工作是什麼」
  - 定義 evaluation：什麼叫做「做好了」

- 2. Engineering（工程能力）
  - 寫工具讓 agent 能呼叫
  - 建 UI/UX 支援 streaming、human-in-the-loop
  - 打造能處理持久執行、記憶管理的 runtime

- 3. Data Science（數據能力）
  - 建立評估系統：evals、A/B testing、monitoring
  - 分析使用模式和錯誤
  - 量化「agent 有沒有在進步」

- ★ **這不是一個人的工作，是跨角色的協作**
  - PM 寫 prompt、工程師寫工具、資料科學家做評估
- → 對我們的意義：Agent Engineering = SDD + Skill + Observability

> 📝 **筆記**：Agent Engineering 是 LangChain 提出的框架，但概念跟我們在做的完全吻合——可以用這個詞來定位我們的工作

---

## 第 20 頁｜新觀點｜Context Engineering：Prompt Engineering 的進化

**副標**：來源：LangChain Blog（2025）— 直接解釋了我們的 Skill 體系為什麼有效

### 什麼是 Context Engineering？

- LangChain 的定義：
  - "建立動態系統，在正確時機把正確資訊
  - 以正確格式傳給 LLM 的藝術與科學"

- 為什麼從 Prompt Engineering 進化到 Context Engineering？
  - 早期：把 prompt 寫得夠聰明就夠了
  - 現在：agent 需要的資訊來源複雜得多
  - → 開發者設定、用戶輸入、歷史對話
  - → 工具呼叫結果、外部 DB、即時資料

- Cognition（Devin 的創辦公司）說的：
- *Context engineering... is effectively the #1 job
    of engineers building AI agents.*

- ★ **LLM 不是讀心術——你不給它正確的 context，它就猜**
  - 大多數 agent 失敗的原因：不是模型不夠強
  - 而是沒有給模型「做決定所需的 context」
- → 我們的 Skill 體系，本質上就是 Context Engineering

### 四個 Context Engineering 策略

- 1. Write（寫入外部記憶）
  - 把重要資訊存到 context window 之外
  - 例：agent scratchpad、file system 筆記
  - 我們的對應做法：Git commit log 記錄 AI 決策

- 2. Select（按需取回）
  - 需要時才把資訊拉進 context
  - 例：RAG、Skill 按需讀入
  - 我們的對應做法：Skill 按任務按需載入，不全塞

- 3. Compress（壓縮冗余）
  - 只保留完成任務所需的 token
  - 例：對話摘要、Skill 提煉精華
  - 實測：對話摘要從 115k token 壓到 60k token
  - 我們的對應做法：Skill = 8000 token 規範壓縮到 800 token

- 4. Isolate（隔離子任務）
  - 把大任務拆給多個 agent，各自有獨立 context
  - 例：git worktree 讓 agent 並行、互不干擾
  - 我們的對應做法：Git Worktree 並行任務

- ★ **這四個策略，我們都已在實踐——只是沒有用這套語言來描述**

> 📝 **筆記**：「Context Engineering」是比「Prompt Engineering」更準確的詞——可以考慮在簡報中用這個新詞重新定位我們的 Skill 工作

---

## 第 21 頁｜新觀點｜LangChain 調查數據 + 真實 Agent 案例

**副標**：來源：State of AI Agents 2026（1,300+ 人）+ LangChain GTM Agent（Mar 2026）

### State of AI Agents 2026：最新調查數字

- ▸ **57% 的組織已有 agent 在生產環境（去年 51%）**
- ▸ **32% 說「品質」是進入生產的最大障礙**
- ▸ **89% 已有 observability（追蹤 agent 行為）**
- ▸ **只有 52% 在做 evaluation（系統性評估）**

- 這個落差很重要
  - 89% 能「看到」agent 在做什麼
  - 但只有 52% 有系統性地「判斷」好不好
  - → 大多數人知道問題在哪，但沒有量化標準

- ? 我們自己有做 evaluation 嗎？
  - 有沒有定義：什麼叫做 agent 這次「做好了」？
  - 有沒有 regression testing：上次好，這次還好嗎？

- ★ **這是我們下半年值得補強的一塊**
  - SDD 的 Spec 其實就是 evaluation 的基礎
- → 每個 Spec 的測試案例 = 可自動化的 eval 資料集

### GTM Agent 真實案例：LangChain 自己做的

- 背景：LangChain 把 sales outbound 流程 agent 化
  - 每個 rep 要在 Salesforce、Gong、LinkedIn 間切換
  - 每封郵件要 15 分鐘研究，才能寫第一個字

- 他們怎麼做的？
  - Agent 接到新 lead → 先查「要不要聯絡」
  - 研究帳戶歷史 → 寫個人化草稿
  - 草稿 + 推理過程 → 用 Slack DM 給 rep 審核
  - Rep 按「送出 / 編輯 / 取消」— 沒有人工審核就不發
  - Rep 每次編輯 → agent 自動學習這個人的風格

- ▸ **結果：lead 轉換率 +250%（3 個月內）**
- ▸ **每個 rep 每月省回 40 小時**
- ▸ **86% 每週活躍使用率**

- 最值得我們借鑑的設計
  - → Human-in-the-loop：草稿必須人工審核才執行
  - → Skill 定義 playbook：agent 遵循「外發郵件規範 skill」
  - → 記憶學習循環：每次編輯 = 一次訓練資料
- ★ **這個案例完美展示了 SDD + Skill + Memory 的組合威力**

> 📝 **筆記**：這三個新觀點可以讓你的簡報更有業界背書：用 LangChain 的語言重新詮釋我們在做的事

---

## 第 22 頁｜新觀點｜Agent = Model + Harness（LangChain，2026 年 3 月）

**副標**：最新發布的框架：解釋了為什麼相同模型在不同團隊手中效果差那麼多

### Harness 是什麼？

- 核心等式：Agent = Model + Harness

- 「不是 Model 的，全部都是 Harness」
  - System prompt、工具定義、執行邏輯
  - Middleware、狀態管理、回饋循環
  - Memory 策略、context 壓縮方式
  - → 換句話說：我們的 SDD、Skill、RULES = Harness

- Model 提供智能，Harness 讓智能有用
  - 比喻：馬（Model）提供力量
  - 馬具（Harness）把力量轉換成可控的牽引力

- ▸ **同一個模型（Opus 4.6）在不同 harness 下：**
  - Claude Code 原本 harness → Terminal Bench 2.0 得分較低
  - 優化過的 third-party harness → 得分高出一截
- ▸ **LangChain 只改 harness，不換模型：52.8 → 66.5 分（+13.7）**
- ★ **Harness 的品質，決定了 AI 能力的上限，不是模型本身**

### Harness Engineering 的三個層次

- LangChain 的分類（從低到高）

  - Framework（LangChain）
  - = 提供積木和抽象，讓你組裝
  - 適合：需要高度客製的場景

  - Runtime（LangGraph）
  - = 管理 agent 的狀態機和執行流程
  - 適合：複雜的 multi-agent 協作

  - Harness（DeepAgents / Claude Code）
  - = 開箱即用的完整環境，有預設 prompt、工具、記憶
  - 適合：直接拿來跑任務，按需客製

- 我們現在用的是哪一層？
  - Cline / Claude Code = Harness 層
  - 我們的 Skill + SDD = 在 Harness 上客製的 overlay
- ★ **我們不只是「在用工具」，我們在做 Harness Engineering**
- → 可以用這個詞對外解釋我們在做什麼，比「AI 導入」更精準

> 📝 **筆記**：Harness 概念讓我們可以更清楚地說：換模型不一定有幫助，優化 harness 才是關鍵

---

## 第 23 頁｜新觀點｜Coding Agent 正在顛覆 EPD 分工（LangChain，2026 年 3 月）

**副標**：來源：「How Coding Agents Are Reshaping Engineering, Product and Design」——這篇給非工程受眾衝擊最大

### 傳統 EPD 流程的崩解

- 傳統流程（Pre-Agent 時代）
  - PM 寫 PRD → Designer 出稿 → 工程師實作
  - 每一步都是瓶頸，等待時間佔了大半

- Coding Agent 改變了什麼？
  - 程式碼的生成成本趨近於零
  - 任何人都可以讓 agent 快速產出一個 prototype
  - 不再需要「先寫完 spec 才看到東西」

- *PRDs are dead."  — Harrison Chase, LangChain CEO*
  - 不是說規格不重要，而是
  - 「先寫文件才能開始動工」的順序已經死了
  - 現在的流程：有想法 → agent 跑出 prototype → 再討論

- ★ **瓶頸從「實作」移到了「Review」**
  - 現在最稀缺的：能判斷 prototype 好不好的人
  - 而不是能把 spec 轉換成 code 的人

### 誰在 Agent 時代更有價值？

- Generalist 的崛起
  - 能同時做 Product + Engineering + Design 的人
  - 以前：溝通成本讓 generalist 的優勢有限
  - 現在：只需要跟 agent 溝通，不需要跨部門協調
  - → 一個好 generalist 的產出 = 過去一個小團隊

- PM 的新角色
  - 以前：寫 PRD，等工程師還原你的想法
  - 現在：直接用 agent 驗證想法，建 prototype
  - PRD 的意義從「施工藍圖」變成「驗收標準」
  - → 這跟 SDD 的 Spec 完全一樣！

- 工程師的新角色
  - 以前：把 spec 轉成 code
  - 現在：確保 agent 的 code 是 well-architected 的
  - Review 能力 > 實作速度

- ★ **我們的 SDD 流程跟 LangChain 的觀察完全吻合**
  - Spec 先行（驗收標準）+ Agent 實作 + 人工 Review
- → 給全公司的訊息：AI 不只是工程師的工具
  - PM 可以跑 prototype，不需要等工程師
  - 你的領域知識 × Agent 執行力 = 真正的槓桿

> 📝 **筆記**：這頁給非工程受眾衝擊最大，強烈建議放在全公司分享的 deck 裡

---

## 第 24 頁｜新觀點總結｜LangChain 的語言，重新詮釋我們在做的事

**副標**：用業界共識的詞彙，幫我們的工作定位——讓聽眾知道我們不是在發明輪子，是在走對的路

### 我們做的事 → 業界的說法

- 我們說：「把 Skill 放進 Git repo」
- 業界說：「Context Engineering 的 Select 策略」

- 我們說：「SDD 先寫規格再讓 AI 實作」
- 業界說：「Agent Engineering 的 Product Thinking 層」

- 我們說：「用 Cline + Skill 跑任務」
- 業界說：「在 Agent Harness 上做 Context Engineering」

- 我們說：「Git Worktree 並行任務」
- 業界說：「Context Isolation 策略」

- 我們說：「PR = Agent 的工作報告」
- 業界說：「Agent Observability 的 Trace 機制」

- ★ **我們沒有在發明輪子**
  - 我們獨立推導出來的方法，跟業界最頂尖的實踐完全一致
  - 差別只是：我們可以用更清楚的詞彙來溝通它

### 我們還缺什麼？（對照業界）

- 業界強調，我們目前還沒有的

- 1. Observability / Tracing
  - 業界：89% 有 production agent 的組織都有
  - 我們：目前沒有系統性的 agent trace
  - → 下半年最值得補的基礎建設

- 2. Systematic Evaluation（Eval）
  - 業界：SDD 的 Spec + 測試案例 = eval dataset 的起點
  - 我們：Spec 有了，但沒有自動化 eval pipeline
  - → 可以從 SDD 測試案例開始，逐步自動化

- 3. 正式的 Harness 設計文件
  - 業界：把 harness 元件顯性化（system prompt、工具、flow）
  - 我們：大多是隱性的，沒有文件化
  - → 可以用 GitAgent 的格式（agent.yaml）來整理

- → 不是說這些明天就要做，而是讓大家知道「下一步在哪裡」
- ★ **半年的探索，讓我們有了扎實的基礎**
  - 接下來：把基礎轉化成可重現、可量化、可擴展的系統

> 📝 **筆記**：這頁建議放在簡報的最後，作為「我們已經走到哪、下一步往哪走」的總結

---

## 第 25 頁｜A2A Protocol (1/2)：Agent 之間溝通的開放標準

**副標**：Google 於 2025 年 4 月發布，現已移交 Linux Foundation 治理——長官最關心的背景

### A2A 是什麼？為什麼重要？

- 核心問題：各家 AI Agent 各說各話，無法互相協作
  - 你公司的 Jira Agent（Atlassian）
  - 你的 Salesforce Agent（Salesforce）
  - 你的 Azure DevOps Agent（Microsoft）
  - → 三個 agent，三種格式，需要大量客製整合

- A2A 的解法：讓 agent 有共同語言
  - 定義 agent 如何自我介紹（Agent Card）
  - 定義 agent 如何委派任務（Task 生命週期）
  - 定義 agent 如何傳遞結果（Artifact）
  - → 就像 HTTP 讓所有網站都能互通，
  - A2A 讓所有 agent 都能互通

- ▸ **2025 年 4 月 Google 發布，150+ 企業夥伴支持**
- ▸ **2025 年 6 月移交 Linux Foundation 開放治理**
- ▸ **Microsoft、AWS、IBM 均已加入 A2A 工作組**
- ▸ **支持方包括：Atlassian、SAP、Salesforce、ServiceNow**
  - 以及 Deloitte、Accenture、McKinsey、PwC 等顧問巨頭

- ★ **這不是 Google 一家在做，是業界共同在推的標準**

### A2A 的三個核心概念

- 1. Agent Card（自我介紹名片）
  - 每個 agent 發布一個 JSON 檔案說明自己
  - 包含：能做什麼、怎麼聯絡、需要什麼授權
  - 其他 agent 讀了 Agent Card，就知道能不能把任務交給它
  - → 就像 API 的 Swagger 文件，但是給 agent 用的

- 2. Task 生命週期
  - submitted → working → input-required → completed
  - 支援長時間執行（不是一問一答，是非同步協作）
  - 任務可以跨越多個 agent、多個步驟、多個系統

- 3. MCP + A2A 分層架構
  - MCP = agent 跟工具/服務溝通（agent to tool）
  - A2A = agent 跟 agent 溝通（agent to agent）
  - 兩者互補，不競爭
  - → MCP 讓 agent 能使用外部資源
  - → A2A 讓多個 agent 能協作完成複雜任務

- ★ **類比：MCP 是每個人的「工具箱」，A2A 是「開會室」**
  - 工具箱讓你能做事，開會室讓你們能協作

> 📝 **筆記**：A2A = 讓不同廠商的 AI Agent 能互相溝通的開放標準，解決企業多系統整合的核心痛點

---

## 第 26 頁｜A2A Protocol (2/2)：企業場景、現實挑戰、我們的策略

**副標**：真實的採用現況 + 對我們公司的意義——不只看美好願景，也看真實困難

### 企業場景想像（長官最感興趣的部分）

- 場景一：招募流程全自動化（Google 示範案例）
  - Client Agent 收到需求：「找符合條件的後端工程師」
  - → 委派 Sourcing Agent：LinkedIn 搜尋候選人
  - → 委派 Scheduling Agent：安排面試時間
  - → 委派 Background Check Agent：背景查核
  - 整個流程 agent 之間自動協作，不需人工接力

- 場景二：供應鏈協作（Tyson Foods + Gordon Food Service）
  - 供應商 agent ←→ 採購 agent，跨公司邊界共享產品資料
  - 庫存 agent 發現不足 → 自動通知訂購 agent → 通知物流 agent

- 場景三：對我們公司的想像
  - Azure DevOps Agent（工作項目）
  - ↕  A2A  ↕
  - Coding Agent（實作程式碼）
  - ↕  A2A  ↕
  - SonarQube Agent（安全掃描）
  - ↕  A2A  ↕
  - Jira Agent（更新票據狀態）
  - → 整個 DevOps 流程 agent 自動接力，人只需審核

- ▸ **Gartner：2026 年 40% 企業應用將有任務型 AI Agent**
  - 目前不到 5%——這個缺口正是 A2A 要填補的

### 誠實的現況評估與我們的策略

- A2A 目前的真實狀況（不只看美好願景）
  - 2025 年 9 月：開發速度明顯放緩
  - MCP 因為開發者體驗更好，搶走了大部分社群動能
  - Production-ready 版本原定 2025 年底，但已延遲
  - 大多數企業仍在觀望，尚未有大規模落地

- ? 為什麼 MCP 比 A2A 更快被採用？
  - MCP：從第一天就能跟 Claude 用，開發者馬上有感
  - A2A：需要先建 multi-agent 基礎設施，門檻較高
  - → 先行者優勢：MCP 從 2024 年底就跑在前面

- 但 A2A 的方向是對的，只是時間問題
  - Google、Microsoft、AWS、IBM 全部都在
  - Linux Foundation 治理 = 不會被單一廠商主導
  - 2026 年 IBM 預測：multi-agent 系統開始進入生產環境

- 我們的策略建議
- → 現在：繼續深化 MCP（工具整合），觀察 A2A 進展
- → 下半年：評估內部 multi-agent 場景（DevOps 自動接力）
- → 2027：若 A2A 社群成熟，考慮導入跨系統 agent 協作
- ★ **核心原則：不追協議本身，追我們要解決的業務問題**
  - A2A 成熟了，就用 A2A；MCP 能解決的，就先用 MCP

> 📝 **筆記**：給長官的一句話：A2A 是正確方向，但現在還在早期——我們應該持續關注，同時先把 MCP 和 Agent Harness 做好作為基礎

---

## 第 27 頁｜延伸補充：Agent Memory 的踩坑經驗與解法

**副標**：我們實際碰到的問題，以及目前的應對方式

### 三個踩過的坑

- 踩坑 1：把所有規範全塞進 system prompt
  - → token 爆，而且 AI 會忽略後段內容
  - → 改成：按需載入相關 Skill

- 踩坑 2：Vector DB 搜尋到不相關的片段
  - → 導致 AI 給出不適合當前任務的建議
  - → 改成：結構化 Skill 比模糊相似度查詢更可靠

- 踩坑 3：Agent 的「記憶」存在本地，團隊看不到
  - → 個人知識無法複用
  - → 改成：所有有用的 Skill 進 Git，全員共用

### 未解決的問題與下一步

- ? 如何讓 Agent 主動沉澱新知識到 Skill？
  - → 目前還是靠人工整理
  - → 理想：agent 自動生成 Skill 草稿，人工審核

- ? 不同情境需要不同的記憶深度，如何動態調配？
  - → 快速任務：只用 in-context
  - → 複雜任務：in-context + skill + external store

- → 下半年方向
  - 嘗試 agent 自動生成 Skill 草稿，人工審核後 merge
  - 評估 External Memory Store 的導入成本

- ★ **核心原則：記憶體系要讓人看得到、改得了、版控得了**
  - 不能是黑盒子，否則出問題沒辦法 debug

> 📝 **筆記**：Claude Code 的 memory feature、Windsurf 的 Cascade——都在搶這塊，我們用 Skill 提前解決了部分

---

## 第 28 頁｜延伸補充：RAG + Knowledge Graph 讓 AI 讀懂程式碼

**副標**：傳統 RAG 解決文字問題，Knowledge Graph 解決邏輯問題

### 傳統 RAG 的現況與限制

- 目前已解決的問題
  - API 文件快速問答：不需要每次翻文件
  - 需求文件檢索：找出相關的歷史規格
  - 錯誤訊息查詢：找出類似問題的解決方案

- RAG 的本質限制（很多人不知道）
  - 只懂「文字相似度」，不懂「程式邏輯」
  - 無法理解：A 函數呼叫了 B，B 又呼叫了 C
  - 改了 B，不知道 A 和 C 都會受影響

- ? 痛點：當 AI 幫你重構，它怎麼知道哪些地方會壞？
- ★ **答案：傳統 RAG 根本做不到這件事，需要 AST**

### AST + Knowledge Graph 展望

- AST = Abstract Syntax Tree（抽象語法樹）
  - 把程式碼解析成有結構的節點關係
  - 不是把程式碼當文字，而是當「邏輯圖」

- Knowledge Graph 能回答的問題
  - 「誰呼叫了這個函數？」
  - 「如果我改這裡，哪些測試會失敗？」
  - 「這個 API 有幾條路徑使用它？」

- 下半年評估計畫
  - Q3：評估 tree-sitter / Neo4j，選一個服務 POC
  - Q4：讓 Cline 能查詢 Knowledge Graph

- ★ **傳統 RAG 懂「文字」，Knowledge Graph 懂「邏輯」**
- → 先從一個語言、一個服務開始，不要一次全上

> 📝 **筆記**：AST + KG 是我們的下半年重點投資，這張說明「為什麼 RAG 不夠用」的深層原因

---

## 第 29 頁｜延伸補充：Git 在 AI 開發中的全新角色 (1/2)

**副標**：AI 時代的 Git 用法跟傳統完全相反——不是記錄完成，而是保護起點

### Git 作為 AI 的安全網

- 傳統用法：寫完才 commit，記錄完成的工作
- AI 時代用法：執行前先 commit，記錄「起點快照」

- 為什麼這樣做？
  - AI agent 可能做出預料外的改動
  - 有 commit 快照，一個指令完全還原
  - 讓 AI 大膽嘗試，不用怕搞壞東西
  - → 嘗試成本趨近於零

- 具體流程
  - $ git commit -m 'snapshot: before agent task'
  - （啟動 agent，讓它跑）
  - 結果不好 → $ git reset --hard HEAD（完全復原）
  - 結果好   → $ git commit -m 'agent: add auth'

- ★ **這個習慣改變了 AI 開發的心理安全感**
  - 不怕 AI 搞壞 → 放心給更大的任務 → 產出更多
- → 建議：把這個 pattern 寫進 team Skill 標準化

### Git 作為 AI 決策的日誌

- Commit message 的新意義
  - 過去：記錄人做了什麼改動
  - 現在：記錄 AI 決定了什麼、為什麼這樣做

- 建議的 AI 任務 commit 格式
  - agent(auth): implement JWT refresh token
  - Spec: SPEC-042
  - Approach: sliding window 避免 race condition
  - Tested: 現有測試全過，新增 3 個 edge case

- PR = Agent 的工作成果報告
  - Description：任務目標 + AI 的推理過程
  - 把不確定的決策標出來，讓 reviewer 聚焦
  - 比傳統 PR 更容易審查，因為思路是明確的

- ★ **可追溯性是 agentic 開發的核心**
  - 不只是工程問題，也是合規問題
  - 誰叫 AI 做了什麼、AI 怎麼想的，全部有記錄

> 📝 **筆記**：Git 不只是版控，在 AI 時代它是：安全網（讓 AI 大膽試）+ 決策日誌（讓人類能審計）

---

## 第 30 頁｜延伸補充：Git 在 AI 開發中的全新角色 (2/2)

**副標**：這是 AI 寫作時代最重要但最少人知道的 Git 技巧——本質是讓 AI 像一支團隊一樣工作

### Git Worktree 是什麼？為什麼這麼重要？

- 先理解問題：傳統開發的並行限制
  - 一個 Git repo = 一個工作目錄
  - 叫 Agent A 開發 auth 功能，它開始改檔案
  - 這時想叫 Agent B 同時修 bug → 兩個 agent 互相覆蓋
  - → 並行 = 災難，所以只能一個一個跑，效率極低

- Worktree 的解法：一個 repo，多個工作目錄
  - $ git worktree add ../task-auth   feature/auth
  - $ git worktree add ../task-bugfix feature/bugfix
  - $ git worktree add ../task-tests  feature/test-coverage

- 結果：三個獨立目錄，共用同一個 .git
  - my-project/    ← 你的主目錄（main branch）
  - ../task-auth/  ← Agent A 在這裡跑，完全獨立
  - ../task-bugfix/ ← Agent B 在這裡跑，互不干擾

- 你的工作方式徹底改變
  - 啟動 3 個 agent → 去喝咖啡 → 回來審查 3 個 PR
  - 不是「等 AI 做完再做下一個」
  - 而是「同時讓多個 AI 工作，你只負責最終審核」

- ★ **這不是技巧，是 agentic 開發的基礎建設需求**
  - 就像 CI/CD 的 parallel jobs——沒有它你就是在浪費時間

### 為什麼 AI 寫作時代讓 Worktree 變得不可或缺

- 人類開發時代：並行不常見
  - 一個人一次只能專注一件事
  - 切換任務有認知成本，所以串行比較好
  - Worktree 存在已久，但大多數人用不到

- AI agent 時代：並行是默認狀態
  - AI 沒有認知切換成本
  - 一個工程師可以同時監督 5-10 個 agent
  - 瓶頸從「寫程式的速度」變成「審查的速度」
  - Worktree 讓你一次給出多個任務，批量審查

- 業界的具體做法
  - Claude Code：每個新任務建議在新 worktree 跑
  - Conductor、Verdent 等工具：核心功能就是管理多個 worktree
  - Simon Willison（知名 AI 開發者）稱之為
  - "embracing the parallel coding agent lifestyle"

- ▸ **一個工程師 + Worktree + 多個 agent**
  - ≈ 過去一個 3-5 人小團隊的產出速度

- ★ **核心洞見：Worktree 讓工程師從「執行者」變成「管理者」**
  - 你不再寫每一行 code，你分配任務、審查結果
- → 可以把 Worktree 的標準流程寫成 team Skill
  - 讓所有人都養成這個習慣，不是只有知道的人才用

> 📝 **筆記**：Git Worktree 是 2025 年最值得推廣的開發習慣改變——它讓一個工程師的產能可以乘以 N 倍

---

## 第 31 頁｜可再深化觀點：從「效率提升」走向「決策品質提升」

**副標**：多數 AI 簡報只講速度，但高階主管更在意的是：決策是否更好、風險是否可控

### 建議加入的三個新問題（比效率更高一層）

- 1. 我們是否正在用 AI 提升「決策品質」，而不只是「產出速度」？
  - 速度快，但若錯誤決策變多，整體價值可能下降
  - 建議補一個 Quality KPI：
  - 「一次做對率（First-pass success rate）」而非只有「PR 產出數」

- 2. 我們是否有「停止機制」（Kill Switch）？
  - Agent 在 production 觸發異常時，能否一鍵降級為人工流程
  - 建議補一頁最小安全設計：
  - 可觀測（trace）→ 可告警（alert）→ 可中止（kill）→ 可回滾（rollback）

- 3. 我們是否量到「組織學習速度」？
  - 真正護城河不是模型能力，而是團隊把經驗轉成 Skill 的速度
  - 可新增指標：
  - 問題到 Skill 的平均轉化時間（Time-to-Skill）
  - Skill 被重用次數（Reuse Count）

- ★ **高層最關心的不是 AI 做了多少，而是公司是否變得更聰明、更穩定**

> 📝 **筆記**：這頁可以把話題從「工程效率」升級到「企業治理與競爭力」

---

## 第 32 頁｜可再新奇觀點：把 Agent 當「數位勞動力組合」來管理

**副標**：從 HR / 財務語言切入，非工程受眾會更有感

### 一個新的敘事框架（建議給全公司）

- 傳統觀點：AI 是工具（Tooling）
- 新觀點：AI 是可配置的數位勞動力（Digital Workforce）

- 對應管理語言可改成：
  - 招募（Provisioning）：新增一個 agent 能力
  - 培訓（Training）：新增 Skill、Rules、案例
  - 績效（Performance）：任務成功率、返工率、人工介入率
  - 風險（Compliance）：權限邊界、審計軌跡、責任歸屬

- 為什麼這個觀點新？
  - 它能讓 HR、法務、稽核、財務一起參與 AI 導入
  - 把 AI 從「工程專案」升級成「組織能力工程」

- 建議加一個對照表（人力管理 vs Agent 管理）
  - 人員職能矩陣 ↔ Agent Capability Matrix
  - 試用期考核 ↔ Sandbox Eval Gate
  - 績效面談 ↔ 每月 Agent Review

- ★ **當公司開始用「人才管理」而非「工具採購」思維看 AI，導入速度與治理成熟度會同時提升**

> 📝 **筆記**：這個角度很少出現在技術簡報，但對跨部門共識建立非常有效

---

## 第 33 頁｜2026/3/16 NVIDIA 新觀點：Agent 的規模化關鍵是「AI Factory + 可觀測執行」

**副標**：把黃仁勛的訊息翻成企業可落地語言：Agent 不只是模型問題，而是系統工程問題

### 可補進簡報的 4 個重點（給管理層最有感）

- 1. Agent 不是單次推理，而是長流程「token 生產線」
  - 傳統 LLM 使用像一次問答
  - Agent 是多步驟循環：規劃 → 呼叫工具 → 執行 → 反思 → 再規劃
  - 對基礎設施的要求從「峰值算力」變成「穩定吞吐 + 低延遲 + 可觀測」

- 2. AI Factory 的核心不是 GPU 數量，而是端到端吞吐（tokens/sec 到 business outcome）
  - 可以加一句管理語言：
  - 我們應該衡量「每單位成本能完成多少可驗收任務」，而不是只看模型參數
  - 對應到你這份 deck：Evaluation + Observability 要先補齊

- 3. Agent 系統的瓶頸常在「資料/工具/記憶」而不在模型本身
  - 模型再強，若工具接不上、權限不可控、記憶不可追溯，仍無法進主流程
  - 可呼應你前面的觀點：MCP（能力邊界）+ Skill（行為品質）+ Git（可審計）

- 4. 實體世界 AI（Physical AI）與數位 Agent 正在收斂
  - NVIDIA 將 simulation / digital twin 與 agent 決策鏈放到同一個敘事
  - 對企業的啟示：未來不是只有 coding agent，還會有 supply chain / manufacturing / operation agent
  - → 現在建立的 governance（rules、trace、rollback）未來都可沿用

- ★ **關鍵結論：Agent 競爭力 = 模型能力 × 系統工程能力 × 組織治理能力**

### 建議補一個「黃仁勛觀點 → 我們行動」對照表

| NVIDIA 訊息 | 對我們的落地行動 |
| --- | --- |
| Agent 是長流程推理，不是單次聊天 | 先做可重跑的 Agent workflow + checkpoint |
| AI Factory 重視端到端吞吐 | 補齊 success rate / latency / cost / human-in-loop 指標 |
| 瓶頸多在工具與資料系統 | 優先投資 MCP 整合、Skill 標準、記憶治理 |
| 數位與實體 Agent 將收斂 | 現在先把 audit / rollback 做成共通能力 |

> 📝 **筆記**：這頁的價值是讓高層理解：我們在做的不只是「導入 AI 工具」，而是提前建立下一代 AI 生產系統
