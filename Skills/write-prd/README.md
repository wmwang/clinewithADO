# PRD Writer Skill

AI Agent 技能：撰寫產品需求文件(PRD) + 生成可互動原型。

## 功能

- 📋 從會議記錄/需求描述提取結構化需求
- 📝 生成完整的 PRD 文件（Markdown 格式）
- 🎨 整合 UI-UX-Pro-Max 設計系統
- 🖥️ 生成單檔案 HTML 可互動原型

## 安裝

```bash
clawhub install prd-writer
```

或手動複製到你的 skills 目錄：

```bash
git clone https://github.com/FinStep-AI/prd-writer-skill.git ~/clawd/skills/prd-writer
```

## 觸發條件

當用戶提到以下關鍵詞時自動觸發：
- 「需求文件」、「PRD」、「產品需求」、「寫需求」
- 「原型」、「feature list」

## 目錄結構

```
prd-writer/
├── SKILL.md                 # 技能主檔案
├── references/              # 參考文件
│   ├── prd-template.md      # PRD 模板
│   ├── feature-list-template.md
│   ├── prototype-guide.md   # 原型生成指南
│   ├── quality-checklist.md # 品質檢查清單
│   └── ...
└── scripts/                 # 可執行腳本
    └── ui-ux-pro-max/       # 設計系統搜尋引擎
        ├── search.py        # 主入口
        └── data/            # 設計數據 CSV
```

## 使用範例

```
用戶: 幫我寫一個電商小程式的 PRD

Agent: [自動觸發 prd-writer 技能]
       1. 采集需求
       2. 生成 Feature List
       3. 生成 PRD 文件
       4. 生成設計系統
       5. 生成 HTML 原型
```

## 設計系統搜尋

```bash
# 生成完整設計系統推薦
python3 scripts/ui-ux-pro-max/search.py "SaaS dashboard" --design-system -p "項目名"

# 搜尋配色方案
python3 scripts/ui-ux-pro-max/search.py "fintech" --domain color

# 搜尋字體配對
python3 scripts/ui-ux-pro-max/search.py "modern elegant" --domain typography
```

## License

MIT