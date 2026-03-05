#!/usr/bin/env bash
# =============================================================================
# AI Assets Manager
# 公司 AI 共同資產一鍵安裝工具
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/ai-assets"

# ---------------------------------------------------------------------------
# Colors & formatting
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
SELECTED_PACKAGES=()
SELECTED_ENGINE=""
SELECTED_SCOPE=""
TARGET_DIR="$(pwd)"
INSTALL_LOG=()

# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------
print_banner() {
  echo ""
  echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}${BOLD}║         AI Assets Manager  v1.0                      ║${NC}"
  echo -e "${CYAN}${BOLD}║         公司 AI 工具一鍵安裝程式                     ║${NC}"
  echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════╝${NC}"
  echo ""
}

print_step() {
  echo ""
  echo -e "${BLUE}${BOLD}▶ $1${NC}"
  echo -e "${DIM}$(printf '─%.0s' {1..54})${NC}"
}

print_success() {
  echo -e "  ${GREEN}✓${NC} $1"
}

print_info() {
  echo -e "  ${CYAN}ℹ${NC} $1"
}

print_warn() {
  echo -e "  ${YELLOW}⚠${NC} $1"
}

print_error() {
  echo -e "  ${RED}✗${NC} $1"
}

print_item() {
  echo -e "  ${DIM}•${NC} $1"
}

# ---------------------------------------------------------------------------
# Multi-select menu
# Returns selected indices in REPLY array
# Usage: multiselect "title" "opt1" "opt2" ...
# ---------------------------------------------------------------------------
multiselect() {
  local title="$1"
  shift
  local options=("$@")
  local count=${#options[@]}
  local selected=()

  # Initialize all as unselected
  for ((i=0; i<count; i++)); do
    selected[$i]=false
  done

  echo -e "${BOLD}$title${NC}"
  echo -e "${DIM}(輸入數字切換選取，按 Enter 確認，輸入 a 全選，輸入 0 取消)${NC}"
  echo ""

  while true; do
    # Display options
    for ((i=0; i<count; i++)); do
      local num=$((i+1))
      if [ "${selected[$i]}" = "true" ]; then
        echo -e "  ${GREEN}[✓] $num. ${options[$i]}${NC}"
      else
        echo -e "  ${DIM}[ ] $num. ${options[$i]}${NC}"
      fi
    done
    echo ""
    echo -e -n "${BOLD}選擇 (數字/a/Enter): ${NC}"
    read -r input

    if [ -z "$input" ]; then
      # Check at least one selected
      local any_selected=false
      for ((i=0; i<count; i++)); do
        if [ "${selected[$i]}" = "true" ]; then
          any_selected=true
          break
        fi
      done
      if [ "$any_selected" = "true" ]; then
        break
      else
        print_warn "請至少選擇一個選項"
        echo ""
      fi
    elif [ "$input" = "a" ] || [ "$input" = "A" ]; then
      for ((i=0; i<count; i++)); do
        selected[$i]=true
      done
      echo ""
    elif [ "$input" = "0" ]; then
      echo -e "${YELLOW}已取消${NC}"
      exit 0
    elif [[ "$input" =~ ^[0-9]+$ ]] && [ "$input" -ge 1 ] && [ "$input" -le "$count" ]; then
      local idx=$((input-1))
      if [ "${selected[$idx]}" = "true" ]; then
        selected[$idx]=false
      else
        selected[$idx]=true
      fi
      echo ""
    else
      print_warn "請輸入有效的數字 (1-$count)、a 全選、或 Enter 確認"
      echo ""
    fi

    # Move cursor up to redraw
    for ((i=0; i<count+3; i++)); do
      tput cuu1 2>/dev/null || echo -ne "\033[A"
    done
    tput el 2>/dev/null || true
  done

  # Build result
  MULTISELECT_RESULT=()
  for ((i=0; i<count; i++)); do
    if [ "${selected[$i]}" = "true" ]; then
      MULTISELECT_RESULT+=("${options[$i]}")
    fi
  done
}

# Single-select menu
# Usage: singleselect "title" "opt1" "opt2" ...
singleselect() {
  local title="$1"
  shift
  local options=("$@")
  local count=${#options[@]}

  echo -e "${BOLD}$title${NC}"
  echo ""

  for ((i=0; i<count; i++)); do
    local num=$((i+1))
    echo -e "  ${CYAN}$num.${NC} ${options[$i]}"
  done
  echo ""

  while true; do
    echo -e -n "${BOLD}請選擇 (1-$count): ${NC}"
    read -r input
    if [[ "$input" =~ ^[0-9]+$ ]] && [ "$input" -ge 1 ] && [ "$input" -le "$count" ]; then
      local idx=$((input-1))
      SINGLESELECT_RESULT="${options[$idx]}"
      return 0
    else
      print_warn "請輸入有效的數字 (1-$count)"
    fi
  done
}

# ---------------------------------------------------------------------------
# Step 1: Select packages
# ---------------------------------------------------------------------------
ask_packages() {
  print_step "Step 1 / 3 — 選擇要安裝的工具套件"

  local pkg_options=(
    "Superpower Skills  (brainstorm / TDD / debugging / planning)"
    "BMAD Method        (AI 產品開發角色：analyst / PM / architect / dev / SM)"
    "OpenSpec           (Spec-driven 開發：proposal → specs → design → tasks)"
    "Spec Kit           (GitHub spec-driven 開發框架)"
  )

  multiselect "請選擇要安裝的套件：" "${pkg_options[@]}"

  SELECTED_PACKAGES=()
  for item in "${MULTISELECT_RESULT[@]}"; do
    case "$item" in
      Superpower*) SELECTED_PACKAGES+=("superpower") ;;
      BMAD*)       SELECTED_PACKAGES+=("bmad-method") ;;
      OpenSpec*)   SELECTED_PACKAGES+=("openspec") ;;
      Spec\ Kit*)  SELECTED_PACKAGES+=("spec-kit") ;;
    esac
  done

  echo ""
  print_info "已選擇：${SELECTED_PACKAGES[*]}"
}

