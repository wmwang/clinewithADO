
# Agent Skill Hub

```text
+--------------------------------------------------------------------------------------------------+
| /---/                                                                                      \---/ |
|            .   '               * '                     .             '                           |
|                                                                                                  |
|                                A G E N T     S K I L L     H U B               s s               |
|                                                                                                  |
|                                One repo. Every AI skill team needs.                              |
|                                                                                                  |
|          o           o                                                             o             |
|      o---o---o---o---o---o                                                     o---o---o         |
| /---/                                                                                      \---/ |
+--------------------------------------------------------------------------------------------------+


> A shared skill repository for **Claude Code** and **Cline** — giving your AI coding agents enterprise-grade capabilities through a single `git clone`.

---

## The Problem

Your team uses AI coding agents daily. But out of the box, they can't query your Azure DevOps work items, review your PRs, or understand your legacy VB6 codebase. Each developer ends up writing their own prompts, with inconsistent quality and no way to share improvements.

**Agent Skill Hub** solves this by turning team knowledge into installable AI skills — version-controlled, peer-reviewed, and deployable to every developer's machine in minutes.

---

## What's Inside

```
clinewithADO/
├── Skills/                         # 13+ installable AI skills
│   ├── ado-devops/                 # ADO work items, PRs, repos, wiki
│   ├── ado-pr-review/              # AI code review on ADO PRs
│   ├── ado-pr-knowledge/           # Extract review rules from PR history
│   ├── legacy-code-analyzer/       # VB6/C#/VB.NET codebase analysis
│   ├── superpowers-plugin/         # Superpowers offline package
│   └── ...
│
├── .claude/skills/
│   └── team-skill-installer/       # One-click skill installer
│       ├── SKILL.md
│       └── scripts/                # Cross-platform Python scripts
│
└── Docker/                         # Cline + ADO MCP Docker image
    └── cline/
```

---

## Quick Start

### 1. Clone

```bash
git clone <repo-url>
cd clinewithADO
```

### 2. Open your AI agent

Launch **Claude Code** or **Cline** with `clinewithADO/` as your working directory.

### 3. Install skills

Just say:

> "Help me install skills"

The **team-skill-installer** activates automatically and guides you through:

1. Environment check (Python 3 required, Node.js optional)
2. Base packages installation (Superpowers, OpenSpec)
3. Skill selection from the full catalog
4. Dual-path installation to `~/.claude/skills/` + `~/.cline/skills/`
5. Installation summary

That's it. Skills work across all your projects — they live in your home directory, not in any single repo.

---

## Available Skills

### Azure DevOps Integration

| Skill | Description | Recommended |
|:------|:------------|:-----------:|
| **ado-devops** | Query work items, manage PRs, browse repos, search wiki | Required |
| **ado-pr-review** | AI code review with inline comments on ADO PRs | Yes |
| **ado-pr-knowledge** | Extract team code review rules from PR history | Yes |

### Development Workflows

| Skill | Description | Recommended |
|:------|:------------|:-----------:|
| **superpowers-workflow** | Full dev lifecycle: brainstorming → plan → implement → review | Yes |
| **kiro-skill** | Interactive requirements → design docs → task lists | Yes |
| **bmad-method** | Multi-agent framework (PM / Architect / Dev roles) | Advanced |
| **spec-kit-skill** | Charter-driven development (9 sub-commands) | Advanced |

### Legacy & Domain-Specific

| Skill | Description | Recommended |
|:------|:------------|:-----------:|
| **legacy-code-analyzer** | Deep analysis of VB6 / C# / VB.NET legacy systems | Yes |
| **npe-guardian** | Java NullPointerException detection and fix | Java projects |
| **prometheus** | Natural language Prometheus metric queries | K8s environments |

### Writing & Tooling

| Skill | Description | Recommended |
|:------|:------------|:-----------:|
| **tech-article-writer** | Technical articles in Traditional Chinese | Yes |
| **skill-creator** | Create and test new AI skills | Advanced |
| **skill-manual-writer** | Auto-generate skill documentation | Advanced |

### Base Packages

| Package | Description |
|:--------|:------------|
| **Superpowers** | Structured AI workflows — brainstorming, TDD, debugging, planning. Offline install included. |
| **OpenSpec** | Spec-driven development — proposal → spec → design → task list. |

---

## How It Works

```
┌──────────────────────────────────────────────────┐
│              Git Repo (source of truth)           │
│                                                  │
│  Skills/              ← skill source code        │
│  .claude/skills/      ← installer (auto-trigger) │
└──────────────┬───────────────────────────────────┘
               │  git clone / git pull
               ▼
┌──────────────────────────────────────────────────┐
│            Developer's Machine                    │
│                                                  │
│  ~/.claude/skills/    ← Claude Code reads here   │
│  ~/.cline/skills/     ← Cline reads here         │
│  ~/.claude/plugins/   ← Superpowers plugin       │
└──────────────────────────────────────────────────┘
```

### Design Decisions

| Decision | Reason |
|:---------|:-------|
| **Offline installation** | Corporate networks may block external plugin marketplaces |
| **Python scripts** | Cross-platform (Windows + macOS + Linux), no extra dependencies |
| **Dual-path install** | Some Cline versions don't read `~/.claude/skills/` |
| **Flat directory structure** | Cline only reads first-level subdirectories |
| **Backup before update** | Old version preserved before overwriting |
| **Git-based distribution** | Version history, `git pull` to sync, PR-based review for new skills |

---

## Updating Skills

```bash
git pull
```

Then tell your AI agent: "Update skills". The installer compares file hashes and only updates skills that have changed.

---

## Creating a New Skill

Anyone on the team can contribute a skill:

```
Skills/my-new-skill/
├── SKILL.md          # Instructions for the AI agent
└── scripts/          # Optional helper scripts
    └── helper.py
```

Write a `SKILL.md` with YAML frontmatter (`name`, `description`) and step-by-step instructions. Submit a PR. Once merged, the entire team can install it.

Install the **skill-creator** skill for a guided experience.

---



## Requirements

| Tool | Required | Notes |
|:-----|:--------:|:------|
| Git | Yes | To clone and update the repo |
| Python 3 | Yes | For installation scripts (cross-platform) |
| Claude Code or Cline | Yes | At least one AI agent |
| Node.js | Optional | Only for OpenSpec npm install |

---

## Contributing

1. Create a skill in `Skills/your-skill-name/`
2. Write a `SKILL.md` with clear instructions
3. Test it locally
4. Submit a PR

See the [skill-creator](Skills/skill-creator/) skill for a guided workflow.

---

## License

Internal use. See your organization's policies.
