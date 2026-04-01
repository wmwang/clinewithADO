---
name: superpowers-workflow
description: 用於以單一 skill 控管完整開發流程：從 brainstorming、git worktree、計畫撰寫、subagent 執行、code review 到分支收尾，適合功能開發與多步驟實作工作。
---

# Superpowers 工作流程

當使用者希望以單一入口跑完整實作流程，而不是手動切換多個 superpowers skill 時，使用這個 skill。

這個 skill 將以下流程整合成單一生命週期：

1. 腦力激盪與設計
2. 建立隔離的 git worktree
3. 撰寫 implementation plan
4. 執行計畫，優先使用 subagent
5. 執行 review gate
6. 完成開發分支收尾

它也內建原本分散在其他 skill 裡的重要紀律：

7. 任何失敗時都要做系統化除錯
8. 行為變更預設採用 TDD
9. 任何完成聲明前都要先驗證
10. 技術性評估收到的 review feedback
11. 只有在真正獨立的工作上才做平行派工
12. 未選擇 subagent 時的 inline execution 流程
13. skill 撰寫與維護
14. 全域 superpowers 操作規則

## 核心原則

單一入口、分階段執行、每一階段都有明確 gate。

不要盲目前跳。只有當目前階段完成，或使用者明確要求跳過時，才能往下一階段移動。

## 全域操作規則

這個 skill 取代原本分散的 superpowers skills。只要它適用，就用它當作主控流程，而不是再去找其他 superpowers skill。

優先順序：

1. 使用者指示與 repository 指示
2. 這個 workflow skill
3. 預設 assistant 行為

操作規則：

- 流程規則優先於實作動作。
- 如果這個 skill 內有 checklist，就照 checklist 執行，不要臨場 improvising。
- 如果這裡已經定義某種 failure mode，就先套用對應的內嵌 discipline，再改程式。
- 如果一個任務同時看起來符合多個段落，先採用限制較嚴格的那一個。
- 不要把「這很簡單」當成跳過紀律的理由。

## 何時使用

當使用者說出以下需求，或語意上等同這些需求時，使用這個 skill：

- 「我想要一個 workflow skill」
- 「整個 feature workflow 幫我跑」
- 「從設計一路處理到 PR」
- 「用一個 skill 管 brainstorming、plan、execution、review」
- 「幫我主控整個 implementation 流程」

除非使用者明確要求完整流程，否則不要把這個 skill 用在極小型的一次性修改上。

## 開場宣告

請這樣說：

`我會用 superpowers-workflow skill，從目前階段開始一路控管到完成。`

## 階段模型

先判斷目前在哪個階段。不要假設每個任務都一定從最前面開始。

### Stage 0：盤點目前狀態

先判斷我們現在在哪：

- 如果沒有已核准的設計，而且這次需求會改變行為，從 Stage 1 開始。
- 如果已有已核准設計，但還沒有 plan，從 Stage 3 開始。
- 如果 plan 已存在，而且使用者要直接開始實作，從 Stage 4 開始。
- 如果實作已完成，只剩驗證或收尾，從 Stage 5 或 6 開始。

如果起始點不明確，做最安全的合理假設，並清楚說明你的假設。

## Stage 1：腦力激盪與設計

凡是創造性工作、行為變更、新功能、架構修改，都應先走這個階段。

必要行為：