# ---------------------------------------------------------------------------
# Step 2: Select engine
# ---------------------------------------------------------------------------
ask_engine() {
  print_step "Step 2 / 3 — 選擇 AI Coding 引擎"

  local engine_options=(
    "Cline     (VS Code 擴充套件)"
    "OpenCode  (CLI 工具)"
    "兩者都安裝"
  )

  singleselect "請選擇您使用的 AI Coding 引擎：" "${engine_options[@]}"

  case "$SINGLESELECT_RESULT" in
    Cline*)    SELECTED_ENGINE="cline" ;;
    OpenCode*) SELECTED_ENGINE="opencode" ;;
    兩者*)     SELECTED_ENGINE="both" ;;
  esac

  echo ""
  print_info "已選擇：$SELECTED_ENGINE"
}

# ---------------------------------------------------------------------------
# Step 3: Select scope
# ---------------------------------------------------------------------------
ask_scope() {
  print_step "Step 3 / 3 — 選擇安裝範圍"

  local scope_options=(
    "專案 (Project)  — 安裝到當前目錄 (只對此專案生效)"
    "全域 (Global)   — 安裝到 HOME 目錄 (對所有專案生效)"
  )

  # Warn about project-only packages
  local project_only_selected=false
  for pkg in "${SELECTED_PACKAGES[@]}"; do
    if [ "$pkg" = "openspec" ] || [ "$pkg" = "spec-kit" ]; then
      project_only_selected=true
      break
    fi
  done

  if [ "$project_only_selected" = "true" ]; then
    print_warn "注意：OpenSpec / Spec Kit 為專案層級工具，全域安裝時仍會安裝到當前目錄"
    echo ""
  fi

  singleselect "請選擇安裝範圍：" "${scope_options[@]}"

  case "$SINGLESELECT_RESULT" in
    專案*) SELECTED_SCOPE="project" ;;
    全域*) SELECTED_SCOPE="global" ;;
  esac

  echo ""
  print_info "已選擇：$SELECTED_SCOPE"
}

