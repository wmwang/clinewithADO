# cline-ado

[Cline CLI](https://github.com/cline/cline) + [Azure DevOps MCP Server](https://github.com/microsoft/azure-devops-mcp) — packaged as a single Docker image.

| Package | Version |
|---------|---------|
| `cline` | 2.5.0 |
| `@azure-devops/mcp` | 2.4.0 |
| Node.js | 22 (slim) |

---

## 快速開始 (Quick Start)

### 1. 取得 Image

**方式 A：從 Docker Hub 直接拉取（推薦）**

```bash
docker pull your-org/cline-ado:latest
```

**方式 B：從原始碼自行建構**

```bash
git clone <this-repo>
cd clinewithADO

# 建構（預設版本）
docker build -t your-org/cline-ado:latest .

# 或用 make
make build IMAGE=your-org/cline-ado

# 建構完成後推送到 Docker Hub
docker push your-org/cline-ado:latest
# 或
make push IMAGE=your-org/cline-ado
```

---

### 2. 取得 Personal Access Token (PAT)

前往 `https://dev.azure.com/<your-org>/_usersSettings/tokens`，建立一個具備以下 scope 的 PAT：

- **Code** — Read
- **Work Items** — Read & Write
- **Build** — Read

---

### 3. 準備設定檔

```bash
cp .env.example .env
# 編輯 .env，填入 API key 和 ADO 資訊
```

---

### 4. 互動模式 (Interactive TUI)

```bash
docker compose run --rm cline
# 或
docker run -it --rm \
  -e ANTHROPIC_API_KEY=sk-ant-xxx \
  -e ADO_ORG=contoso \
  -e ADO_MCP_AUTH_TOKEN=your-pat \
  -v "$(pwd):/workspace" \
  your-org/cline-ado:latest
```

### 5. Headless 模式 (CI/CD)

```bash
docker run --rm \
  -e ANTHROPIC_API_KEY=sk-ant-xxx \
  -e ADO_ORG=contoso \
  -e ADO_MCP_AUTH_TOKEN=your-pat \
  -v "$(pwd):/workspace" \
  your-org/cline-ado:latest \
  -y "create a work item for the login bug"
```

---

## 環境變數

### AI Provider（擇一設定）

偵測優先順序如下，符合第一個條件就套用：

| 優先 | 需要設定的變數 | 適用情境 |
|------|--------------|---------|
| 1 | `CLINE_PROVIDER` + `CLINE_API_KEY` (+ `CLINE_MODEL`, `CLINE_BASE_URL`) | 完全自訂 |
| 2 | `ANTHROPIC_API_KEY` | Claude (Anthropic) |
| 3 | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | OpenAI-compatible 自訂 endpoint |
| 4 | `OPENAI_API_KEY` | 標準 OpenAI |
| 5 | `OPENROUTER_API_KEY` | OpenRouter |

**各變數說明：**

| 變數 | 說明 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API key（預設模型：`claude-sonnet-4-5-20250929`） |
| `OPENAI_API_KEY` | OpenAI API key（預設模型：`gpt-4o`） |
| `OPENAI_BASE_URL` | 自訂 endpoint URL，設定後自動套用 OpenAI-compatible 模式 |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `CLINE_PROVIDER` | 自訂 provider 名稱（需搭配 `CLINE_API_KEY`） |
| `CLINE_API_KEY` | 自訂 provider 的 API key |
| `CLINE_MODEL` | 覆寫任何 provider 的預設模型 |
| `CLINE_BASE_URL` | 搭配 `CLINE_PROVIDER` 使用的自訂 endpoint |

#### OpenAI-compatible 範例

```bash
# Azure OpenAI
-e OPENAI_API_KEY=<azure-key>
-e OPENAI_BASE_URL=https://<resource>.openai.azure.com/openai/deployments/<deployment>
-e CLINE_MODEL=gpt-4o

# Ollama（本機，從 container 連 host）
-e OPENAI_API_KEY=ollama
-e OPENAI_BASE_URL=http://host.docker.internal:11434/v1
-e CLINE_MODEL=llama3.2

# LM Studio
-e OPENAI_API_KEY=lm-studio
-e OPENAI_BASE_URL=http://host.docker.internal:1234/v1
-e CLINE_MODEL=your-loaded-model

# vLLM / 其他 self-hosted
-e OPENAI_API_KEY=<token>
-e OPENAI_BASE_URL=http://your-server:8000/v1
-e CLINE_MODEL=mistral-7b
```

### Azure DevOps MCP

| 變數 | 必填 | 說明 |
|------|------|------|
| `ADO_ORG` | ✅ | 組織名稱（URL 中 `dev.azure.com/` 後面的部分） |
| `ADO_MCP_AUTH_TOKEN` | ✅ (headless) | Personal Access Token，搭配 `--authentication envvar` |
| `ADO_TENANT_ID` | — | Azure Tenant ID（多租戶 / 訪客帳號時需要） |
| `ADO_MCP_DOMAINS` | — | 逗號分隔的 domain 篩選（見下方） |
| `ADO_MCP_DISABLED` | — | 設 `true` 可停用 ADO MCP |

**ADO_MCP_DOMAINS 可用值**（不設定則載入全部）：
`core`, `work`, `work-items`, `search`, `test-plans`, `repositories`, `wiki`, `pipelines`, `advanced-security`

範例（只載入常用的三個）：
```
ADO_MCP_DOMAINS=repositories,work-items,pipelines
```

### 企業網路 / Corporate Proxy

若你的網路需要透過 proxy 才能連線到 Azure DevOps 或 AI Provider：

| 變數 | 說明 |
|------|------|
| `HTTPS_PROXY` | Proxy URL，例如 `http://proxy.corp.com:8080` |
| `HTTP_PROXY` | HTTP proxy URL（通常與 `HTTPS_PROXY` 相同） |
| `NO_PROXY` | 不走 proxy 的 hostname，逗號分隔，例如 `localhost,127.0.0.1,.corp.internal` |
| `ADO_MCP_TLS_SKIP_VERIFY` | 設 `true` 可停用 TLS 憑證驗證（proxy 做 SSL inspection / MITM 時需要） |

> **實作說明**：`HTTPS_PROXY` 會同時作用於兩層：
> - **typed-rest-client**（WebApi 底層 HTTP）— 透過 build-time patch 注入 `IRequestOptions.proxy`
> - **Node.js http/https agent**（其他 HTTP 呼叫）— 透過 `global-agent` 在執行期 preload

範例：
```bash
docker run --rm \
  -e ANTHROPIC_API_KEY=sk-ant-xxx \
  -e ADO_ORG=contoso \
  -e ADO_MCP_AUTH_TOKEN=your-pat \
  -e HTTPS_PROXY=http://proxy.corp.com:8080 \
  -e NO_PROXY=localhost,127.0.0.1 \
  -e ADO_MCP_TLS_SKIP_VERIFY=true \
  -v "$(pwd):/workspace" \
  your-org/cline-ado:latest \
  -y "list my work items"
```

---

## 認證說明

官方 `@azure-devops/mcp` 支援三種認證模式：

| 模式 | 設定方式 | Docker 相容 |
|------|----------|-------------|
| `envvar` | `ADO_MCP_AUTH_TOKEN=<PAT>` | ✅ 推薦 |
| `azcli` | 需先執行 `az login`（掛載 `~/.azure`） | ⚠️ 需額外設定 |
| `interactive` | 自動開啟瀏覽器 | ❌ 無法在 headless Docker 使用 |

> **注意**：`AZURE_DEVOPS_PAT` 是社群套件 `@tiberriver256/mcp-server-azure-devops` 的變數，**官方套件不支援**，請使用 `ADO_MCP_AUTH_TOKEN`。

---

## 新增更多 MCP Server

未來要加其他 MCP（GitHub、Jira、Slack 等），**不需要修改 Dockerfile**，只需準備一個 JSON 設定檔並掛載：

```json
// my-mcp-settings.json
{
  "mcpServers": {
    "azure-devops": {
      "command": "mcp-server-azuredevops",
      "args": ["contoso", "--authentication", "envvar"],
      "env": { "ADO_MCP_AUTH_TOKEN": "your-pat" }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "your-token" }
    }
  }
}
```

```bash
docker run -it --rm \
  -e ANTHROPIC_API_KEY=... \
  -e MCP_SETTINGS_FILE=/mcp-settings.json \
  -v ./my-mcp-settings.json:/mcp-settings.json \
  -v "$(pwd):/workspace" \
  your-org/cline-ado
```

掛載後，`MCP_SETTINGS_FILE` 指向的檔案優先順序最高，entrypoint 會直接使用它，忽略 `ADO_ORG` 等自動生成邏輯。

---

## 持久化設定

Cline 的設定（包含 MCP auth token 快取）存放在 `/home/node/.cline/data`。
建議掛載 named volume 以保留設定：

```yaml
# docker-compose.yml 已預設加入此設定
volumes:
  - cline-data:/home/node/.cline/data
```

---

## 安全性注意事項

- **cline v2.3.0** 為被入侵的 supply-chain 攻擊版本（2026-02-17 發布），已下架。
  此 image 使用 v2.5.0（含 OIDC provenance attestation）。
- `.env` 檔案包含機密資訊，請確保已加入 `.gitignore`。
- Container 以非 root 使用者（UID 1000）執行。

---

## 版本紀錄

| Image Tag | cline | @azure-devops/mcp | Node.js |
|-----------|-------|-------------------|---------|
| `latest`, `2.5.0` | 2.5.0 | 2.4.0 | 22 |
