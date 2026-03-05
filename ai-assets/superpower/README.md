# Superpower Skills

Skills for AI coding assistants that encode proven engineering methodologies as reusable instructions.

**Source:** [obra/superpowers-skills](https://github.com/obra/superpowers-skills)

## Available Skills

### Collaboration
| Skill | Description |
|-------|-------------|
| `brainstorming` | Structure problem exploration before coding |
| `writing-plans` | Create actionable implementation plans |
| `finishing-a-development-branch` | Complete branches cleanly before merge |
| `subagent-driven-development` | Coordinate parallel work via subagents |
| `executing-plans` | Execute written plans in batches with checkpoints |

### Debugging
| Skill | Description |
|-------|-------------|
| `systematic-debugging` | Root cause first, then fix |
| `root-cause-tracing` | Trace bugs to their true origin |
| `defense-in-depth` | Validate at every layer |

### Problem Solving
| Skill | Description |
|-------|-------------|
| `when-stuck` | Break through mental blocks |
| `inversion-exercise` | Find solutions by exploring failure modes |

### Testing
| Skill | Description |
|-------|-------------|
| `test-driven-development` | Red-Green-Refactor cycle |

## How Skills Work

Each skill is a `SKILL.md` file containing:
- **Purpose:** What the skill does and when to use it
- **Methodology:** Step-by-step phases
- **Anti-patterns:** What to avoid
- **Verification checklist:** How to confirm quality

The AI announces when it's using a skill: `"I'm using the [Skill Name] skill."`

## Installation

Use the repo's `install.sh` to copy skills to the right location for your AI tool.

**For Cline (project):** Skills go to `.clinerules/superpower-skills/`
**For Cline (global):** Skills go to `~/.cline/rules/superpower-skills/`
**For OpenCode (project):** Skills go to `.opencode/commands/superpower/`
**For OpenCode (global):** Skills go to `~/.config/opencode/commands/superpower/`