# ---------------------------------------------------------------------------
# Confirm
# ---------------------------------------------------------------------------
confirm_install() {
  echo ""
  echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}║  安裝確認                                            ║${NC}"
  echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo -e "  ${BOLD}套件：${NC}   ${GREEN}${SELECTED_PACKAGES[*]}${NC}"
  echo -e "  ${BOLD}引擎：${NC}   ${GREEN}${SELECTED_ENGINE}${NC}"
  echo -e "  ${BOLD}範圍：${NC}   ${GREEN}${SELECTED_SCOPE}${NC}"

  if [ "$SELECTED_SCOPE" = "project" ]; then
    echo -e "  ${BOLD}目錄：${NC}   ${GREEN}${TARGET_DIR}${NC}"
  fi
  echo ""

  echo -e -n "${BOLD}確認安裝？[y/N]: ${NC}"
  read -r confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消${NC}"
    exit 0
  fi
}

# ---------------------------------------------------------------------------
# Install helpers
# ---------------------------------------------------------------------------
copy_dir() {
  local src="$1"
  local dst="$2"
  local desc="$3"

  mkdir -p "$dst"
  cp -r "$src/." "$dst/"
  print_success "$desc → $(short_path "$dst")"
  INSTALL_LOG+=("$desc → $dst")
}

copy_file() {
  local src="$1"
  local dst_dir="$2"
  local desc="$3"

  mkdir -p "$dst_dir"
  cp "$src" "$dst_dir/"
  print_success "$desc"
  INSTALL_LOG+=("$desc")
}

short_path() {
  echo "$1" | sed "s|$HOME|~|g" | sed "s|$(pwd)|./|g"
}

# Update OpenCode config to add instruction files
update_opencode_config() {
  local config_file="$1"
  local instruction_path="$2"

  mkdir -p "$(dirname "$config_file")"

  if [ ! -f "$config_file" ]; then
    echo '{}' > "$config_file"
  fi

  # Use python3 if available, otherwise use node, otherwise manual
  if command -v python3 &>/dev/null; then
    python3 - <<PYEOF
import json, sys

config_file = "$config_file"
instruction_path = "$instruction_path"

with open(config_file, 'r') as f:
    try:
        config = json.load(f)
    except:
        config = {}

if 'instructions' not in config:
    config['instructions'] = []

if instruction_path not in config['instructions']:
    config['instructions'].append(instruction_path)

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    f.write('\n')

print("updated")
PYEOF
  elif command -v node &>/dev/null; then
    node - <<NJEOF
const fs = require('fs');
const configFile = "$config_file";
const instructionPath = "$instruction_path";

let config = {};
try { config = JSON.parse(fs.readFileSync(configFile, 'utf8')); } catch(e) {}

if (!config.instructions) config.instructions = [];
if (!config.instructions.includes(instructionPath)) {
    config.instructions.push(instructionPath);
}

fs.writeFileSync(configFile, JSON.stringify(config, null, 2) + '\n');
console.log('updated');
NJEOF
  else
    print_warn "無法自動更新 $config_file，請手動添加："
    print_warn "  \"instructions\": [\"$instruction_path\"]"
  fi
}

# ---------------------------------------------------------------------------
# Package installers
# ---------------------------------------------------------------------------

