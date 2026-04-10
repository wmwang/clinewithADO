#!/usr/bin/env python3
"""
install_superpowers.py — Superpowers 離線安裝（同時支援 Claude Code 和 Cline）

用法：
  python install_superpowers.py <superpowers-plugin-目錄路徑>

不需要網路連線，直接從 repo 內建的 plugin 包安裝。
跨平台：Windows / macOS / Linux 皆可執行
"""

import json
import os
import shutil
import sys
from datetime import datetime, timezone


def get_version(source_dir: str) -> str:
    """讀取 plugin 版本號"""
    for json_file in [
        os.path.join(source_dir, ".claude-plugin", "plugin.json"),
        os.path.join(source_dir, "package.json"),
    ]:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("version", "unknown")
        except (OSError, json.JSONDecodeError):
            continue
    return "unknown"


def install_claude_code(source_dir: str, version: str):
    """安裝到 Claude Code 的 plugin cache 並註冊"""
    home = os.path.expanduser("~")
    plugins_dir = os.path.join(home, ".claude", "plugins")
    cache_dir = os.path.join(plugins_dir, "cache", "claude-plugins-official", "superpowers", version)
    installed_json = os.path.join(plugins_dir, "installed_plugins.json")

    print("\n[Claude Code] 安裝中...")

    # 1. 複製到 cache
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    shutil.copytree(source_dir, cache_dir)
    print(f"  已複製到 {cache_dir}")

    # 2. 註冊到 installed_plugins.json
    os.makedirs(plugins_dir, exist_ok=True)

    if os.path.isfile(installed_json):
        with open(installed_json, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"version": 2, "plugins": {}}
    else:
        data = {"version": 2, "plugins": {}}

    if "plugins" not in data:
        data["plugins"] = {}

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    key = "superpowers@claude-plugins-official"
    entry = {
        "scope": "user",
        "installPath": cache_dir,
        "version": version,
        "installedAt": timestamp,
        "lastUpdated": timestamp,
    }

    if key in data["plugins"]:
        entries = data["plugins"][key]
        updated = False
        for i, e in enumerate(entries):
            if e.get("scope") == "user":
                entries[i] = entry
                updated = True
                break
        if not updated:
            entries.append(entry)
    else:
        data["plugins"][key] = [entry]

    with open(installed_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("  已註冊到 installed_plugins.json")
    print("  [Claude Code] 完成！重啟 Claude Code 即可使用")


def install_cline(source_dir: str):
    """安裝到 Cline 的全域規則目錄"""
    home = os.path.expanduser("~")
    cline_rules_dir = os.path.join(home, ".cline", "rules", "superpowers")

    print("\n[Cline] 安裝中...")

    # 複製 skills 目錄
    skills_src = os.path.join(source_dir, "skills")
    if os.path.isdir(skills_src):
        if os.path.exists(cline_rules_dir):
            shutil.rmtree(cline_rules_dir)
        shutil.copytree(skills_src, cline_rules_dir)

        skill_count = sum(
            1 for root, _, files in os.walk(cline_rules_dir) if "SKILL.md" in files
        )
        print(f"  已複製 {skill_count} 個技能規則到 {cline_rules_dir}")

    # 複製使用指南
    claude_md = os.path.join(source_dir, "CLAUDE.md")
    if os.path.isfile(claude_md):
        os.makedirs(cline_rules_dir, exist_ok=True)
        shutil.copy2(claude_md, os.path.join(cline_rules_dir, "superpowers-guide.md"))
        print("  已複製使用指南")

    print("  [Cline] 完成！")
    print()
    print("  提醒：請在 VS Code 的 Cline 設定中確認全域規則路徑包含：")
    home_display = "~" if os.name != "nt" else "%USERPROFILE%"
    print(f"    {home_display}/.cline/rules/")


def list_skills(source_dir: str):
    """列出所有包含的技能"""
    skills_dir = os.path.join(source_dir, "skills")
    if not os.path.isdir(skills_dir):
        return

    print("\n包含的技能：")
    for entry in sorted(os.listdir(skills_dir)):
        if os.path.isdir(os.path.join(skills_dir, entry)):
            print(f"  - {entry}")


def main():
    if len(sys.argv) < 2:
        print("用法: python install_superpowers.py <superpowers-plugin-目錄路徑>")
        sys.exit(1)

    source_dir = sys.argv[1]

    if not os.path.isdir(source_dir):
        print(f"錯誤：找不到 Superpowers 來源目錄 — {source_dir}")
        print()
        print("可能原因：")
        print("  1. repo 還沒有打包 superpowers（請聯繫管理員）")
        print("  2. 路徑打錯了")
        print()
        print("備用方案（需要網路）：")
        print("  Claude Code: claude plugins install superpowers@claude-plugins-official")
        sys.exit(1)

    version = get_version(source_dir)
    print(f"Superpowers 離線安裝 (v{version})")
    print("=" * 40)

    install_claude_code(source_dir, version)
    install_cline(source_dir)

    print()
    print("=" * 40)
    print(f"Superpowers v{version} 安裝完成！")
    list_skills(source_dir)


if __name__ == "__main__":
    main()
