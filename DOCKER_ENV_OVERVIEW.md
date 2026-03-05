# 🐳 雙 AI 引擎 Sandbox (Docker) 環境介紹

為了確保 AI 在這個專案發揮最大的寫 Code 效益，本專案準備了 **Cline** 與 **OpenCode** 兩套隔離的 Docker 環境。

每個 Docker Image 都是特別為了「全端開發 (Full-stack)」與「Azure DevOps (ADO) 自動化」而打造的超級環境。這保證了 AI 收到你的指令後，不論是要編譯、寫單元測試、或是發布 PR，都能直接利用預先安裝好的系統工具完成，**不需要再花費漫長的時間去猜指令或是等待下載安裝**。

---

## 📦 預載的核心工具鏈清單

這兩套 Docker 環境（`Docker/cline` 與 `Docker/opencode`）都**預設安裝了以下核心套件與語言環境**：

| 開發環境 / 套件 | 詳細內容 / 模組名稱 | 為什麼需要這個？ (AI 的使用情境) |
| :--- | :--- | :--- |
| **Node.js 生態系** | `node:22-slim`, `npm` | 核心地基。不僅用來運行 Cline 或 OpenCode 引擎本身，更讓 AI 可以直接執行 `npm run dev`、`npm test` 或是開發任何前端/全端專案。 |
| **Python 開發環境** | `python3`, `python3-pip`, `python3-venv` | 讓 AI 能直接執行 Python 腳本。`venv` 是必須的，可以解決 Debian 系統下要求建立虛擬環境才能 `pip install` 的限制。 |
| **Java 開發環境** | `default-jdk` (預設為 Java 17), `maven` | 讓 AI 具備幫你寫 Java 程式碼、執行 `mvn clean test` 編譯、或產生 JAR 檔的能力。 |
| **C/C++ 建置工具** | `build-essential`, `make` | 許多 Node 或 Python 三方套件在底層依賴 C/C++ native addon (例如 node-gyp)，沒有它，AI 在安裝依賴時常會遇到編譯失敗。 |
| **ADO / 雲基礎套件**| `azure-cli`, `az extension add --name azure-devops` | 讓 AI 可以直接在 Command Line 底下使用 `az boards` 或 `az repos` 等原生指令，讀取 Issue 或是發 Pull Request。 |
| **ADO Python SDK**| `azure-devops` (Python 模組) | 這個本機內建的 Python SDK 讓這份大補帖底下所有 `Skills/ado/*` 的 Python 自動化腳本能無縫與 ADO API 溝通。 |
| **系統必備工具** | `git`, `curl`, `jq`, `gnupg` | `git` 負責版控；`jq` 是 JSON 的瑞士刀，AI 分析大量 API 或 Log 回傳時的最愛。 |

---

## 🛠️ 兩套 Docker 引擎的差異比較

### 1. 🥇 Cline Runtime (`Docker/cline/`)
- **啟動指令**: `docker compose -f Docker/cline/docker-compose.yml run --rm cline`
- **核心主件**: `npm install -g cline`
- **環境變數注入**: 讀取 `.env` 內的 `CLINE_VERSION`, `CLINE_MODEL`, `ADO_PAT` 等。
- **最佳用途**: **架構設計、任務拆解、腳本自動化**。它擅長默默在背景幫你執行長篇大論的規劃、產出與 ADO 長篇報告。

### 2. 🥈 OpenCode Runtime (`Docker/opencode/`)
- **啟動指令**: `docker compose -f Docker/opencode/docker-compose.yml run --rm opencode`
- **核心主件**: `npm install -g oh-my-opencode`
- **環境變數注入**: 讀取 `.env` 內的 `OPENCODE_VERSION`, `OPENCODE_MODEL`, `ADO_PAT` 等。
- **最佳用途**: **快速除錯、互動式終端機寫 Code**。OpenCode 在 Terminal 中提供了很漂亮的互動介面，適合「即時且短小精悍」的互動開發。

---

## 🔐 資安與權限控管 (Security Best Practices)

這份環境除了裝齊工具外，在**安全性設計**上也絕不馬虎：

- 🛡️ **非 Root 使用者 (Non-Root User)**：容器執行階段強制降權為 `node (UID 1000)`，防止 AI 誤下災難性的系統全域刪除指令。
- 🚫 **機敏資訊不進 Image (Secret Isolation)**：嚴格透過 `docker-compose.yml` 搭配 `.env` 動態注入 ADO Token 或 OpenAI Key，絕對不會把你的密碼 Build 死在 Docker Image 裡面。
- 📥 **預設載入目前專案目錄 (Volume Mount)**：透過啟動時掛載你目前的 `$(pwd)` 到 Container 的 `/workspace` 中，AI 寫的所有 Code 與修改都會即時同步回你的筆電，只要一關掉 Docker，環境就恢復乾淨。

> **懶人包**: 當你需要把任何專案交給 AI 幫忙時，只要在這個目錄下輸入啟動指令，這台內建各種「黑科技語言與武器」的 AI 沙盒就會馬上為你服務。