1. 先探索專案上下文。
2. 一次只問一個釐清問題。
3. 提出 2-3 個方案與取捨。
4. 提出設計並取得核准。
5. 將設計文件寫到 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`，除非使用者指定別的位置。
6. 自我審查 spec 的歧義、矛盾、placeholder 與 scope。
7. 在進下一步前，請使用者審閱寫好的 spec。

如果視覺化溝通會更有效，請以獨立訊息提出 visual companion，並閱讀：

- `references/visual-companion.md`

如果需要 brainstorm 的支援資產，可使用：

- `scripts/start-server.sh`
- `scripts/stop-server.sh`
- `scripts/server.cjs`
- `scripts/helper.js`
- `scripts/frame-template.html`

如果想用可重複使用的 spec 檢查 prompt，可參考：

- `prompts/spec-document-reviewer-prompt.md`

硬性 gate：

在設計尚未被提出並獲得核准前，不得開始實作。

## Stage 2：隔離工作區

在撰寫 plan 或執行多步驟實作前，優先建立隔離的 git worktree。

依序採用以下規則：

1. 若 `.worktrees/` 已存在，優先使用它。
2. 否則若 `worktrees/` 已存在，使用它。
3. 否則檢查 repository 指示，例如 `CLAUDE.md`、`GEMINI.md`、`AGENTS.md`。
4. 否則詢問使用者 worktree 應放在哪裡。

若使用專案內本地 worktree：

1. 先確認該目錄已被 git ignore。
2. 若尚未 ignore，先把它加到 `.gitignore` 並 commit，再建立 worktree。

之後：

1. 建立對應 branch 的 worktree。
2. 根據專案技術棧執行 setup 指令。
3. 跑 baseline 測試。

如果 baseline 已經失敗，不要默默繼續。要先回報現況，再問是否繼續。

## Stage 3：撰寫計畫

當需求或 spec 已存在，且工作屬於多步驟實作時，先寫完整 implementation plan，再碰程式碼。

必要輸出：

- 將 plan 存到 `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`，除非使用者指定其他路徑。

plan 必須具備以下品質：

1. 假設實作者幾乎不了解專案上下文。
2. 使用精確檔案路徑。
3. 將工作拆成小步驟。
4. 合適時採用 TDD 型步驟。
5. 包含精確指令與預期結果。
6. 不得有 placeholder。

自我審查：

1. 檢查 spec coverage。
2. 移除 placeholders。
3. 檢查型別與命名一致性。

如果想用可重複使用的 plan 審查 prompt，可參考：

- `prompts/plan-document-reviewer-prompt.md`

plan 存檔後，提供兩種執行方式：

1. Subagent-driven execution
2. Inline execution

除非任務彼此高度耦合，或使用者明確要求 inline，否則優先推薦 subagent-driven execution。

## Stage 4：執行計畫

優先模式：subagent-driven development。

每個 task 使用一個全新的 subagent。不要讓 subagent 自己去讀 plan 檔；要直接提供完整 task 文字與必要上下文。

每個 task 的流程：

1. 派出 implementer。
2. 處理問題、阻塞與澄清。
3. 要求測試與 self-review。
4. 執行 spec compliance review。
5. 修正任何 spec 缺口。
6. 執行 code quality review。
7. 修正任何品質問題。
8. 標記 task 完成後再往下。

本階段會用到的 prompt 資產：

- `prompts/implementer-prompt.md`
- `prompts/spec-reviewer-prompt.md`
- `prompts/code-quality-reviewer-prompt.md`

執行規則：

- 絕不能跳過 spec compliance review。
- spec compliance review 尚未通過前，不能開始 code quality review。
- 只要還有重要 review issue 未解決，就不能進入下一個 task。
- 每個子任務都要優先選擇足夠勝任、但最小可用的模型。

如果使用者明確要求 inline execution，也要盡可能保留相同的 review gate。

### Inline Execution Mode

如果沒有選擇 subagent execution，就自己執行 plan，但仍要保持同樣的紀律：

1. 先完整讀完 plan，對不清楚的地方先提出挑戰。
2. 依 plan 建立 task tracker。
3. 依序執行各 task。
4. 每個 task 或每一批次之後都執行必要驗證。
5. 一旦受阻，立刻停下來，不要猜。
6. 完成後進入 branch completion 階段。

## 內嵌紀律：除錯

只要遇到 bug、測試失敗、build 壞掉、整合異常、或任何不符合預期的行為，在提出或實作修正前，必須切換到除錯模式。

鐵律：

`沒有完成 root cause investigation，就不能修。`

必要順序：

1. 仔細讀錯誤輸出。
2. 穩定重現問題。
3. 檢查近期變更。
4. 在系統邊界蒐集證據，不要猜。
5. 追溯錯誤值或異常行為的來源。
6. 形成單一假設。
7. 以最小改動驗證該假設。
8. 之後才能實作真正修正。

規則：

- 不要堆疊多個猜測性修正。
- 不要一邊說「應該是這個」一邊盲修。
- 如果連續 3 次修正都失敗，就停下來重新質疑架構，而不是做第 4 次猜測。

內建除錯參考：

- `references/debugging/root-cause-tracing.md`
- `references/debugging/condition-based-waiting.md`
- `references/debugging/defense-in-depth.md`
- `scripts/debugging/find-polluter.sh`

## 內嵌紀律：測試驅動開發（TDD）

凡是新行為、bug 修正、行為變更，除非使用者明確表示不要，否則預設採用 TDD。

以下例外必須得到使用者明確同意，而且應該很少見：

- 丟棄型 prototype
- 產生式碼
- 純設定檔修改

鐵律：

`沒有先看到 failing test，就不能寫 production code。`

如果 production code 已經先寫了，必須刪掉那份實作，回到先寫 test 的流程。不要把舊實作留著當 reference 再來寫 test。

必要循環：

1. 為單一行為寫一個 failing test。
2. 執行測試，確認它是因為正確原因而 fail。
3. 寫出最小可通過的實作。
4. 再跑測試，確認它 pass。
5. 在維持綠燈狀態下做重構。

規則：

- 一個 test 只測一個行為。
- 測試名稱必須清楚描述行為。
- 優先測真實行為，不要過度依賴 mock。
- 如果 test 一開始就 pass，代表你還沒測到缺失行為。
- 如果 test 是 error 而不是因為預期原因 fail，就先修 test，直到它正確 fail。
- 一旦決定用 TDD，就不能把已寫好的 implementation 留著當 reference。
- 為了讓測試變綠，不要順便加入額外功能。
- 只有在綠燈之後，才能針對可讀性、重複與結構進行重構；重構時不得改變行為。

必須立即拒絕的常見 rationalization：

- 「我之後再補 test」
- 「我已經手動測過了」
- 「這個太簡單，不用 test」
- 「我先把 implementation 留著參考」
- 「這邊 TDD 太教條」
- 「把已寫的 code 刪掉太浪費」

只要你發現自己在說這些話，就立刻停下來，回到 failing-test-first 流程。

在宣告 TDD 工作完成前，必須確認：

- 每個新增或變更的行為都有測試
- 每個相關測試在實作前都真的 fail 過
- fail 的原因是正確的
- 實作是最小可行的綠燈版本
- 目標測試都 pass
- 相關較大範圍的測試集也仍然 pass

如果卡住：

- 如果 test 很難寫，代表設計可能不夠清楚
- 如果 test setup 太大，應該簡化介面或抽 helper
- 如果什麼都得 mock，代表程式耦合可能太高
- 如果不知道怎麼表達想要的 API，先寫出理想用法，再逐步收斂

內建測試參考：

- `references/testing/testing-anti-patterns.md`

## 內嵌紀律：完成前驗證

凡是要宣稱「已修好」、「已通過」、「已完成」、「可 merge」、「可 commit」，都必須先做最新驗證。

鐵律：

`沒有最新驗證證據，就不能做完成聲明。`

必要順序：

1. 先辨認哪個指令可以證明這個聲明。
2. 現在立刻執行它。
3. 讀完整輸出與 exit status。
4. 依證據陳述實際結果。

規則：

- 不要依賴之前跑過的測試結果。
- 不要因為 subagent 說成功就直接相信。
- 驗證結果若過期或失敗，就不能 commit、push、或提出 merge 選項。

## 內嵌紀律：接收 Review Feedback

當使用者或外部 reviewer 提出 review comments 時，不要盲目照做。

必要順序：

1. 先完整讀完所有 feedback。
2. 任何不清楚的地方，先重述或提問澄清，再改 code。
3. 把每個建議放回實際 codebase 驗證。
4. 一次實作一個項目。
5. 每個重要修正後都重新測試。

規則：

- 技術正確性比表演式同意重要。
- 如果 feedback 不適用於這個 codebase，要拿證據推回去。
- 如果有多個 comment 不清楚，要先釐清，再開始實作。

## 內嵌紀律：平行派工

只有在工作真的彼此獨立時，才能平行派工。

適合平行派工的情況：

- 任務碰的是不同檔案或不同子系統
- 任務彼此不依賴結果
- agents 不會互相衝突於編輯或共享狀態

不適合平行派工的情況：

- 修掉一個問題就可能順便修掉其他問題
- 工作需要共享架構判斷
- 多個 agents 會同時改同一區域

若要平行化，指派內容必須保持高度聚焦，最後還要驗證整合結果。

## 內嵌能力：Skill 撰寫

當要建立、編輯、整合、或驗證 skill 時，使用這一段規則。

核心原則：

寫 skill，就是把 TDD 套用到流程文件上。

必要方法：

1. 先定義一個真實的 pressure scenario。
2. 先觀察在沒有 skill 時會怎麼失敗、偷懶、或鑽漏洞。
3. 寫出最小 skill 內容，只補上真正缺失的部分。
4. 重新跑同一情境，確認 skill 現在能導向正確行為。
5. 行為正確之後，再調整文字與表達。

skill 撰寫規則：

- skill 應描述可重複使用的技巧、模式、流程或參考資料。
- 不要把一次性的事後敘事寫成 skill。
- trigger description 要聚焦在「何時使用」，不是摘要整個 workflow。
- 優先保持 `SKILL.md` 精簡，把重型參考資料移到支援檔。
- 名稱用小寫加連字號。
- frontmatter 必須正確，至少要有 `name` 和 `description`。

建議 skill 結構：

- `SKILL.md` 放核心 workflow
- `references/` 放重型文件
- `scripts/` 放可重複執行、具決定性的 helper

skill 撰寫支援資源：

- `references/skill-authoring/anthropic-best-practices.md`
- `references/skill-authoring/persuasion-principles.md`
- `references/skill-authoring/testing-skills-with-subagents.md`
- `references/skill-authoring/graphviz-conventions.dot`
- `scripts/skill-authoring/render-graphs.js`

驗證 skill 時：

- 要用真實 prompt，不要用理想化 prompt
- 要檢查 trigger description 是否真的導向正確行為
- 優先用能暴露 rationalization 與偷跑行為的 pressure test
- 如果 agent 只照 description 做、卻跳過內文，就要收緊 wording

## Stage 5：Review Gate

在以下節點請求 review：

- subagent-driven execution 的每個 task 後
- inline execution 的每一批次後
- merge 或 PR 前
- 當工作風險高、狀況不清、或特別複雜時

使用：

- `prompts/code-reviewer.md`

review 期待：

1. 比對實作是否符合 plan 或 requirements。
2. 檢查測試品質。
3. 檢查可維護性與設計。
4. 依嚴重度分類 findings。
5. 修掉 critical 與 important issues 後才能繼續。

如果 reviewer 判斷錯誤，要用技術證據推回去，而不是盲從。

## Stage 6：完成開發分支

只有在實作完成且測試通過時，才能進入此階段。

在提出選項前：

1. 跑相關測試集。
2. 確認正確的 base branch。

然後只能提出以下四個選項：

1. 本地 merge 回 base branch
2. push 並建立 Pull Request
3. 保留目前 branch 不動
4. 丟棄這份工作

規則：

- 測試失敗時不能繼續。
- 沒有明確 typed confirmation，不得丟棄工作。
- worktree 清理方式必須符合使用者實際選擇。

## 決策捷徑

選擇最輕量但仍然正確的 workflow 路徑：

- 有設計變更但沒 spec：Stage 1 -> 2 -> 3 -> 4 -> 5 -> 6
- 已有核准 spec，但沒 plan：Stage 2 -> 3 -> 4 -> 5 -> 6
- 已有 plan，準備實作：Stage 2 -> 4 -> 5 -> 6
- 已實作完，只需要 review：Stage 5 -> 6

## 資源配置

這個 skill 把原本分散在多個 skills 的可重用資源集中起來：

- brainstorm helper scripts 放在 `scripts/`
- visual brainstorming 指引放在 `references/`
- review 與 subagent prompt templates 放在 `prompts/`
- debugging 參考資料放在 `references/debugging/`
- testing 參考資料放在 `references/testing/`
- debugging helper scripts 放在 `scripts/debugging/`
- skill-authoring 參考資料放在 `references/skill-authoring/`
- skill-authoring helper scripts 放在 `scripts/skill-authoring/`

## 非目標

這個 skill 是一個自包含的 orchestrator，不是用來取代工程判斷。

不要：

- 對小任務強迫使用者走完整流程，除非他明確要求
- 在 design-heavy 工作上跳過 approval gate
- 把 prompt template 當成閱讀實際 code 或 plan 的替代品
- 假設 workflow 一定要從 brainstorming 開始
- 依賴其他 superpowers skill 還存在於磁碟上

## 成功條件

當使用者只需呼叫這一個 workflow skill，而 agent 就能從目前生命週期階段一路安全地執行到 reviewed implementation 或乾淨的 branch handoff，而且不依賴任何其他 superpowers skill 留在磁碟上時，這個 skill 就算成功。