install_superpower() {
  local engine="$1"
  local scope="$2"

  echo ""
  echo -e "  ${MAGENTA}▸ Superpower Skills${NC}"

  local src="$ASSETS_DIR/superpower/skills"

  if [ "$engine" = "cline" ] || [ "$engine" = "both" ]; then
    if [ "$scope" = "project" ]; then
      local dst="$TARGET_DIR/.clinerules/superpower-skills"
      copy_dir "$src" "$dst" "Cline (project): Superpower Skills"
    else
      local dst="$HOME/.cline/rules/superpower-skills"
      copy_dir "$src" "$dst" "Cline (global): Superpower Skills"
      print_info "請在 VS Code Cline 設定中加入以下路徑："
      print_info "  Settings → Cline → Custom Instructions → 參考 $dst"
    fi
  fi

  if [ "$engine" = "opencode" ] || [ "$engine" = "both" ]; then
    if [ "$scope" = "project" ]; then
      local dst="$TARGET_DIR/.opencode/command/superpower"
      # OpenCode commands are markdown files - flatten skill directories
      # Note: OpenCode uses .opencode/command/ (singular) per official spec
      mkdir -p "$dst"
      find "$src" -name "SKILL.md" | while read -r skill_file; do
        local skill_name
        skill_name=$(basename "$(dirname "$skill_file")")
        local category
        category=$(basename "$(dirname "$(dirname "$skill_file")")")
        cp "$skill_file" "$dst/${category}-${skill_name}.md"
      done
      print_success "OpenCode (project): Superpower Skills → $(short_path "$dst")"
      INSTALL_LOG+=("OpenCode (project): Superpower Skills → $dst")
    else
      local dst="$HOME/.config/opencode/command/superpower"
      mkdir -p "$dst"
      find "$src" -name "SKILL.md" | while read -r skill_file; do
        local skill_name
        skill_name=$(basename "$(dirname "$skill_file")")
        local category
        category=$(basename "$(dirname "$(dirname "$skill_file")")")
        cp "$skill_file" "$dst/${category}-${skill_name}.md"
      done
      print_success "OpenCode (global): Superpower Skills → $(short_path "$dst")"
      INSTALL_LOG+=("OpenCode (global): Superpower Skills → $dst")
    fi
  fi
}

install_bmad() {
  local engine="$1"
  local scope="$2"

  echo ""
  echo -e "  ${MAGENTA}▸ BMAD Method${NC}"

  local src="$ASSETS_DIR/bmad-method/.bmad-core"

  if [ "$engine" = "cline" ] || [ "$engine" = "both" ]; then
    if [ "$scope" = "project" ]; then
      local dst="$TARGET_DIR/.clinerules/bmad"
      copy_dir "$src/agents" "$dst/agents" "Cline (project): BMAD agents"
      # Create a loader file for .clinerules
      cat > "$TARGET_DIR/.clinerules/bmad-loader.md" <<'BMADEOF'
# BMAD Method - Agent Loader

This project uses the BMAD Method agents. Load agents from `.clinerules/bmad/agents/`.

## Available Agents

- **Mary** (analyst.md) - Business Analyst
- **John** (pm.md) - Product Manager
- **Winston** (architect.md) - Software Architect
- **Amelia** (dev.md) - Developer
- **Bob** (sm.md) - Scrum Master

## Usage

Invoke an agent by name in your prompt. The agent's instructions are in the corresponding file.

Example: "Mary, help me write requirements for the login feature."
BMADEOF
      print_success "Cline (project): BMAD loader → $(short_path "$TARGET_DIR/.clinerules/bmad-loader.md")"
    else
      local dst="$HOME/.cline/rules/bmad"
      copy_dir "$src/agents" "$dst/agents" "Cline (global): BMAD agents"
      print_info "請將 $dst 加入 VS Code Cline 設定的 Custom Instructions"
    fi
  fi

  if [ "$engine" = "opencode" ] || [ "$engine" = "both" ]; then
    if [ "$scope" = "project" ]; then
      local dst="$TARGET_DIR/.opencode/command/bmad"
      copy_dir "$src/agents" "$dst" "OpenCode (project): BMAD agents"
    else
      local dst="$HOME/.config/opencode/command/bmad"
      copy_dir "$src/agents" "$dst" "OpenCode (global): BMAD agents"
    fi
  fi
}

