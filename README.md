# cline-ado

[Cline CLI](https://github.com/cline/cline) + Azure DevOps CLI (`az devops`) + Python SDK — packaged as a single Docker image.

| Package | Version |
|---------|---------|
| `cline` | 2.5.0 |
| `azure-cli` + `azure-devops` extension | 最新穩定版 |
| `azure-devops` (Python SDK) | 最新穩定版 |
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
  -e OPENAI_API_KEY=sk-xxx \
  -e ADO_ORG=contoso \
  -e ADO_PAT=your-pat \
  -v "$(pwd):/workspace" \
  your-org/cline-ado:latest
```

### 5. Headless 模式 (CI/CD)

```bash
docker run --rm \
  -e OPENAI_API_KEY=sk-xxx \
  -e ADO_ORG=contoso \
  -e ADO_PAT=your-pat \
  -v "$(pwd):/workspace" \
  your-org/cline-ado:latest \
  -y "create a work item for the login bug"
```

---

## 環境變數

### AI Provider（OpenAI-compatible）

| 變數 | 必填 | 說明 |
|------|------|------|
| `OPENAI_API_KEY` | ✅ | OpenAI 或 OpenAI-compatible provider 的 API key |
| `OPENAI_BASE_URL` | — | 自訂 endpoint URL（Azure OpenAI、Ollama、vLLM 等） |
| `CLINE_MODEL` | — | 覆寫預設模型（預設：`gpt-4o`） |

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

### Azure DevOps

| 變數 | 必填 | 說明 |
|------|------|------|
| `ADO_PAT` | — | Personal Access Token（設定後啟用 az devops 自動設定） |
| `ADO_ORG` | ✅ (當 `ADO_PAT` 有設時) | 組織名稱（URL 中 `dev.azure.com/` 後面的部分） |
| `ADO_PROJECT` | — | 預設專案名稱 |

### 企業網路 / Corporate Proxy

若你的網路需要透過 proxy 才能連線到 Azure DevOps 或 AI Provider：

| 變數 | 說明 |
|------|------|
| `HTTPS_PROXY` | Proxy URL，例如 `http://proxy.corp.com:8080` |
| `HTTP_PROXY` | HTTP proxy URL（通常與 `HTTPS_PROXY` 相同） |
| `NO_PROXY` | 不走 proxy 的 hostname，逗號分隔，例如 `localhost,127.0.0.1,.corp.internal` |

範例：
```bash
docker run --rm \
  -e OPENAI_API_KEY=sk-xxx \
  -e ADO_ORG=contoso \
  -e ADO_PAT=your-pat \
  -e HTTPS_PROXY=http://proxy.corp.com:8080 \
  -e NO_PROXY=localhost,127.0.0.1 \
  -v "$(pwd):/workspace" \
  your-org/cline-ado:latest \
  -y "list my work items"
```

---

## Azure CLI (`az devops`)

Image 內已預裝 `azure-cli` 及 `azure-devops` extension。
只要設定 `ADO_PAT`，entrypoint 會自動完成以下動作，**不需要手動 `az login`**：

```bash
export AZURE_DEVOPS_EXT_PAT="${ADO_PAT}"
az devops configure --defaults organization="https://dev.azure.com/${ADO_ORG}"
```

若同時設定 `ADO_PROJECT`，也會自動設為預設專案：

```bash
az devops configure --defaults organization="https://dev.azure.com/${ADO_ORG}" project="${ADO_PROJECT}"
```

容器啟動後可直接使用所有 `az devops` 指令：

```bash
az devops project list
az repos list
az pipelines list
az boards work-item show --id 1234
```

---

## 持久化設定

Cline 的設定存放在 `/home/node/.cline/data`。
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

| Image Tag | cline | Node.js |
|-----------|-------|---------|
| `latest`, `2.5.0` | 2.5.0 | 22 |
