#!/usr/bin/env python3
"""
install_skill.py — 安裝/更新/刪除單一技能到 Claude Code 和 Cline

用法：
  python install_skill.py --source <來源目錄> --skill-name <技能名稱> --action install
  python install_skill.py --skill-name <技能名稱> --action uninstall
  python install_skill.py --skill-name <技能名稱> --action check

跨平台：Windows / macOS / Linux 皆可執行
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime


def backup_dir(target: str) -> str:
    """備份目錄，回傳備份路徑"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{target}.bak.{timestamp}"
    shutil.copytree(target, backup_path)
    return backup_path


def do_install(source: str, skill_name: str, claude_dir: str, cline_dir: str) -> dict:
    """安裝或更新技能"""
    if not source or not os.path.isdir(source):
        return {"skill": skill_name, "action": "install", "error": f"來源目錄不存在 — {source}"}

    results = []

    # --- Claude Code ---
    claude_target = os.path.join(claude_dir, skill_name)
    os.makedirs(claude_dir, exist_ok=True)

    if os.path.isdir(claude_target):
        backup_dir(claude_target)
        shutil.rmtree(claude_target)
        action_text = "已更新"
    else:
        action_text = "已安裝"

    shutil.copytree(source, claude_target)
    results.append(f"Claude Code: {action_text} ({claude_target})")

    # --- Cline ---
    cline_target = os.path.join(cline_dir, skill_name)
    os.makedirs(cline_dir, exist_ok=True)

    if os.path.isdir(cline_target):
        backup_dir(cline_target)
        shutil.rmtree(cline_target)
        action_text = "已更新"
    else:
        action_text = "已安裝"

    shutil.copytree(source, cline_target)
    results.append(f"Cline: {action_text} ({cline_target})")

    return {"skill": skill_name, "action": "install", "results": results}


def do_uninstall(skill_name: str, claude_dir: str, cline_dir: str) -> dict:
    """刪除技能"""
    results = []

    claude_target = os.path.join(claude_dir, skill_name)
    if os.path.isdir(claude_target):
        shutil.rmtree(claude_target)
        # 清理備份
        parent = os.path.dirname(claude_target)
        for item in os.listdir(parent):
            if item.startswith(f"{skill_name}.bak."):
                shutil.rmtree(os.path.join(parent, item), ignore_errors=True)
        results.append(f"Claude Code: 已刪除 ({claude_target})")
    else:
        results.append("Claude Code: 未安裝，跳過")

    cline_target = os.path.join(cline_dir, skill_name)
    if os.path.isdir(cline_target):
        shutil.rmtree(cline_target)
        parent = os.path.dirname(cline_target)
        for item in os.listdir(parent):
            if item.startswith(f"{skill_name}.bak."):
                shutil.rmtree(os.path.join(parent, item), ignore_errors=True)
        results.append(f"Cline: 已刪除 ({cline_target})")
    else:
        results.append("Cline: 未安裝，跳過")

    return {"skill": skill_name, "action": "uninstall", "results": results}


def do_check(skill_name: str, claude_dir: str, cline_dir: str) -> dict:
    """檢查安裝狀態"""
    return {
        "skill": skill_name,
        "claude_installed": os.path.isdir(os.path.join(claude_dir, skill_name)),
        "cline_installed": os.path.isdir(os.path.join(cline_dir, skill_name)),
    }


def main():
    parser = argparse.ArgumentParser(description="安裝/更新/刪除單一技能")
    parser.add_argument("--source", default="", help="來源技能目錄路徑")
    parser.add_argument("--skill-name", required=True, help="技能名稱")
    parser.add_argument("--claude-dir", default=os.path.join(os.path.expanduser("~"), ".claude", "skills"))
    parser.add_argument("--cline-dir", default=os.path.join(os.path.expanduser("~"), ".cline", "rules"))
    parser.add_argument("--action", required=True, choices=["install", "uninstall", "check"])
    args = parser.parse_args()

    if args.action == "install":
        result = do_install(args.source, args.skill_name, args.claude_dir, args.cline_dir)
    elif args.action == "uninstall":
        result = do_uninstall(args.skill_name, args.claude_dir, args.cline_dir)
    else:
        result = do_check(args.skill_name, args.claude_dir, args.cline_dir)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
