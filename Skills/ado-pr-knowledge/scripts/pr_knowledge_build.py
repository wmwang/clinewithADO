#!/usr/bin/env python3
"""
Aggregate batch analysis results into a final team_rules.md.

This script does NOT call Claude — it prepares structured input so Claude
can do the actual analysis. It also handles:
  - Merging multiple batch JSON files into one aggregated view
  - Computing thread frequency per file / per issue type
  - Emitting a prompt template Claude should use to produce team_rules.md

Usage:
  python pr_knowledge_build.py --input-dir /tmp/pr_batches/
      Reads all batch_*.json from the directory, aggregates, prints summary + analysis prompt.

  python pr_knowledge_build.py --input-file /tmp/batch_0.json
      Aggregate a single batch file.

  python pr_knowledge_build.py --input-dir /tmp/pr_batches/ --stats-only
      Print frequency statistics without the full analysis prompt.

Output (stdout): aggregated statistics JSON + the Claude analysis prompt.
"""

import argparse
import glob
import json
import os
import sys
from collections import Counter


def load_batches(input_dir: str = None, input_file: str = None) -> list:
    """Load all PR records from batch JSON files."""
    files = []
    if input_file:
        files = [input_file]
    elif input_dir:
        files = sorted(glob.glob(os.path.join(input_dir, "batch_*.json")))
        if not files:
            # Also accept any .json in directory
            files = sorted(glob.glob(os.path.join(input_dir, "*.json")))

    all_prs = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        # Handle both single-batch dict and array of batches
        if isinstance(data, list):
            for batch in data:
                all_prs.extend(batch.get("prs", []))
        else:
            all_prs.extend(data.get("prs", []))

    return all_prs


def compute_stats(prs: list) -> dict:
    """Compute frequency statistics from all threads."""
    status_counter   = Counter()
    file_counter     = Counter()
    total_threads    = 0
    prs_with_threads = 0
    threads_by_status = {"fixed": [], "wontFix": [], "byDesign": [], "active": []}

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
                # Normalize to just filename for readability
                file_counter[os.path.basename(f)] += 1
            if status in threads_by_status:
                threads_by_status[status].append({
                    "pr_id":   pr.get("id"),
                    "pr_title": pr.get("title", ""),
                    "file":    t.get("file"),
                    "line":    t.get("line"),
                    "comment": t.get("comment", "")[:300],  # truncate for stats
                })

    return {
        "total_prs":         len(prs),
        "prs_with_threads":  prs_with_threads,
        "total_threads":     total_threads,
        "by_status":         dict(status_counter.most_common()),
        "top_files":         dict(file_counter.most_common(20)),
        "threads_by_status": threads_by_status,
    }


def build_analysis_prompt(prs: list, stats: dict, config: dict) -> str:
    """
    Build the prompt Claude should use to produce team_rules.md.
    This is printed so Claude can copy it into the analysis step.
    """
    lang = config.get("output_language", "zh-TW")
    repo = config.get("repo", "unknown")
    include_wont_fix = config.get("include_wont_fix", True)

    # Prepare compact thread listing for Claude to analyze
    thread_lines = []
    for pr in prs:
        for t in pr.get("threads", []):
            status  = t.get("status", "")
            file_   = t.get("file", "")
            comment = t.get("comment", "").replace("\n", " ").strip()[:250]
            thread_lines.append(
                f"[{status.upper()}] {os.path.basename(file_) if file_ else '(PR-level)'} | {comment}"
            )

    threads_text = "\n".join(thread_lines)

    prompt = f"""你是一位資深 Java Spring Boot 技術 Lead，正在分析 repo「{repo}」過去一年的 {stats['total_prs']} 個 PR review 紀錄。

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

請執行以下分析，輸出**繁體中文** Markdown 文件，格式如下：

---

# {repo} 團隊 Code Review 規則庫
> 從 {stats['total_prs']} 個 PR（{stats['total_threads']} 則 review 留言）自動提煉
> 生成日期：{{TODAY}}

## 📌 高頻問題規則（出現 3 次以上，應列為強制規範）

對每條規則：
- **規則**：一句話描述
- **出現次數**：N 次（佔 FIXED threads 的 X%）
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

列出最常被 review 留言的檔案，代表這些地方需要特別注意或重構。

---

分析原則：
1. 以 FIXED threads 為主要訊號（代表問題被確認且修正）
2. 相似意思的留言應合併歸類，不要重複列出
3. 避免過度泛化——保持規則和這個 repo 的實際程式碼習慣相關
4. WONTFIX 是寶貴資訊，代表這個團隊的風格選擇，不要評判
"""
    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate batch data and build Claude analysis prompt"
    )
    parser.add_argument("--input-dir",  metavar="DIR",
                        help="Directory containing batch_*.json files")
    parser.add_argument("--input-file", metavar="FILE",
                        help="Single batch JSON file")
    parser.add_argument("--stats-only", action="store_true",
                        help="Print stats only, skip analysis prompt")
    parser.add_argument("--config",     metavar="PATH",
                        help="Config file (default: ../config.json relative to scripts/)")
    args = parser.parse_args()

    if not args.input_dir and not args.input_file:
        parser.error("Provide --input-dir or --input-file")

    # Load config
    default_config = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )
    config_path = args.config or default_config
    config = {}
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)

    prs   = load_batches(input_dir=args.input_dir, input_file=args.input_file)
    stats = compute_stats(prs)

    if args.stats_only:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    # Print stats to stderr, prompt to stdout (so caller can pipe the prompt)
    sys.stderr.write(json.dumps({
        "total_prs":        stats["total_prs"],
        "prs_with_threads": stats["prs_with_threads"],
        "total_threads":    stats["total_threads"],
        "by_status":        stats["by_status"],
        "top_files":        stats["top_files"],
    }, ensure_ascii=False, indent=2) + "\n")

    prompt = build_analysis_prompt(prs, stats, config)
    print(prompt)


if __name__ == "__main__":
    main()
