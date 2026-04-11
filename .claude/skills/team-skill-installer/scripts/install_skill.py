#!/usr/bin/env python3
"""
install_skill.py — 安裝/更新/刪除單一技能到 ~/.claude/skills/

用法：
  python install_skill.py --source <來源目錄> --skill-name <技能名稱> --action install
  python install_skill.py --skill-name <技能名稱> --action uninstall
  python install_skill.py --skill-name <技能名稱> --action check

安裝目標：~/.claude/skills/<技能名稱>/
Claude Code 和 Cline 都會讀取此路徑，安裝一次兩邊都能用。

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
import json
import os
import shutil
from datetime import datetime

DEFAULT_SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "skills")


def backup_dir(target: str) -> str:
    """備份目錄，回傳備份路徑"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{target}.bak.{timestamp}"
    shutil.copytree(target, backup_path)
    return backup_path


def do_install(source: str, skill_name: str, skills_dir: str) -> dict:
    """安裝或更新技能"""
    if not source or not os.path.isdir(source):
        return {"skill": skill_name, "action": "install", "error": f"來源目錄不存在 — {source}"}

    target = os.path.join(skills_dir, skill_name)
    os.makedirs(skills_dir, exist_ok=True)

    if os.path.isdir(target):
        backup_dir(target)
        shutil.rmtree(target)
        action_text = "已更新"
    else:
        action_text = "已安裝"

    shutil.copytree(source, target)

    return {
        "skill": skill_name,
        "action": "install",
        "status": action_text,
        "path": target,
    }


def do_uninstall(skill_name: str, skills_dir: str) -> dict:
    """刪除技能"""
    target = os.path.join(skills_dir, skill_name)

    if os.path.isdir(target):
        shutil.rmtree(target)
        # 清理備份
        for item in os.listdir(skills_dir):
            if item.startswith(f"{skill_name}.bak."):
                shutil.rmtree(os.path.join(skills_dir, item), ignore_errors=True)
        return {"skill": skill_name, "action": "uninstall", "status": "已刪除", "path": target}
    else:
        return {"skill": skill_name, "action": "uninstall", "status": "未安裝，跳過"}


def do_check(skill_name: str, skills_dir: str) -> dict:
    """檢查安裝狀態"""
    target = os.path.join(skills_dir, skill_name)
    return {
        "skill": skill_name,
        "installed": os.path.isdir(target),
        "path": target if os.path.isdir(target) else None,
    }


def main():
    parser = argparse.ArgumentParser(description="安裝/更新/刪除單一技能到 ~/.claude/skills/")
    parser.add_argument("--source", default="", help="來源技能目錄路徑")
    parser.add_argument("--skill-name", required=True, help="技能名稱")
    parser.add_argument("--skills-dir", default=DEFAULT_SKILLS_DIR, help="安裝目標目錄 (預設 ~/.claude/skills)")
    parser.add_argument("--action", required=True, choices=["install", "uninstall", "check"])
    args = parser.parse_args()

    if args.action == "install":
        result = do_install(args.source, args.skill_name, args.skills_dir)
    elif args.action == "uninstall":
        result = do_uninstall(args.skill_name, args.skills_dir)
    else:
        result = do_check(args.skill_name, args.skills_dir)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
