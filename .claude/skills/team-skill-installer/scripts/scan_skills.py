#!/usr/bin/env python3
"""
scan_skills.py — 掃描 Skills/ 目錄，輸出技能清單 JSON

用法：
  python scan_skills.py <Skills目錄路徑> [--check-installed] [--installed-dir <path>]

安裝目標：~/.claude/skills/（Claude Code 和 Cline 共用）

跨平台：Windows / macOS / Linux 皆可執行
"""

import io
import sys

# Windows 預設編碼是 cp950/cp936，中文會亂碼，強制 UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import os

# 不需要對外安裝的技能
EXCLUDE_LIST = {"team-skill-installer", "skill-manual-writer-workspace", "superpowers-plugin"}

CLAUDE_SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "skills")
CLINE_SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".cline", "skills")


def dir_hash(directory: str) -> str:
    """計算目錄中所有關鍵檔案的 hash（用於偵測變更）"""
    extensions = {".md", ".sh", ".py", ".json"}
    h = hashlib.md5()
    try:
        for root, _, files in sorted(os.walk(directory)):
            for fname in sorted(files):
                if os.path.splitext(fname)[1] in extensions:
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "rb") as f:
                            h.update(f.read())
                    except OSError:
                        pass
    except OSError:
        return "unknown"
    return h.hexdigest()


def get_description(skill_file: str) -> str:
    """從 SKILL.md 的 YAML frontmatter 中抓取 description 第一行"""
    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return ""

    in_frontmatter = False
    found_desc = False

    for line in lines:
        stripped = line.strip()

        if stripped == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break  # frontmatter 結束

        if not in_frontmatter:
            continue

        if found_desc:
            # 在 description 的續行中（縮排的行）
            if line[0] in (" ", "\t"):
                text = stripped
                if text:
                    return text
            else:
                break  # 遇到下一個 key，description 沒有值
            continue

        if stripped.startswith("description:"):
            found_desc = True
            value = stripped[len("description:"):].strip()
            # 移除 YAML 多行指示符 |、>、|+、|- 等
            if value in ("|", ">", "|+", "|-", ">+", ">-", ""):
                continue
            # 移除前後引號
            if len(value) >= 2 and value[0] in ("'", '"') and value[-1] == value[0]:
                value = value[1:-1]
            if value:
                return value

    return ""


def check_install_status(skill_name: str, source_dir: str, claude_dir: str, cline_dir: str) -> dict:
    """檢查技能在兩個目錄的安裝狀態"""
    source_hash = dir_hash(source_dir)
    result = {}

    for label, installed_dir in [("claude", claude_dir), ("cline", cline_dir)]:
        target = os.path.join(installed_dir, skill_name)
        if not os.path.isdir(target):
            result[label] = "not_installed"
        elif source_hash == dir_hash(target):
            result[label] = "up_to_date"
        else:
            result[label] = "needs_update"

    # 整體狀態：任一個未安裝就算未安裝，任一個需更新就算需更新
    if any(v == "not_installed" for v in result.values()):
        result["overall"] = "not_installed"
    elif any(v == "needs_update" for v in result.values()):
        result["overall"] = "needs_update"
    else:
        result["overall"] = "up_to_date"

    return result


def count_sub_skills(skill_dir: str) -> int:
    """計算子技能數量（子目錄中的 SKILL.md）"""
    count = 0
    for root, _, files in os.walk(skill_dir):
        if root == skill_dir:
            continue
        if "SKILL.md" in files:
            count += 1
    return count


def scan(skills_dir: str, check_installed: bool, claude_dir: str, cline_dir: str) -> list:
    """掃描 Skills/ 目錄，回傳技能清單"""
    results = []

    if not os.path.isdir(skills_dir):
        print(f"錯誤：找不到目錄 — {skills_dir}", file=sys.stderr)
        sys.exit(1)

    for entry in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, entry)
        if not os.path.isdir(skill_path):
            continue
        if entry.startswith("."):
            continue
        if entry in EXCLUDE_LIST:
            continue

        skill_file = os.path.join(skill_path, "SKILL.md")
        is_bundle = False

        if os.path.isfile(skill_file):
            description = get_description(skill_file)
        else:
            sub_count = count_sub_skills(skill_path)
            if sub_count == 0:
                continue
            is_bundle = True
            description = f"套件型技能（包含 {sub_count} 個子指令）"

        # 安裝狀態
        status = "not_installed"
        if check_installed:
            status_detail = check_install_status(entry, skill_path, claude_dir, cline_dir)
            status = status_detail["overall"]

        results.append({
            "name": entry,
            "description": description,
            "is_bundle": is_bundle,
            "path": skill_path,
            "status": status,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="掃描 Skills/ 目錄，輸出技能清單 JSON")
    parser.add_argument("source_dir", help="Skills 來源目錄路徑（repo 中的 Skills/）")
    parser.add_argument("--check-installed", action="store_true", help="檢查安裝狀態")
    parser.add_argument("--claude-dir", default=CLAUDE_SKILLS_DIR,
                        help="Claude Code skills 目錄 (預設 ~/.claude/skills)")
    parser.add_argument("--cline-dir", default=CLINE_SKILLS_DIR,
                        help="Cline skills 目錄 (預設 ~/.cline/skills)")
    args = parser.parse_args()

    results = scan(args.source_dir, args.check_installed, args.claude_dir, args.cline_dir)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