install_openspec() {
  local engine="$1"
  local scope="$2"  # openspec is always project-level

  echo ""
  echo -e "  ${MAGENTA}▸ OpenSpec${NC}"

  local src="$ASSETS_DIR/openspec"

  # Always install to project directory
  local dst="$TARGET_DIR"

  # Copy AGENTS.md
  cp "$src/AGENTS.md" "$dst/AGENTS.md"
  print_success "OpenSpec: AGENTS.md → $(short_path "$dst/AGENTS.md")"

  # Create openspec directory structure
  mkdir -p "$dst/openspec/changes"
  mkdir -p "$dst/openspec/specs"
  touch "$dst/openspec/changes/.gitkeep"
  touch "$dst/openspec/specs/.gitkeep"

  # Copy templates
  local tmpl_dst="$dst/openspec/.templates"
  mkdir -p "$tmpl_dst"
  cp -r "$src/schemas/spec-driven/templates/." "$tmpl_dst/"
  print_success "OpenSpec: 目錄結構 → $(short_path "$dst/openspec/")"
  print_success "OpenSpec: Templates → $(short_path "$tmpl_dst")"
  INSTALL_LOG+=("OpenSpec → $dst/openspec/")

  # For OpenCode, also add command stubs
  if [ "$engine" = "opencode" ] || [ "$engine" = "both" ]; then
    mkdir -p "$dst/.opencode/command"
    cat > "$dst/.opencode/command/opsx-propose.md" <<'EOMD'
---
description: "OpenSpec: Start a new feature with proposal → specs → design → tasks"
---

# /opsx:propose

Start a new OpenSpec change for $ARGUMENTS.

Create the folder `openspec/changes/$ARGUMENTS/` and generate:
1. `proposal.md` - why and what changes (use template from `openspec/.templates/proposal.md`)
2. `specs/<capability>/spec.md` - requirements (use template from `openspec/.templates/spec.md`)
3. `design.md` - technical approach (use template from `openspec/.templates/design.md`)
4. `tasks.md` - implementation checklist (use template from `openspec/.templates/tasks.md`)

Follow the instructions in `AGENTS.md` for the complete workflow.
EOMD
    print_success "OpenCode: opsx-propose command → $(short_path "$dst/.opencode/command/opsx-propose.md")"
  fi
}

install_speckit() {
  local engine="$1"
  local scope="$2"  # spec-kit is always project-level

  echo ""
  echo -e "  ${MAGENTA}▸ Spec Kit${NC}"

  local src="$ASSETS_DIR/spec-kit"
  local dst="$TARGET_DIR"

  # Create .specify directory
  mkdir -p "$dst/.specify/memory"
  mkdir -p "$dst/.specify/templates/commands"

  # Copy constitution template
  cp "$src/templates/constitution-template.md" "$dst/.specify/memory/constitution.md"
  print_success "Spec Kit: constitution → $(short_path "$dst/.specify/memory/constitution.md")"

  # Copy templates
  cp "$src/templates/spec-template.md"         "$dst/.specify/templates/"
  cp "$src/templates/plan-template.md"         "$dst/.specify/templates/"
  cp "$src/templates/tasks-template.md"        "$dst/.specify/templates/"
  cp "$src/templates/constitution-template.md" "$dst/.specify/templates/"
  cp "$src/templates/commands/"*.md            "$dst/.specify/templates/commands/" 2>/dev/null || true
  print_success "Spec Kit: templates → $(short_path "$dst/.specify/templates/")"
  INSTALL_LOG+=("Spec Kit → $dst/.specify/")

  # For Cline: create command stubs in .clinerules
  if [ "$engine" = "cline" ] || [ "$engine" = "both" ]; then
    mkdir -p "$dst/.clinerules/speckit-commands"
    cp "$src/templates/commands/"*.md "$dst/.clinerules/speckit-commands/" 2>/dev/null || true
    print_success "Cline: speckit commands → $(short_path "$dst/.clinerules/speckit-commands/")"
  fi

  # For OpenCode: create commands
  if [ "$engine" = "opencode" ] || [ "$engine" = "both" ]; then
    mkdir -p "$dst/.opencode/command"
    cp "$src/templates/commands/"*.md "$dst/.opencode/command/" 2>/dev/null || true
    print_success "OpenCode: speckit commands → $(short_path "$dst/.opencode/command/")"
  fi
}

