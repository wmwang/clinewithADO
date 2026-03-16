# PromQL Patterns Reference

A quick-reference for translating common natural language requests into PromQL.

## Table of Contents

1. [Basic Patterns](#basic-patterns)
2. [Rate & Counter Patterns](#rate--counter-patterns)
3. [Aggregation Patterns](#aggregation-patterns)
4. [HTTP / API Patterns](#http--api-patterns)
5. [Container / Kubernetes Patterns](#container--kubernetes-patterns)
6. [Node / Host Patterns](#node--host-patterns)
7. [Alerting Patterns](#alerting-patterns)
8. [Time Functions](#time-functions)
9. [Common Gotchas](#common-gotchas)

---

## Basic Patterns

### "Is service X up?"
```promql
up{job="<service>"}
```

### "Show me all metrics for service X"
First discover metrics:
```promql
{job="<service>"}
```
Or use the metadata API: `prom_client.py metadata --limit 50`

### "What jobs/targets are being scraped?"
```promql
up
```
Or use: `prom_client.py targets`

---

## Rate & Counter Patterns

Counters only go up. To get meaningful values, apply `rate()` or `increase()`.

### "How many requests per second?"
```promql
rate(http_requests_total[5m])
```

### "Total requests in the last hour"
```promql
increase(http_requests_total[1h])
```

### "Request rate by status code"
```promql
sum by (status_code) (rate(http_requests_total[5m]))
```

### "Rate of errors (5xx)"
```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
```

### Choosing the range window `[Xm]`
- `[1m]` — noisy, good for real-time dashboards
- `[5m]` — standard, good default for most queries
- `[15m]` — smoother, good for trend analysis
- `[1h]` — very smooth, good for capacity planning

---

## Aggregation Patterns

### "Average across all instances"
```promql
avg(metric_name)
```

### "Total across all instances"
```promql
sum(metric_name)
```

### "Max value across instances"
```promql
max(metric_name)
```

### "Break down by label"
```promql
sum by (label_name) (metric_name)
```

### "Top 5 by value"
```promql
topk(5, metric_name)
```

### "Bottom 3 by value"
```promql
bottomk(3, metric_name)
```

### "Count how many series"
```promql
count(metric_name)
```

---

## HTTP / API Patterns

### "Error rate (percentage)"
```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
* 100
```

### "Success rate"
```promql
sum(rate(http_requests_total{status_code=~"2.."}[5m]))
/
sum(rate(http_requests_total[5m]))
* 100
```

### "P99 latency" (requires histogram)
```promql
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

### "P95 latency by endpoint"
```promql
histogram_quantile(0.95, sum by (le, handler) (rate(http_request_duration_seconds_bucket[5m])))
```

### "P50 (median) latency"
```promql
histogram_quantile(0.50, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

### "Average request duration"
```promql
rate(http_request_duration_seconds_sum[5m])
/
rate(http_request_duration_seconds_count[5m])
```

### "Requests per endpoint"
```promql
sum by (handler) (rate(http_requests_total[5m]))
```

---

## Container / Kubernetes Patterns

### "Pod CPU usage"
```promql
sum by (pod) (rate(container_cpu_usage_seconds_total{container!="POD", container!=""}[5m]))
```

### "Pod memory usage (bytes)"
```promql
sum by (pod) (container_memory_working_set_bytes{container!="POD", container!=""})
```

### "Pod memory usage (%)"
```promql
sum by (pod) (container_memory_working_set_bytes{container!="POD", container!=""})
/
sum by (pod) (container_spec_memory_limit_bytes{container!="POD", container!=""} > 0)
* 100
```

### "Container restarts"
```promql
sum by (pod, container) (increase(kube_pod_container_status_restarts_total[1h]))
```

### "Pods not ready"
```promql
kube_pod_status_ready{condition="false"}
```

### "Namespace resource usage"
```promql
sum by (namespace) (rate(container_cpu_usage_seconds_total{container!="POD", container!=""}[5m]))
```

---

## Node / Host Patterns

### "Node CPU usage (%)"
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### "Node memory usage (%)"
```promql
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
```

### "Disk usage (%)"
```promql
(1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100
```

### "Disk I/O rate"
```promql
rate(node_disk_read_bytes_total[5m]) + rate(node_disk_written_bytes_total[5m])
```

### "Network traffic (bytes/sec)"
```promql
rate(node_network_receive_bytes_total{device!="lo"}[5m])
```

---

## Alerting Patterns

### "Which alerts are firing?"
Use the API: `prom_client.py alerts`

### "Show recording rules"
Use the API: `prom_client.py rules --type record`

### "Show alert rules"
Use the API: `prom_client.py rules --type alert`

---

## Time Functions

### "Value at a specific time"
Use `--time` flag: `prom_client.py query 'up' --time 2024-01-15T10:00:00Z`

### "Range over last N hours"
Use `--start` flag: `prom_client.py query_range 'rate(http_requests_total[5m])' --start=-6h`

### "Compare to yesterday" (offset)
```promql
rate(http_requests_total[5m]) - rate(http_requests_total[5m] offset 1d)
```

### "Week-over-week comparison"
```promql
rate(http_requests_total[5m]) / rate(http_requests_total[5m] offset 7d)
```

---

## Common Gotchas

### Counter resets
Counters reset to 0 on restart. `rate()` and `increase()` handle this automatically.
Never use raw counter values — always wrap in `rate()` or `increase()`.

### Missing `by` clause
`sum(rate(x[5m]))` collapses everything into one number.
`sum by (instance) (rate(x[5m]))` keeps per-instance breakdown.

### Histogram buckets
`histogram_quantile()` needs the `le` label in the `by` clause:
```promql
histogram_quantile(0.99, sum by (le) (rate(bucket_metric[5m])))
```

### irate vs rate
- `rate()` — average rate over the window, smoother
- `irate()` — instant rate using last two data points, spikier

### Stale series
If a target goes down, its series become "stale" after 5 minutes.
Use `up == 0` to find down targets instead of checking for missing metrics.

### Label matching operators
- `=` exact match: `{job="api"}`
- `!=` not equal: `{job!="test"}`
- `=~` regex match: `{status_code=~"5.."}`
- `!~` regex not match: `{method!~"GET|HEAD"}`
