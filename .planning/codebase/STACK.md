# Technology Stack

**Researched:** 2026-02-27  
**Domain:** Cline CLI + Azure DevOps MCP Server  
**Confidence:** HIGH

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `cline` | 2.5.0 | Command-line interface for project management | Widely used for automation |
| `@azure-devops/mcp` | 2.4.0 | Azure DevOps Model Context Protocol server | Integrates with Azure DevOps for CI/CD |
| Node.js | 22 (slim) | JavaScript runtime | Standard for server-side applications |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Docker | Latest | Containerization | For deploying applications in isolated environments |
| Docker Compose | Latest | Multi-container orchestration | For managing multi-container applications |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `@azure-devops/mcp` | Custom API integration | More control but requires more development effort |

**Installation:**
```bash
docker pull your-org/cline-ado:latest