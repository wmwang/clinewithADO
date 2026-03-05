# BMAD Method

The BMad Agile Development method - a full product development framework with specialized AI agents for each role.

**Source:** [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)

## Agents

| Agent | Name | Role |
|-------|------|------|
| `analyst` | Mary | Business Analyst - requirements, research, project briefs |
| `pm` | John | Product Manager - PRDs, user stories, prioritization |
| `architect` | Winston | Software Architect - system design, technology decisions |
| `dev` | Amelia | Developer - TDD implementation, code review |
| `sm` | Bob | Scrum Master - sprint planning, retrospectives, blockers |

## How It Works

Each agent has:
- A distinct **persona** with a name and personality
- **Specific responsibilities** for their role
- **Workflows** they can execute
- **Communication style** guidelines

## Usage

Invoke an agent by name in your prompt:

```
"Mary, can you help me understand the requirements for the payment system?"
"John, please create user stories for the authentication feature."
"Winston, design the architecture for our microservices migration."
"Amelia, implement Story 3: User login with JWT."
"Bob, run sprint planning for our 2-week sprint."
```

## Installation

Use the repo's `install.sh` to copy agents to the right location.

**For Cline (project):** Agents go to `.clinerules/bmad/`
**For Cline (global):** Agents go to `~/.cline/rules/bmad/`
**For OpenCode (project):** Agents go to `.opencode/commands/bmad/`
**For OpenCode (global):** Agents go to `~/.config/opencode/commands/bmad/`

## Full Framework

For the complete BMAD framework including workflows, tasks, and modules, visit the [official repository](https://github.com/bmad-code-org/BMAD-METHOD).
