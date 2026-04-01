---
name: npe-guardian
description: Detect, triage, fix, and prepare pull requests for Java null-safety defects using SpotBugs findings plus source-aware LLM reasoning. Use when Codex needs to investigate possible Java NullPointerException risks in an existing repository, scan changed files or a module, separate likely true positives from noise, apply safe code-level null-handling fixes without relying on nullness annotations, run targeted verification, and prepare a PR for GitHub or Azure DevOps.
---

# NPE Guardian

## 概覽

這個 Skill 的目標不是只產出靜態分析報告，而是把 Java 的 null-safety finding 轉成可驗證、可提交、可開 PR 的修復工作。這個版本以 `SpotBugs` 為唯一靜態分析入口，避免依賴 `NullAway`、`Checker Framework` 或 repository-wide nullness annotation policy。

這個 Skill 對應你要的 `Level 2` 流程：偵測、判讀、修復、驗證、整理 PR 說明。

## 跨平台原則

這個 Skill 的 helper script 全部使用 `Python`，避免依賴 `bash/sh`、`rg` 或 Unix-only shell 行為。

預期最低需求：

- 已安裝 `Python 3`
- 已安裝 `git`
- Java 專案本身可用 `mvn`、`gradlew`、`gradle` 或團隊既有命令執行分析

在 Windows 上，優先用：

```bash
python path/to/script.py
```

不要假設使用者有 `Git Bash` 或 `WSL`。

## 模式

這個 Skill 只提供單一模式：

- `fast`: 跑 `SpotBugs`。適合 legacy repo、第一次掃描、低摩擦自動修復。

預設永遠從 `fast` 開始。

## 工作流程

1. 確認這是一個 Java repository，並偵測 build tool。
2. 用 [`scripts/detect_null_tools.py`](./scripts/detect_null_tools.py) 確認是否有 `SpotBugs` 線索，並回傳 `fast` 模式。
3. 如果使用情境跟 branch、PR 或最近修改有關，先縮小到變更過的 `.java` 檔案。
4. 依選定模式執行對應工具。
5. 用 [`scripts/parse_spotbugs_npe.py`](./scripts/parse_spotbugs_npe.py) 解析 `SpotBugs` XML。
6. 依 [`references/tooling-notes.md`](./references/tooling-notes.md) 的原則做 source-aware triage。
7. 打開真實原始碼，逐筆確認 finding 是否可操作。
8. 採用最小且安全的修復方式。
9. 跑最小必要驗證，再視情況擴大測試範圍。
10. 用 [`references/pr-template.md`](./references/pr-template.md) 整理 commit / PR 說明。

## 範圍選擇

預設先做小範圍掃描，不要一開始就掃整個 monorepo。

- 如果使用者提到 branch、PR、最近修改，先用 [`scripts/list_changed_java_files.py`](./scripts/list_changed_java_files.py) 取得變更 `.java` 檔案。
- 如果 repo 很大但沒有指定範圍，先從相關 module 或出問題的 package 開始。
- 如果 repo 根本沒接 SpotBugs，不要直接大改 build；先判斷是否有現成 profile、task 或團隊命令。

用 [`scripts/detect_build_tool.py`](./scripts/detect_build_tool.py) 偵測 `maven` 或 `gradle`。

## 模式選擇規則

這個 Skill 固定使用以下 heuristics：

- `fast`: 以 `SpotBugs` 做 finding 入口，配合原始碼判讀與局部安全修補。

不要在同一個 auto-fix patch 裡順手導入 `NullAway`、`Checker Framework`、`Error Prone nullness policy` 或 repository-wide annotation adoption。

## 執行 SpotBugs

### Maven

盡量產出穩定的 XML report 路徑，方便後續解析。

```bash
mvn -q -DskipTests spotbugs:spotbugs \
  -Dspotbugs.effort=Max \
  -Dspotbugs.threshold=Low \
  -Dspotbugs.xmlOutput=true \
  -Dspotbugs.excludeFilterFile="<skill-dir>/assets/spotbugs-null-filter.xml"
```

如果專案本來就有 SpotBugs profile 或 module 專用命令，優先沿用，不要硬套新規則。

### Gradle

```bash
./gradlew spotbugsMain \
  -PspotbugsEffort=Max \
  -PspotbugsReportLevel=low
```

