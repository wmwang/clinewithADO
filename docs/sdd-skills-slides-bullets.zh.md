# 三套 SDD Skill 簡報條列文案

> 用途：可直接複製到 PowerPoint / Google Slides。  
> 建議頁數：5 頁。  
> 搭配講稿：[sdd-skills-presentation.zh.md](./sdd-skills-presentation.zh.md)

---

## Slide 1

### Title

三套 SDD Skill：BMAD、OpenSpec、Spec-Kit，我們該怎麼選？

### Bullets

- 三套都支援 spec-driven / spec-first 開發
- 但它們解決的問題層級不同
- 比較重點不是誰比較強
- 比較重點是：
  - 適合什麼場景
  - 文件與流程差在哪裡
  - 導入成本與團隊收益是什麼

---

## Slide 2

### Title

BMAD / OpenSpec / Spec-Kit 一頁對照

### Bullets

- BMAD
  - 最像：AI 產品研發團隊作業系統
  - 核心單位：Agent / Workflow / Story
  - 最強的完整性：跨角色協作流程完整

- OpenSpec
  - 最像：有狀態的正式變更單
  - 核心單位：Change
  - 最強的完整性：Change lifecycle 完整

- Spec-Kit
  - 最像：工程團隊可直接開工的功能實作包
  - 核心單位：Feature branch
  - 最強的完整性：Feature planning package 完整

---

## Slide 3

### Title

最容易搞混的一組：OpenSpec vs Spec-Kit

### Bullets

- OpenSpec 重點流程
  - `proposal -> specs -> design -> tasks -> verify -> sync -> archive`
  - 適合高風險 change、跨團隊 change、需要 audit trail
  - 更像正式變更單系統

- Spec-Kit 重點流程
  - `spec -> clarify -> plan -> tasks -> analyze -> implement`
  - 適合既有產品上的單一功能、MVP、日常迭代
  - 更像工程實作包

- 一句話記憶
  - OpenSpec：在管理這次變更
  - Spec-Kit：在準備這個功能怎麼做

---

## Slide 4

### Title

團隊導入建議矩陣

### Bullets

- 需求很模糊，還需要 PM / UX / Architect 一起收斂
  - 建議：BMAD

- 功能方向清楚，但變更風險高，需要正式記錄與封存
  - 建議：OpenSpec

- 日常功能迭代，希望低摩擦快速落地
  - 建議：Spec-Kit

- 新產品 / 大功能，且後續要正式控管 change
  - 建議：BMAD + OpenSpec

- 日常大多用輕量流程，重要 change 才升級
  - 建議：Spec-Kit + OpenSpec

---

## Slide 5

### Title

建議怎麼開始，不會一次導入太重

### Bullets

- 不建議三套一起全面導入
- 建議先挑 1 到 2 個真實需求試跑

- 可採三種路線
  - 路線 A：先試 Spec-Kit，驗證日常 feature 流程
  - 路線 B：先試 OpenSpec，驗證正式 change 管理能力
  - 路線 C：先試 BMAD，驗證需求探索與跨角色協作價值

- 評估指標
  - 文件是否真的被團隊使用
  - 任務拆解是否更清楚
  - 返工是否下降
  - 討論成本是否下降
  - 是否更容易做交接與回顧

---

## Closing Slide Optional

### Title

一句話總結

### Bullets

- BMAD：需求還模糊時最有價值
- OpenSpec：需要正式追蹤變更時最有價值
- Spec-Kit：日常 feature 交付時最有價值

---

## Presenter Notes Optional

### Bullets

- 這三套不是互斥關係，可以混搭
- 先試跑真實需求，再決定標準流程
- 不要先追求完美標準，先找最適合團隊節奏的做法
