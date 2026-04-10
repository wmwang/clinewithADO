#!/usr/bin/env python3
"""
Aggregate batch analysis results into a final team_rules.md.

This script does NOT call Claude — it prepares structured input so Claude
can do the actual analysis. Three modes are supported:

1. Standard (single-agent) mode:
   python pr_knowledge_build.py --input-dir /tmp/pr_batches/
       Aggregates all batches and emits one large analysis prompt.
       Suitable for small repos (<200 PRs) where context fits in one pass.

2. Per-batch prompt (for sub-agents, Map phase):
   python pr_knowledge_build.py --input-file /tmp/batch_0.json --per-batch-prompt
       Emits a focused prompt for a single batch.
       Each sub-agent processes one batch independently and returns a pattern summary.

3. Merge prompt (for main agent, Reduce phase):
   python pr_knowledge_build.py --merge-prompt --summaries-dir /tmp/summaries/
       Reads all batch_summary_*.txt from the summaries dir,
       emits a final merge prompt for the main agent to produce team_rules.md.

4. Stats only:
   python pr_knowledge_build.py --input-dir /tmp/pr_batches/ --stats-only

Environment variables:
  ADO_PAT, ADO_ORG, ADO_PROJECT  (not required — this script is offline)
"""

import argparse
import glob
import json
import os
import sys
from collections import Counter


# ── Data loading ──────────────────────────────────────────────────────────────

def load_batches(input_dir: str = None, input_file: str = None) -> list:
    """Load all PR records from batch JSON files."""
    files = []
    if input_file:
        files = [input_file]
    elif input_dir:
        files = sorted(glob.glob(os.path.join(input_dir, "batch_*.json")))
        if not files:
            files = sorted(glob.glob(os.path.join(input_dir, "*.json")))

    all_prs = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            for batch in data:
                all_prs.extend(batch.get("prs", []))
        else:
            all_prs.extend(data.get("prs", []))
    return all_prs


def load_summaries(summaries_dir: str) -> list[tuple[str, str]]:
    """Load batch summary text files. Returns list of (filename, content)."""
    files = sorted(glob.glob(os.path.join(summaries_dir, "batch_summary_*.txt")))
    if not files:
        files = sorted(glob.glob(os.path.join(summaries_dir, "*.txt")))
    results = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            results.append((os.path.basename(f), fh.read().strip()))
    return results


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        return {}
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


# ── Statistics ────────────────────────────────────────────────────────────────

def compute_stats(prs: list) -> dict:
    status_counter    = Counter()
    file_counter      = Counter()
    total_threads     = 0
    prs_with_threads  = 0

    for pr in prs:
        threads = pr.get("threads", [])
        if not threads:
            continue
        prs_with_threads += 1
        for t in threads:
            total_threads += 1
            status = t.get("status", "unknown")
            status_counter[status] += 1
            f = t.get("file")
            if f:
                file_counter[os.path.basename(f)] += 1

    return {
        "total_prs":        len(prs),
        "prs_with_threads": prs_with_threads,
        "total_threads":    total_threads,
        "by_status":        dict(status_counter.most_common()),
        "top_files":        dict(file_counter.most_common(20)),
    }


# ── Prompt builders ───────────────────────────────────────────────────────────

def _thread_lines(prs: list) -> str:
    """Compact one-line representation of all threads, suitable for prompts."""
    lines = []
    for pr in prs:
        for t in pr.get("threads", []):
            status  = t.get("status", "")
            file_   = t.get("file", "")
            comment = t.get("comment", "").replace("\n", " ").strip()[:250]
            lines.append(
                f"[{status.upper()}] "
                f"{os.path.basename(file_) if file_ else '(PR-level)'} | "
                f"{comment}"
            )
    return "\n".join(lines)