# ---------------------------------------------------------------------------
# Main install logic
# ---------------------------------------------------------------------------
do_install() {
  echo ""
  echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}║  安裝中...                                           ║${NC}"
  echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${NC}"

  local engines=()
  case "$SELECTED_ENGINE" in
    cline)    engines=("cline") ;;
    opencode) engines=("opencode") ;;
    both)     engines=("both") ;;
  esac

  for pkg in "${SELECTED_PACKAGES[@]}"; do
    case "$pkg" in
      superpower) install_superpower "${engines[0]}" "$SELECTED_SCOPE" ;;
      bmad-method) install_bmad "${engines[0]}" "$SELECTED_SCOPE" ;;
      openspec)   install_openspec "${engines[0]}" "$SELECTED_SCOPE" ;;
      spec-kit)   install_speckit "${engines[0]}" "$SELECTED_SCOPE" ;;
    esac
  done
}

# ---------------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------------
print_summary() {
  echo ""
  echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}${BOLD}║  ✓ 安裝完成！                                        ║${NC}"
  echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════╝${NC}"
  echo ""

  if [ ${#INSTALL_LOG[@]} -gt 0 ]; then
    echo -e "${BOLD}已安裝的項目：${NC}"
    for item in "${INSTALL_LOG[@]}"; do
      print_item "$item"
    done
    echo ""
  fi

  # Engine-specific next steps
  echo -e "${BOLD}後續步驟：${NC}"

  case "$SELECTED_ENGINE" in
    cline|both)
      if [ "$SELECTED_SCOPE" = "project" ]; then
        print_info "Cline: 開啟 VS Code，Cline 會自動讀取 .clinerules/ 目錄"
      else
        print_info "Cline: 在 VS Code 設定中，將以下路徑加入 Cline Custom Instructions："
        print_info "  File → Preferences → Settings → 搜尋 'Cline Custom Instructions'"
        if echo "${SELECTED_PACKAGES[@]}" | grep -q "superpower"; then
          print_item "~/.cline/rules/superpower-skills"
        fi
        if echo "${SELECTED_PACKAGES[@]}" | grep -q "bmad"; then
          print_item "~/.cline/rules/bmad"
        fi
      fi
      ;;
  esac

  case "$SELECTED_ENGINE" in
    opencode|both)
      if [ "$SELECTED_SCOPE" = "global" ]; then
        print_info "OpenCode: 全域命令已安裝到 ~/.config/opencode/command/"
        print_info "  啟動 opencode 即可使用"
      else
        print_info "OpenCode: 專案命令已安裝到 .opencode/command/"
        print_info "  在此目錄執行 opencode 即可使用"
      fi
      ;;
  esac

  echo ""

  # Package-specific usage hints
  for pkg in "${SELECTED_PACKAGES[@]}"; do
    case "$pkg" in
      superpower)
        echo -e "  ${CYAN}Superpower Skills:${NC}"
        print_item "在對話中說 '用 Brainstorming skill 來分析這個問題'"
        print_item "說 '用 TDD skill 來實作這個功能'"
        echo ""
        ;;
      bmad-method)
        echo -e "  ${CYAN}BMAD Method:${NC}"
        print_item "呼叫角色名稱：'Mary, 幫我寫這個功能的需求'"
        print_item "'Winston, 設計這個系統的架構'"
        echo ""
        ;;
      openspec)
        echo -e "  ${CYAN}OpenSpec:${NC}"
        print_item "使用 /opsx:propose <功能名稱> 開始一個新功能"
        print_item "使用 /opsx:apply 實作待辦任務"
        echo ""
        ;;
      spec-kit)
        echo -e "  ${CYAN}Spec Kit:${NC}"
        print_item "使用 /speckit.specify 建立規格"
        print_item "使用 /speckit.plan 建立技術計畫"
        print_item "使用 /speckit.tasks 產生任務清單"
        echo ""
        ;;
    esac
  done

  echo -e "${DIM}完整文件請參閱 ai-assets/ 各套件的 README.md${NC}"
  echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  # Check we're running from the right place
  if [ ! -d "$ASSETS_DIR" ]; then
    echo -e "${RED}Error: 找不到 ai-assets/ 目錄${NC}"
    echo -e "請確認您在 repo 根目錄執行此腳本"
    exit 1
  fi

  print_banner
  ask_packages
  ask_engine
  ask_scope
  confirm_install
  do_install
  print_summary
}

main "$@"
