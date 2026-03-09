---
name: speckit-constitution
description: 建立或更新專案憲法——治理所有規劃與實作的架構原則。不需安裝任何 CLI。
---
> **重要**：所有檔案讀寫操作均相對於使用者的 **project root（當前工作目錄）**，不是 skill 檔案所在路徑。如有疑慮，先執行 `pwd` 確認再操作。


## 使用者輸入

請考慮使用者在對話中提供的原則內容或憲法修訂需求。

## 流程說明

你正在建立或更新位於 `.specify/memory/constitution.md` 的專案憲法。

### 步驟 1：若不存在則初始化

```bash
ls .specify/memory/constitution.md 2>/dev/null || echo "missing"
```

若不存在，建立目錄並從此模板初始化：

```bash
mkdir -p .specify/memory
```

然後建立 `.specify/memory/constitution.md`，內容如下：

```markdown
# [PROJECT_NAME] 憲法

## 核心原則

### 一、[PRINCIPLE_1_NAME]

[PRINCIPLE_1_DESCRIPTION]

### 二、[PRINCIPLE_2_NAME]

[PRINCIPLE_2_DESCRIPTION]

### 三、[PRINCIPLE_3_NAME]

[PRINCIPLE_3_DESCRIPTION]

### 四、[PRINCIPLE_4_NAME]

[PRINCIPLE_4_DESCRIPTION]

### 五、[PRINCIPLE_5_NAME]

[PRINCIPLE_5_DESCRIPTION]

## 開發標準

[STANDARDS_CONTENT]

## 治理

[GOVERNANCE_RULES]

**版本**：[CONSTITUTION_VERSION] | **批准日期**：[RATIFICATION_DATE] | **最後修訂**：[LAST_AMENDED_DATE]
```

使用者可能指定較少或較多的原則——依其意圖調整數量。

### 步驟 2：收集所有佔位符的值

- 使用者輸入若有提供則直接使用；否則從 repo 背景推斷（README、現有程式碼模式）
- `RATIFICATION_DATE`：原始批准日期（不知道則用今天或標記 `TODO(RATIFICATION_DATE): 不明`）
- `LAST_AMENDED_DATE`：若有更動則填今天
- `CONSTITUTION_VERSION`：語意化版本規則：
  - **MAJOR**：以不相容的方式移除或重新定義原則
  - **MINOR**：新增原則或段落
  - **PATCH**：澄清、措辭調整、錯字修正

常見原則範本（依專案背景調整）：
- **函式庫優先**：每個功能先作為獨立函式庫實作
- **測試優先**（不可妥協）：TDD 強制要求——先寫測試 → 測試失敗 → 實作
- **簡潔性**：從簡單開始，YAGNI，不提前抽象化
- **可觀測性**：必須有結構化日誌，透過文字 I/O 確保可偵錯性
- **版本管理**：MAJOR.MINOR.BUILD 格式，承諾向下相容

### 步驟 3：起草更新後的憲法

- 用具體文字替換每個 `[佔位符]`——不留任何括號（除非明確延後並附說明）
- 每個原則段落必須包含：簡潔名稱、不可妥協的規則（條列或段落）、明確理由
- 治理段落必須包含：修訂程序、版本政策、合規審查頻率
- 將「應該」替換為 必須/應當（MUST/SHOULD）（規範強度明確時）

### 步驟 4：同步更新相依檔案

檢查哪些檔案存在並更新任何引用原則的內容：

```bash
ls README.md 2>/dev/null
ls docs/ 2>/dev/null
ls AGENTS.md CLAUDE.md .cursor/rules/ .github/copilot-instructions.md 2>/dev/null
```

對每個找到的檔案，更新任何對已重新命名、新增或移除的原則的引用。

若專案也使用 spec-kit 的模板檔案（`templates/plan-template.md` 等），也一併更新——但這只適用於 spec-kit repo，若不存在則靜默跳過。

### 步驟 5：同步影響報告

在憲法檔案頂端插入 HTML 註解：

```html
<!--
## 同步影響報告

**版本變更**：{舊版} → {新版}
**修改的原則**：{清單或無}
**新增段落**：{清單或無}
**移除段落**：{清單或無}
**已更新的檔案**：
- README.md：✅ 已更新 / ⚠ 待處理 / N/A
- AGENTS.md / agent context 檔案：✅ 已更新 / ⚠ 待處理 / N/A
- templates/（若為 spec-kit 專案）：✅ 已更新 / ⚠ 待處理 / N/A
**延後項目**：{清單或無}
-->
```

### 步驟 6：寫入前驗證

- 無殘留的 `[佔位符]` token（除非明確以 `TODO` 延後）
- 版本與同步影響報告一致
- 日期為 ISO 格式（YYYY-MM-DD）
- 所有原則為陳述性語句，不含模糊用語

### 步驟 7：寫入憲法

覆寫 `.specify/memory/constitution.md`。

### 步驟 8：回報結果

- 新版本與版本升級理由
- 需要人工跟進的檔案
- 建議的 commit 訊息（例如：`docs: 更新憲法至 vX.Y.Z`）