def build_per_batch_prompt(prs: list, stats: dict, config: dict,
                            batch_index: int, total_batches: int) -> str:
    """
    Prompt for a single sub-agent handling one batch (Map phase).
    The sub-agent should return a compact JSON pattern summary,
    NOT the final team_rules.md — that's the main agent's job.
    """
    repo             = config.get("repo", "unknown")
    include_wont_fix = config.get("include_wont_fix", True)
    threads_text     = _thread_lines(prs)

    return f"""你是一位資深 Java Spring Boot 技術 Lead。
你正在處理 repo「{repo}」PR review 歷史分析任務的第 {batch_index + 1} 批（共 {total_batches} 批）。

**你的任務只有一件事**：從以下 {stats['total_prs']} 個 PR 的 review threads 中，
找出重複出現的問題模式，整理成結構化 JSON。
不要輸出最終文件，只輸出 JSON pattern summary，讓主 agent 在最後合併。

以下是這批 PR 的所有有意義 review threads（格式：[狀態] 檔名 | 留言摘要）：

---
{threads_text}
---

統計：
- 此批 PR 數：{stats['total_prs']}（含有 thread 的：{stats['prs_with_threads']}）
- FIXED：{stats['by_status'].get('fixed', 0)}，ACTIVE：{stats['by_status'].get('active', 0)}
{"- WONTFIX：" + str(stats['by_status'].get('wontFix', 0)) if include_wont_fix else ""}
- 本批最常被留言的檔案：{", ".join(list(stats['top_files'].keys())[:5])}

**請輸出以下 JSON 格式（不要輸出其他任何文字）**：

```json
{{
  "batch": {batch_index},
  "pr_count": {stats['total_prs']},
  "thread_count": {stats['total_threads']},
  "patterns": [
    {{
      "id": "P001",
      "title": "一句話描述這個問題模式",
      "category": "CA規範 | Security | Performance | 例外處理 | Logging | 測試 | 其他",
      "occurrences": 3,
      "status_breakdown": {{"fixed": 2, "active": 1, "wontFix": 0}},
      "representative_comment": "最能代表這個問題的留言原文（不超過 150 字）",
      "affected_files": ["UserService.java", "OrderController.java"],
      "severity_suggestion": "MAJOR"
    }}
  ],
  "wontfix_notes": [
    {{
      "title": "這個團隊刻意不管的事項",
      "comment": "原始留言摘要"
    }}
  ],
  "top_files": {json.dumps(dict(list(stats['top_files'].items())[:10]), ensure_ascii=False)}
}}
```

分析原則：
- FIXED 是最可信的訊號，優先列出
- 相似問題合併為一個 pattern，不要拆得太細
- WONTFIX / BYDESIGN 放到 wontfix_notes，不要混入 patterns
- occurrences 是這批中這個問題出現幾次
- 如果這批沒有特別值得提的 pattern，patterns 可以是空陣列
"""


def build_standard_prompt(prs: list, stats: dict, config: dict) -> str:
    """Full analysis prompt for single-agent mode (small repos)."""
    repo             = config.get("repo", "unknown")
    include_wont_fix = config.get("include_wont_fix", True)
    threads_text     = _thread_lines(prs)

    return f"""你是一位資深 Java Spring Boot 技術 Lead，正在分析 repo「{repo}」過去一年的 {stats['total_prs']} 個 PR review 紀錄。

以下是所有有意義的 review thread 清單（格式：[狀態] 檔名 | 留言摘要）：

---
{threads_text}
---

統計摘要：
- 總 threads：{stats['total_threads']}
- FIXED（雙方認可的問題）：{stats['by_status'].get('fixed', 0)}
- ACTIVE（尚未解決）：{stats['by_status'].get('active', 0)}
{"- WONTFIX（刻意不修）：" + str(stats['by_status'].get('wontFix', 0)) if include_wont_fix else ""}
- 最常被留言的檔案：{", ".join(list(stats['top_files'].keys())[:5])}

{_final_output_instructions(repo, stats)}
"""


def build_merge_prompt(summaries: list[tuple[str, str]], config: dict,
                        total_pr_count: int, total_thread_count: int) -> str:
    """
    Prompt for the main agent to merge all batch summaries (Reduce phase).
    summaries: list of (filename, content) tuples from batch sub-agents.
    """
    repo = config.get("repo", "unknown")

    summaries_text = ""
    for fname, content in summaries:
        summaries_text += f"\n\n### {fname}\n{content}"

    return f"""你是一位資深 Java Spring Boot 技術 Lead。
你已完成對 repo「{repo}」所有 {len(summaries)} 批 PR review 紀錄的分批分析。

以下是每批 sub-agent 回傳的 pattern summary：
{summaries_text}

---

現在執行 **Reduce 合併**：
1. 跨批次合併相同/相似的 pattern（加總 occurrences）
2. 計算每個 pattern 在所有批次的總出現次數
3. 合併所有批次的 wontfix_notes（去重）
4. 合併 top_files，累加各批次的出現次數

總計：{total_pr_count} 個 PR，{total_thread_count} 則 threads。

{_final_output_instructions(repo, {"total_prs": total_pr_count, "total_threads": total_thread_count})}
"""


