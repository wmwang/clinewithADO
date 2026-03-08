---
name: speckit-specify
description: 從自然語言描述建立 Feature Specification，自動建立 git 分支與目錄結構。不需安裝任何 CLI。
---

## 使用者輸入

請考慮使用者在對話中提供的 feature 描述或額外說明。若使用者有提供具體說明，以其為優先依據。

## 流程說明

feature 描述**就是**使用者說的話。除非描述為空，否則不要要求使用者重複。

### 步驟 1：產生簡短的分支名稱

從 feature 描述中，建立一個 2–4 個詞的 kebab-case 名稱：

- "新增使用者驗證" → `user-auth`
- "實作 API 的 OAuth2 整合" → `oauth2-api-integration`
- "分析儀表板" → `analytics-dashboard`
- "修正付款逾時 bug" → `fix-payment-timeout`

保留技術術語（OAuth2、JWT、API）。只使用小寫和連字號。

### 步驟 2：確定下一個功能編號

```bash
git fetch --all --prune 2>/dev/null || true
```

從三個來源搜尋符合 `<short-name>` 的最高現有編號：

```bash
# 遠端分支
git ls-remote --heads origin 2>/dev/null | grep -oE '[0-9]+-<short-name>$' | grep -oE '^[0-9]+' | sort -n | tail -1

# 本地分支
git branch 2>/dev/null | grep -oE '[0-9]+-<short-name>' | grep -oE '^[0-9]+' | sort -n | tail -1

# 現有 specs 目錄
ls specs/ 2>/dev/null | grep -E '^[0-9]+-<short-name>$' | grep -oE '^[0-9]+' | sort -n | tail -1
```

取三個來源中最高的 N，使用 N+1（若無則從 1 開始）。

### 步驟 3：建立分支與目錄

```bash
git checkout -b {N}-{SHORT_NAME}
mkdir -p specs/{N}-{SHORT_NAME}/checklists
```

確立變數：
- `BRANCH_NAME` = `{N}-{SHORT_NAME}`
- `FEATURE_DIR` = `specs/{N}-{SHORT_NAME}`
- `SPEC_FILE` = `specs/{N}-{SHORT_NAME}/spec.md`

### 步驟 4：撰寫規格文件

若描述為空：ERROR「未提供 feature 描述」

提取：角色、行為、資料、限制條件。對未知事項做出合理推測。只在選擇**明顯影響範疇、安全性或使用者體驗**，且**沒有合理預設值**時，才加入 `[待釐清：<問題>]`。**最多 3 個此類標記。**

使用以下結構寫入 `SPEC_FILE`：

```markdown
# 功能規格：{功能名稱}

**功能分支**：`{BRANCH_NAME}`
**建立日期**：{今天}
**狀態**：草稿
**輸入**：{使用者描述}

## 使用者情境與測試

### 使用者故事 1 – {簡短標題}（優先級：P1）

{以平易近人的語言描述使用者旅程}

**此優先級的原因**：{商業價值}

**獨立測試方式**：{如何單獨測試此故事}

**驗收情境**：

1. **假設** {狀態}，**當** {行為}，**則** {預期結果}
2. **假設** {狀態}，**當** {行為}，**則** {預期結果}

---

### 使用者故事 2 – {簡短標題}（優先級：P2）

{繼續同樣格式}

---

### 邊界情況

- 當 {邊界條件} 時會發生什麼？
- 系統如何處理 {錯誤情境}？

## 需求

### 功能需求

- **FR-001**：系統必須 {具體能力}
- **FR-002**：系統必須 {具體能力}

### 關鍵實體（僅在功能涉及資料時加入）

- **{實體}**：{代表什麼，關鍵屬性}

## 成功標準

- **SC-001**：{可量測、與技術無關的指標}
- **SC-002**：{可量測、與技術無關的指標}
```

**成功標準規則**：具體指標（時間/百分比/數量/比率）、不含框架/語言/資料庫、以使用者角度描述結果、不需知道實作細節即可驗證。

### 步驟 5：建立品質 Checklist

寫入 `FEATURE_DIR/checklists/requirements.md`：

```markdown
# 規格品質 Checklist：{功能名稱}

**目的**：在進入規劃前，驗證規格的完整性
**建立日期**：{今天}
**功能**：[spec.md](../spec.md)

## 內容品質

- [ ] 無實作細節（語言、框架、API）
- [ ] 聚焦於使用者價值和商業需求
- [ ] 以非技術利害關係人為撰寫對象
- [ ] 所有必要段落已完成

## 需求完整性

- [ ] 無 [待釐清] 標記殘留
- [ ] 需求可測試且無歧義
- [ ] 成功標準可量測且與技術無關
- [ ] 所有驗收情境已定義
- [ ] 邊界情況已識別
- [ ] 範圍明確界定

## 功能就緒度

- [ ] 所有功能需求都有明確的驗收標準
- [ ] 使用者情境涵蓋主要流程
- [ ] 規格中沒有洩漏實作細節

## 備註

- 標記為未完成的項目需在執行 speckit-clarify 或 speckit-plan skill 之前更新規格
```

### 步驟 6：處理 [待釐清] 標記

若有殘留（最多 3 個），以此格式呈現：

```markdown
## 問題 {N}：{主題}

**背景**：{引用相關規格段落}
**需要了解**：{具體問題}

**選項**：

| 選項 | 答案 | 影響 |
|------|------|------|
| A | {答案} | {代表什麼} |
| B | {答案} | {代表什麼} |
| C | {答案} | {代表什麼} |
```

等待回應，用選擇的答案替換標記，重新驗證 checklist。

### 步驟 7：回報結果

- 已建立分支：`{BRANCH_NAME}`
- 規格：`{SPEC_FILE}`
- Checklist：`{FEATURE_DIR}/checklists/requirements.md`
- 下一步：使用 speckit-clarify 或 speckit-plan skill
