---
name: prometheus
description: "Natural language interface for querying Prometheus metrics. This skill should be used when the user asks to \"check metrics\", \"query Prometheus\", \"show me CPU usage\", \"what's the error rate\", \"how's the service doing\", \"check alerts\", \"查指標\", \"看 metrics\", \"查 Prometheus\", \"服務狀態\", \"error rate 多少\", \"CPU 用量\", \"memory 使用率\", or any request involving monitoring data, PromQL, metrics exploration, or system observability. Use this skill whenever the user mentions Prometheus, Grafana metrics, monitoring, alerting, scrape targets, or wants to understand system health — even if they don't explicitly say 'Prometheus'."
---

# Prometheus Natural Language Query

Translate natural language requests into PromQL queries, execute them against the Prometheus HTTP API, and present results in a clear, readable format.

## Setup

Two environment variables are required:

| Variable | Description | Example |
|----------|-------------|---------|
| `PROMETHEUS_URL` | Prometheus base URL | `http://prometheus.internal:9090` |
| `PROMETHEUS_TOKEN` | Bearer token for auth | `eyJhbG...` |

These can also be set in `~/.prometheus.env`:
```
PROMETHEUS_URL=http://prometheus.internal:9090
PROMETHEUS_TOKEN=your-token-here
```

## Workflow

When a user asks about metrics in natural language, follow this process:

### 1. Understand the Intent

Identify what the user wants to know. Common patterns:

| User says | Intent |
|-----------|--------|
| "Is the API up?" | Check service health |
| "How many errors in the last hour?" | Error count / rate |
| "CPU usage of pod X" | Resource utilization |
| "What's the p99 latency?" | Performance percentile |
| "Any alerts firing?" | Alert status |
| "Show me request rate by endpoint" | Traffic breakdown |

### 2. Discover Available Metrics

Before writing PromQL, understand what metrics exist. Use these commands from the `scripts/prom_client.py` script:

```bash
# List all scrape targets and their health
python <SKILL_DIR>/scripts/prom_client.py targets

# Find metrics by name pattern
python <SKILL_DIR>/scripts/prom_client.py series '{__name__=~"http_.*"}'

# Get metadata (type, help text) for a metric
python <SKILL_DIR>/scripts/prom_client.py metadata http_requests_total

# List all label names
python <SKILL_DIR>/scripts/prom_client.py labels

# List values for a specific label (e.g. all job names)
python <SKILL_DIR>/scripts/prom_client.py label_values job
```

This discovery step matters because metric names vary across setups. Don't assume metric names — check what's actually available.

### 3. Build and Execute the Query

Consult `references/promql_patterns.md` for common PromQL patterns organized by use case (HTTP, containers, node, etc.).

**Instant query** (current value):
```bash
python <SKILL_DIR>/scripts/prom_client.py query 'rate(http_requests_total[5m])'
```

**Range query** (time series):
```bash
python <SKILL_DIR>/scripts/prom_client.py query_range 'rate(http_requests_total[5m])' --start=-1h
```

**With raw JSON output** (for programmatic use):
```bash
python <SKILL_DIR>/scripts/prom_client.py query 'up' --raw
```

### 4. Present Results

Format the output to match what the user asked:

**Summary style** — when user asks a yes/no or single-value question:
> API service is **UP** across all 3 instances. Last scrape: 12s ago.

**Table style** — when showing multiple metrics:
> | Pod | CPU Usage | Memory |
> |-----|-----------|--------|
> | api-7c8d | 23% | 512 MB |
> | api-9f2a | 18% | 489 MB |

**Trend style** — when showing changes over time:
> HTTP error rate over the last hour:
> - 10:00 → 0.2%
> - 10:15 → 0.3%
> - 10:30 → 1.8% (spike)
> - 10:45 → 0.4% (recovered)

### 5. Suggest Follow-ups

After presenting results, suggest related queries the user might want to explore. For example, if they asked about error rate, suggest:
- "Want me to break that down by endpoint?"
- "Should I check which pods have the highest error rate?"
- "Want to see the p99 latency alongside the errors?"

## Quick Command Reference

| Command | What it does |
|---------|-------------|
| `query '<promql>'` | Instant query (current value) |
| `query_range '<promql>' --start=-Xh` | Range query over time |
| `series '{matcher}'` | Find matching time series |
| `labels` | List all label names |
| `label_values <label>` | List values for a label |
| `targets` | Show scrape targets and health |
| `alerts` | Show firing alerts |
| `rules` | Show alert/recording rules |
| `metadata <metric>` | Get metric type and help text |
| `config` | Get Prometheus runtime config |

All commands are run via: `python <SKILL_DIR>/scripts/prom_client.py <command>`

## Key Principles

- **Discover before querying.** Metric names differ across environments. Always check what's available before assuming a metric name exists.
- **Counters need rate().** Raw counter values are meaningless — always wrap counters in `rate()` or `increase()`.
- **Default to 5m windows.** Use `[5m]` as the range window unless the user asks for finer or coarser granularity.
- **Show units.** Always include units in output (%, bytes, req/s, ms). Convert bytes to human-readable (MB/GB) when appropriate.
- **Explain the query.** Briefly tell the user what PromQL was generated, so they can learn and reuse it.

## Additional Resources

### Reference Files

For detailed PromQL patterns organized by use case:
- **`references/promql_patterns.md`** — Common query patterns for HTTP, containers, nodes, alerting, and more. Consult this when translating natural language into PromQL.
