# 三套 SDD Skill 內部分享簡報稿（5 頁版）

> 用途：給團隊做 10 到 15 分鐘內部分享。  
> 搭配文件：[三套 SDD Skill 比較：BMAD、OpenSpec、Spec-Kit](./sdd-skills-comparison.zh.md)

---

## 第 1 頁：為什麼要比較這三套

### 投影片標題

三套 SDD Skill：BMAD、OpenSpec、Spec-Kit，我們該怎麼選？

### 投影片重點

- 這三套都支援 spec-driven / spec-first 的開發方式
- 但它們解決的問題層級不同，不是單純誰比較強
- 我們要比較的重點是：
  - 適合什麼場景
  - 文件與流程差在哪裡
  - 導入成本與團隊收益是什麼

### 講稿提示

這三套工具看起來都在做 SDD，但其實不是同一層的東西。  
BMAD 比較像完整的產品研發方法，OpenSpec 比較像 change 管理框架，Spec-Kit 比較像工程團隊日常使用的 feature 規劃與實作流程。  
所以今天不是在問哪套最好，而是在問哪套最適合我們現在的工作型態。

---

## 第 2 頁：一頁看懂三套差異

### 投影片標題

BMAD / OpenSpec / Spec-Kit 一頁對照

### 投影片重點

| 面向 | BMAD | OpenSpec | Spec-Kit |
|---|---|---|---|
| 最像什麼 | AI 產品研發團隊作業系統 | 有狀態的正式變更單 | 工程團隊可直接開工的功能實作包 |
| 核心單位 | Agent / Workflow / Story | Change | Feature branch |
| 最強的完整性 | 跨角色協作流程完整 | Change lifecycle 完整 | Feature planning package 完整 |
| 適合誰 | PM / Architect / Dev / QA | 需要審核與封存的團隊 | 日常 feature 開發團隊 |
| 一句話選擇 | 需求還模糊就用它 | 要正式追蹤變更就用它 | 要快速 spec 化並開工就用它 |

### 講稿提示

這頁最重要的訊息只有一個：  
**OpenSpec 和 Spec-Kit 不是在比文件份數，而是在比哪一種完整性。**

- BMAD 的完整，是從需求探索一路到 story-ready
- OpenSpec 的完整，是這次 change 怎麼被記錄、驗證、同步、封存
- Spec-Kit 的完整，是工程團隊拿到一包文件後可以直接開工

---

## 第 3 頁：OpenSpec vs Spec-Kit 真正差在哪裡

### 投影片標題

最容易搞混的一組：OpenSpec vs Spec-Kit

### 投影片重點

- **OpenSpec**
  - 重點在 `proposal -> specs -> design -> tasks -> verify -> sync -> archive`
  - 適合高風險 change、跨團隊 change、需要 audit trail 的情境
  - 比較像正式變更單系統

- **Spec-Kit**
  - 重點在 `spec -> clarify -> plan -> tasks -> analyze -> implement`
  - 適合既有產品上的單一功能、MVP、日常迭代
  - 比較像工程實作包

- 關鍵差別
  - OpenSpec：比較強在 change lifecycle
  - Spec-Kit：比較強在 feature planning package

### 講稿提示

如果今天需求是「新增 MFA 登入」：

- 用 OpenSpec 做，團隊拿到的是一個正式 change：有 proposal、delta spec、驗證、封存
- 用 Spec-Kit 做，團隊拿到的是一包工程文件：spec、plan、research、data model、tasks

所以可以記成一句話：

- **OpenSpec 在管理這次變更**
- **Spec-Kit 在準備這個功能怎麼做**

---

## 第 4 頁：我們怎麼選

### 投影片標題

團隊導入建議矩陣

### 投影片重點

| 情況 | 建議 |
|---|---|
| 需求很模糊，還需要 PM / UX / Architect 一起收斂 | **BMAD** |
| 功能方向清楚，但變更風險高，需要正式記錄與封存 | **OpenSpec** |
| 日常功能迭代，希望低摩擦快速落地 | **Spec-Kit** |
| 新產品 / 大功能，且後續要正式控管 change | **BMAD + OpenSpec** |
| 日常大多用輕量流程，重要 change 才升級 | **Spec-Kit + OpenSpec** |

### 講稿提示

選擇時可以只看三件事：

1. 需求現在模不模糊？
2. 這次變更風險高不高？
3. 我們需不需要正式記錄、驗證、封存？

如果答案偏「模糊」，先用 BMAD。  
如果答案偏「高風險 + 要可查可封存」，先用 OpenSpec。  
如果答案偏「日常功能開發」，先用 Spec-Kit。

---

## 第 5 頁：建議試跑方式

### 投影片標題

建議怎麼開始，不會一次導入太重

### 投影片重點

- 不建議三套一起全面導入
- 建議先挑 1 到 2 個真實需求試跑
- 可採這三種路線：
  - **路線 A**：先試 Spec-Kit，驗證日常 feature 流程
  - **路線 B**：先試 OpenSpec，驗證正式 change 管理能力
  - **路線 C**：先試 BMAD，驗證需求探索與跨角色協作價值

- 建議評估指標：
  - 文件是否真的被團隊使用
  - 任務拆解是否更清楚
  - 返工是否下降
  - 討論成本是否下降
  - 是否更容易做交接與回顧

### 講稿提示

最務實的方式不是先定標準答案，而是先跑一輪真實案例。  
例如可以選：

- 一個中小型功能，用 Spec-Kit 試
- 一個高風險 change，用 OpenSpec 試
- 一個需求很模糊的新功能，用 BMAD 試

跑完之後再看：

- 哪套文件真的有人看
- 哪套流程最符合我們現在的協作方式
- 哪套最值得變成團隊標準

---

## 結尾一句話

- **BMAD**：需求還模糊時最有價值
- **OpenSpec**：需要正式追蹤變更時最有價值
- **Spec-Kit**：日常 feature 交付時最有價值

---

## 備用附錄：分享者可補充的兩句話

- 「這三套不是互斥關係，很多時候是不同階段可以混搭的工具。」
- 「先試跑真實需求，再決定標準流程，比一開始就定唯一標準更實際。」