def _final_output_instructions(repo: str, stats: dict) -> str:
    """Shared output format instructions used in both standard and merge prompts."""
    return f"""請輸出**繁體中文** Markdown 文件：

---

# {repo} 團隊 Code Review 規則庫
> 從 {stats['total_prs']} 個 PR（{stats.get('total_threads', '?')} 則 review 留言）自動提煉
> 生成日期：{{TODAY}}

## 📌 高頻問題規則（出現 3 次以上，應列為強制規範）

對每條規則：
- **規則**：一句話描述
- **出現次數**：N 次
- **反例**：從實際留言提煉一個典型的錯誤寫法
- **正例**：對應的正確寫法
- **嚴重度建議**：BLOCKER / MAJOR / MINOR

## ⚠️ 中頻問題（出現 2 次）

同上格式，但可省略反例/正例。

## 🔍 單次重要問題（只出現一次但影響嚴重）

條列即可，不需範例。

## 🤝 團隊刻意不強制的事項（WONTFIX / BYDESIGN）

條列說明：這個 repo/團隊對哪些 CA 規則採取寬鬆態度，避免未來 reviewer 浪費時間。

## 📁 高風險檔案清單

| 檔案 | 被留言次數 | 說明 |
|------|----------|------|
| ... | ... | ... |

---

分析原則：
1. 以 FIXED threads 為主要訊號（代表問題被確認且修正）
2. 相似意思的留言應合併歸類，不要重複列出
3. 避免過度泛化——保持規則和這個 repo 的實際程式碼習慣相關
4. WONTFIX 是寶貴資訊，代表這個團隊的風格選擇，不要評判
"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Aggregate batch data and build Claude analysis prompts"
    )
    parser.add_argument("--input-dir",      metavar="DIR",
                        help="Directory containing batch_*.json files")
    parser.add_argument("--input-file",     metavar="FILE",
                        help="Single batch JSON file")
    parser.add_argument("--stats-only",     action="store_true",
                        help="Print stats only, skip prompt generation")
    parser.add_argument("--per-batch-prompt", action="store_true",
                        help="[Sub-agent / Map] Emit a focused prompt for a single batch")
    parser.add_argument("--batch-index",    type=int, default=0,
                        help="Batch index (0-based) used in --per-batch-prompt header")
    parser.add_argument("--total-batches",  type=int, default=1,
                        help="Total batch count used in --per-batch-prompt header")
    parser.add_argument("--merge-prompt",   action="store_true",
                        help="[Main agent / Reduce] Merge batch summaries into final prompt")
    parser.add_argument("--summaries-dir",  metavar="DIR",
                        help="Directory with batch_summary_*.txt files (for --merge-prompt)")
    parser.add_argument("--total-prs",      type=int, default=0,
                        help="Total PR count across all batches (for --merge-prompt)")
    parser.add_argument("--total-threads",  type=int, default=0,
                        help="Total thread count across all batches (for --merge-prompt)")
    parser.add_argument("--config",         metavar="PATH",
                        help="Config file path")
    args = parser.parse_args()

    # Load config
    default_config = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )
    config_path = args.config or default_config
    config = load_config(config_path)

    # ── Merge / Reduce mode ─────────────────────────────────────────────────
    if args.merge_prompt:
        if not args.summaries_dir:
            parser.error("--merge-prompt requires --summaries-dir")
        summaries = load_summaries(args.summaries_dir)
        if not summaries:
            print(json.dumps({"error": f"No summary files found in {args.summaries_dir}"}))
            sys.exit(1)
        sys.stderr.write(f"Merging {len(summaries)} batch summaries...\n")
        prompt = build_merge_prompt(
            summaries, config,
            total_pr_count=args.total_prs,
            total_thread_count=args.total_threads,
        )
        print(prompt)
        return

    # ── All other modes need PR data ────────────────────────────────────────
    if not args.input_dir and not args.input_file:
        parser.error("Provide --input-dir, --input-file, or --merge-prompt")

    prs   = load_batches(input_dir=args.input_dir, input_file=args.input_file)
    stats = compute_stats(prs)

    if args.stats_only:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    # Print stats to stderr so stdout is clean for the prompt
    sys.stderr.write(json.dumps({
        "total_prs":        stats["total_prs"],
        "prs_with_threads": stats["prs_with_threads"],
        "total_threads":    stats["total_threads"],
        "by_status":        stats["by_status"],
        "top_files":        stats["top_files"],
    }, ensure_ascii=False, indent=2) + "\n")

    # ── Per-batch prompt (Map phase, for sub-agents) ─────────────────────────
    if args.per_batch_prompt:
        prompt = build_per_batch_prompt(
            prs, stats, config,
            batch_index=args.batch_index,
            total_batches=args.total_batches,
        )
    else:
        # ── Standard single-agent prompt ────────────────────────────────────
        prompt = build_standard_prompt(prs, stats, config)

    print(prompt)


if __name__ == "__main__":
    main()