如果是 Windows，可能要改成：

```bash
gradlew.bat spotbugsMain -PspotbugsEffort=Max -PspotbugsReportLevel=low
```

如果 build 沒有現成 SpotBugs task，先看 build file，不要憑空創造太多設定。

## Finding 判讀規則

先確認 `SpotBugs` finding，再決定修不修。

- `SpotBugs` 是入口，不是最終判決。
- 以原始碼真實語意、控制流程與最小安全修改為準。
- 不要因為想追求更嚴格的靜態保證，就把 patch 擴大成 annotation campaign 或 compiler-policy migration。

## Triage 規則

不要只看報告就自動修。一定要打開原始碼看控制流程。

以下情況可視為較可能的 true positive：

- nullable 值真的能沿某條合理路徑走到 dereference
- 現有 guard 不支配該 dereference
- 程式契約或附近使用情境無法證明它一定 non-null
- 至少一個 analyzer 的訊息跟原始碼推理一致，或多個弱訊號能拼成同一個風險

以下情況偏向 false positive 或應先 defer：

- framework lifecycle 保證 non-null，但 analyzer 看不到
- finding 依賴 generated code、reflection、proxy 或特殊 wiring
- 要安全修正必須先做業務語意決策
- 問題本質比較像 repository-wide annotation policy 缺口，而不是這次範圍內的明確 NPE 風險

如果不確定，寧可在 PR summary 註記，也不要做高風險修補。

## 修復策略

優先參考 [`references/fix-strategies.md`](./references/fix-strategies.md)。

偏好順序：

1. 重用檔案或 module 內既有 guard pattern
2. 補 local guard clause 或 early return
3. 把鏈式 dereference 拆成可檢查的中間變數
4. 只有在 fail-fast 語意合理時才用 `Objects.requireNonNull`
5. 只有在周邊 API 本來就接受 absence modeling 時才用 `Optional`

除非使用者明確要求，避免：

- 大範圍方法簽名變更
- 大量 nullness annotation campaign
- 整個 module 改成 `Optional`
- 只為了消 warning 而不處理真實風險
- 用 `@Nullable`、`@NonNull` 或類似註解當主要修法
- 在同一個 auto-fix patch 裡順手導入更嚴格的 nullness tooling

## 驗證

沒有證據不要宣稱修好了。

最低驗證要求：

- 重跑受影響程式碼最相關的測試
- 重跑產生該 finding 的 analyzer，確認問題消失、降級或有明確 defer 理由
- 如果沒有 focused tests，至少跑最小 module-level 驗證，並誠實說明還沒驗到哪裡

如果修正改變了 exception 行為、null return semantics 或 API contract，要在 PR 說明裡明講。

## PR 準備

程式改完後：

1. 整理每個 true positive 的位置、根因、修法
2. 註明哪些 finding 先 defer
3. 套用 [`references/pr-template.md`](./references/pr-template.md)
4. 依 remote 平台開 PR

平台建議：

- GitHub repo：優先走 Codex 內建 GitHub 工作流
- Azure DevOps repo：優先走 `az repos pr create` 或團隊既有自動化
- 如果使用者只要 patch 不要 PR，就停在驗證後並輸出整理好的 summary

## 資源

- [`scripts/detect_build_tool.py`](./scripts/detect_build_tool.py)：跨平台偵測 Maven / Gradle
- [`scripts/detect_null_tools.py`](./scripts/detect_null_tools.py)：跨平台偵測 SpotBugs 線索並回傳建議模式
- [`scripts/list_changed_java_files.py`](./scripts/list_changed_java_files.py)：跨平台列出變更過的 `.java` 檔案
- [`scripts/parse_spotbugs_npe.py`](./scripts/parse_spotbugs_npe.py)：解析 SpotBugs XML
- [`assets/spotbugs-null-filter.xml`](./assets/spotbugs-null-filter.xml)：聚焦 null 相關 bug pattern
- [`references/fix-strategies.md`](./references/fix-strategies.md)：修復策略對照
- [`references/pr-template.md`](./references/pr-template.md)：PR 說明模板
- [`references/tooling-notes.md`](./references/tooling-notes.md)：SpotBugs 定位與 source-aware triage 原則
