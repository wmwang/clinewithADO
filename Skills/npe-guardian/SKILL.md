---
name: npe-guardian
description: Detect, triage, fix, and prepare pull requests for Java null-safety defects by combining SpotBugs, NullAway, and Checker Framework findings with source-aware LLM reasoning. Use when Codex needs to investigate possible Java NullPointerException risks, choose an appropriate null-analysis depth for a Java repository, scan changed files or a module, separate likely true positives from noise, apply safe null-handling fixes, run targeted verification, and prepare a PR for GitHub or Azure DevOps.
---

# NPE Guardian

## 概覽

這個 Skill 的目標不是只產出靜態分析報告，而是把 Java 的 null-safety finding 轉成可驗證、可提交、可開 PR 的修復工作。預設先從 `SpotBugs` 開始；當專案本身已經具備較成熟的 nullness tooling 時，再擴展到 `NullAway` 與 `Checker Framework`。

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

依照專案成熟度選擇分析深度。

- `fast`: 只跑 `SpotBugs`。適合 legacy repo、第一次掃描、低摩擦自動修復。
- `strict`: 跑 `SpotBugs + NullAway`。適合專案已導入 `Error Prone` 與基本 nullness annotation。
- `deep`: 跑 `SpotBugs + NullAway + Checker Framework`。適合願意承擔較高導入與修復成本的團隊。

除非 repo 本身已經明顯支援更嚴格的 tooling，否則預設從 `fast` 開始。

## 工作流程

1. 確認這是一個 Java repository，並偵測 build tool。
2. 用 [`scripts/detect_null_tools.py`](./scripts/detect_null_tools.py) 判斷目前 repo 適合 `fast`、`strict` 或 `deep`。
3. 如果使用情境跟 branch、PR 或最近修改有關，先縮小到變更過的 `.java` 檔案。
4. 依選定模式執行對應工具。
5. 用 [`scripts/parse_spotbugs_npe.py`](./scripts/parse_spotbugs_npe.py) 解析 `SpotBugs` XML，並把其他工具輸出整理成同樣可比對的 finding 結構。
6. 依 [`references/tooling-notes.md`](./references/tooling-notes.md) 的原則合併 findings。
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

使用以下 heuristics：

- `fast`: 沒有明顯 nullness annotation、沒有 `Error Prone`、或使用者要低風險低摩擦。
- `strict`: build 已參考 `NullAway`、`Error Prone`，或 repo 已穩定使用 `javax.annotation`、`jakarta.annotation`、`org.jetbrains.annotations` 等 annotation 套件。
- `deep`: repo 已整合 `Checker Framework`，或使用者明確要求更高保證且接受較高成本。

如果 repo 尚未導入較嚴格的工具，不要在同一個 auto-fix patch 裡順手做整個 build adoption，除非使用者明確要求。

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

## 執行 NullAway

只在 repo 已經明確支援 `Error Prone` / `NullAway` 時才執行。

常見訊號：

- Maven compiler config 已含 `error_prone_core`
- Gradle 已套用 Error Prone plugin
- build 裡已有 `-Xep:NullAway` 或 `NullAway` 相關設定

優先沿用既有 compile 命令，例如：

```bash
mvn -q -DskipTests compile
```

```bash
./gradlew compileJava
```

Windows 可改成：

```bash
gradlew.bat compileJava
```

再從 compiler output 擷取 `file`、`line`、`symbol`、`message` 做 triage。

## 執行 Checker Framework

只在 build 已經支援，或使用者明確要求時才執行。

常見命令：

```bash
mvn -q -DskipTests compile
```

```bash
./gradlew compileJava
```

Windows 可改成：

```bash
gradlew.bat compileJava
```

把它當成高訊號但高摩擦的工具，不要因為它更嚴格就直接做大範圍重構。

## Finding 合併規則

先合併 findings，再決定修不修。

- 兩套工具指向同一條 dereference path 時，可信度上升。
- `SpotBugs` 有報、`NullAway` 或 `Checker Framework` 沒報，不代表一定沒問題；三者著重面向不同。
- `NullAway` / `Checker Framework` 有報 contract 問題、`SpotBugs` 沒報時，優先考慮局部修補，不要立刻做大規模 signature refactor。
- 工具間結論衝突時，以原始碼真實語意與最小安全修改為準。

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
- 嚴格工具報的是 repository-wide annotation policy 缺口，而不是這次修改範圍內的明確 NPE 風險

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
- 大量 annotation campaign
- 整個 module 改成 `Optional`
- 只為了消 warning 而不處理真實風險
- 在同一個 auto-fix patch 裡順手導入 `NullAway` 或 `Checker Framework`

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
- [`scripts/detect_null_tools.py`](./scripts/detect_null_tools.py)：跨平台偵測 SpotBugs / NullAway / Checker Framework 線索
- [`scripts/list_changed_java_files.py`](./scripts/list_changed_java_files.py)：跨平台列出變更過的 `.java` 檔案
- [`scripts/parse_spotbugs_npe.py`](./scripts/parse_spotbugs_npe.py)：解析 SpotBugs XML
- [`assets/spotbugs-null-filter.xml`](./assets/spotbugs-null-filter.xml)：聚焦 null 相關 bug pattern
- [`references/fix-strategies.md`](./references/fix-strategies.md)：修復策略對照
- [`references/pr-template.md`](./references/pr-template.md)：PR 說明模板
- [`references/tooling-notes.md`](./references/tooling-notes.md)：三套工具定位與 findings merge 原則
