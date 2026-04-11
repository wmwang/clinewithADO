#!/usr/bin/env python3
"""
install_superpowers.py — Superpowers 離線安裝

用法：
  python install_superpowers.py <superpowers-plugin-目錄路徑>

做兩件事：
1. Claude Code plugin 註冊（~/.claude/plugins/cache/ + installed_plugins.json）
2. 把每個 skill 打散放到 ~/.claude/skills/<skill-name>/（扁平結構）
   這樣 Claude Code 和 Cline 都能讀到（Cline 只讀第一層）

跨平台：Windows / macOS / Linux 皆可執行，只用 Python 標準庫
"""

import io
import sys

# Windows 預設編碼是 cp950/cp936，中文會亂碼，強制 UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
import os
import shutil
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


def install_plugin(source_dir: str, version: str):
    """安裝到 Claude Code 的 plugin cache 並註冊"""
    home = os.path.expanduser("~")
    plugins_dir = os.path.join(home, ".claude", "plugins")
    cache_dir = os.path.join(plugins_dir, "cache", "claude-plugins-official", "superpowers", version)
    installed_json = os.path.join(plugins_dir, "installed_plugins.json")

    print("\n[1/2] Claude Code plugin 註冊中...")

    # 複製到 cache
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    shutil.copytree(source_dir, cache_dir)
    print(f"  複製到 {cache_dir}")

    # 註冊到 installed_plugins.json
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
    print("  完成！重啟 Claude Code 即可使用")


def install_skills_flat(source_dir: str):
    """把每個 skill 打散放到 ~/.claude/skills/ 根目錄下（扁平結構）

    Cline 只讀 ~/.claude/skills/ 的第一層子目錄，
    所以不能把 14 個 skill 包在 superpowers/ 下面，
    必須各自獨立為 ~/.claude/skills/<skill-name>/
    """
    home = os.path.expanduser("~")
    skills_dir = os.path.join(home, ".claude", "skills")
    skills_src = os.path.join(source_dir, "skills")

    if not os.path.isdir(skills_src):
        print("\n[2/2] 找不到 skills/ 目錄，跳過")
        return

    print("\n[2/2] 安裝 skills 到 ~/.claude/skills/（扁平結構）...")

    installed = []
    for skill_name in sorted(os.listdir(skills_src)):
        src_path = os.path.join(skills_src, skill_name)
        if not os.path.isdir(src_path):
            continue

        # 加上 sp- prefix 避免跟其他 skill 撞名，同時方便辨識來源
        target_name = f"sp-{skill_name}"
        target_path = os.path.join(skills_dir, target_name)

        if os.path.exists(target_path):
            shutil.rmtree(target_path)

        shutil.copytree(src_path, target_path)
        installed.append(target_name)

    # 複製使用指南到 ~/.claude/skills/sp-superpowers-guide/
    claude_md = os.path.join(source_dir, "CLAUDE.md")
    if os.path.isfile(claude_md):
        guide_dir = os.path.join(skills_dir, "sp-superpowers-guide")
        os.makedirs(guide_dir, exist_ok=True)
        shutil.copy2(claude_md, os.path.join(guide_dir, "SKILL.md"))
        installed.append("sp-superpowers-guide")

    print(f"  已安裝 {len(installed)} 個 skill：")
    for name in installed:
        print(f"    ~/.claude/skills/{name}/")

    # 清理舊的巢狀結構（如果存在）
    old_nested = os.path.join(skills_dir, "superpowers")
    if os.path.isdir(old_nested):
        shutil.rmtree(old_nested)
        print("\n  已清理舊的巢狀結構 (~/.claude/skills/superpowers/)")


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

    install_plugin(source_dir, version)
    install_skills_flat(source_dir)

    print()
    print("=" * 40)
    print(f"Superpowers v{version} 安裝完成！")
    print("Claude Code: 透過 plugin 機制載入（superpowers: prefix）")
    print("Cline: 透過 ~/.claude/skills/sp-*/ 載入（扁平結構）")


if __name__ == "__main__":
    main()
