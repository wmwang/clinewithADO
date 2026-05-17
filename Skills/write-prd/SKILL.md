---
name: prd-writer
description: 撰寫產品需求文件(PRD)並生成 API 技術規格。觸發條件：用戶提到「需求文件」、「PRD」、「產品需求」、「寫需求」、「feature list」等關鍵詞。
---

# PRD Writer

產品需求文件撰寫 + API 技術規格工作流。

## 工作流程

### 階段1：需求采集

整理用戶輸入（會議記錄/需求描述）為結構化格式：

```
## 核心業務流程
- 🔴 P0 功能名稱：功能描述

## 用戶端功能
- 🟡 P1 功能名稱：功能描述

## 管理端功能
- 🟢 P2 功能名稱：功能描述
```

優先級：🔴 P0（必須）/ 🟡 P1（重要）/ 🟢 P2（優化）

詳細 prompt 模板見 [references/prompts.md](references/prompts.md)

### 階段2：Feature List

按模組組織功能表格，使用 [references/feature-list-template.md](references/feature-list-template.md)

**完整性檢查**：主動指出缺失環節（如有「加入購物車」但沒「購物車編輯」）

### 階段3：PRD 文件

使用 [references/prd-template.md](references/prd-template.md) 生成完整 PRD。

### 階段4：技術規格（針對 API）

為每個 P0/P1 功能撰寫技術規格：

```markdown
## [API-xxx] 功能名稱

**端點**: `POST /api/v1/...`
**認證**: Bearer Token
**請求格式**:
```json
{
  "field": "value"
}
```

**錯誤碼**:
| 碼 | 描述 | 處理方式 |
|---|-----|--------|
| 400 | 參數錯誤 | 返回具體欄位問題 |
| 401 | 未認證 | 導向登入 |
| ... | ... | ... |

**業務邏輯**:
- 邏輯點 1
- 邏輯點 2

**相依服務**:
- 依賴服務 A（描述）
- 依賴服務 B（描述）
```

詳細模板見 [references/api-template.md](references/api-template.md)

## 品質檢查

完成後以四角色審視，詳見 [references/quality-checklist.md](references/quality-checklist.md)：

1. **技術負責人**：實現難度、效能、安全
2. **挑剔用戶**：操作便捷性、流程合理性
3. **營運負責人**：數據分析、營銷推廣
4. **測試工程師**：異常場景、邊界問題

## 輸出檔案

- `feature_list.md` - 功能清單
- `PRD.md` - 完整需求文件
- `api_spec.md` - API 技術規格（每個 P0/P1 功能）