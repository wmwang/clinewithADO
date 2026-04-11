# Superpowers 使用說明

Superpowers 是一套 AI 進階工作流程插件，讓 AI 在寫程式前先思考、先規劃，大幅提升開發品質。

## 包含的技能

- **superpowers-workflow** — 完整開發流程整合，涵蓋：
  - Brainstorming：發散思考，探索設計方向
  - 計畫撰寫：把想法整理成具體的實作計畫
  - TDD：測試先行的開發節奏
  - Code Review：多角色互審
  - Debugging：系統化除錯方法

## 如何使用（Claude Code）

插件安裝後，直接用自然語言觸發即可，例如：
- 「幫我規劃這個功能的實作方式」
- 「用 TDD 方式開發這個 class」
- 「review 我的 PR」
- 「這個 bug 怎麼除」

## 如何使用（Cline）

在 VS Code 中開啟 Cline，技能規則已自動載入。直接對話使用即可。

## 離線安裝方式

使用 team-skill-installer 技能，或手動執行：

```bash
python3 Skills/team-skill-installer/scripts/install_superpowers.py Skills/superpowers-plugin
```
