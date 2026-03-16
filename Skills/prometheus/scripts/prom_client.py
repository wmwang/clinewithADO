#!/usr/bin/env python3
"""
Prometheus HTTP client — query metrics via natural language workflow.

Uses only stdlib (urllib), no pip install needed. Follows the same pattern
as ado_client.py.

Environment variables:
  PROMETHEUS_URL   - Prometheus base URL (required, e.g. http://prometheus:9090)
  PROMETHEUS_TOKEN - Bearer token for Authorization header (required)

Usage:
  python prom_client.py query 'up'
  python prom_client.py query_range 'rate(http_requests_total[5m])' --start=-1h
  python prom_client.py series '{__name__=~"http_.*"}'
  python prom_client.py labels
  python prom_client.py label_values job
  python prom_client.py targets
  python prom_client.py alerts
  python prom_client.py rules
  python prom_client.py metadata http_requests_total
  python prom_client.py config
"""

import os
import sys
import json
import ssl
import time
import urllib.parse
import urllib.request
import urllib.error
import argparse
import re


def _load_config_file():
    """Load credentials from ~/.prometheus.env if it exists."""
    config_path = os.path.expanduser("~/.prometheus.env")
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip()
    return config


def get_client():
    """Build PromClient from environment variables or ~/.prometheus.env."""
    file_config = _load_config_file()

    url   = os.environ.get("PROMETHEUS_URL")   or file_config.get("PROMETHEUS_URL", "")
    token = os.environ.get("PROMETHEUS_TOKEN") or file_config.get("PROMETHEUS_TOKEN", "")

    errors = []
    if not url:
        errors.append("PROMETHEUS_URL")
    if not token:
        errors.append("PROMETHEUS_TOKEN")
    if errors:
        print(json.dumps({
            "error": f"Missing config: {', '.join(errors)}",
            "hint": "Set PROMETHEUS_URL and PROMETHEUS_TOKEN env vars, or create ~/.prometheus.env",
        }))
        sys.exit(1)
    return PromClient(url.rstrip("/"), token)


def _parse_duration(s):
    """Parse human-friendly duration like '-1h', '30m', '2d' into seconds."""
    m = re.match(r'^-?(\d+)([smhdw])$', s)
    if not m:
        return None
    val, unit = int(m.group(1)), m.group(2)
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return val * mult[unit]


class PromClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self._token = token
        self._opener = self._build_opener()

    def _build_opener(self):
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        return urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl_ctx)
        )

    def _request(self, path, method="GET", params=None, data=None):
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        req_data = None
        if data is not None:
            req_data = urllib.parse.urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        try:
            with self._opener.open(req) as resp:
                body = resp.read().decode()
                return json.loads(body) if body.strip() else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"HTTP {e.code} {method} {url}: {body}")

    # ── Instant Query ────────────────────────────────────────────────────────

    def query(self, promql, ts=None, timeout=None):
        """Execute an instant PromQL query.

        Args:
            promql: PromQL expression
            ts: evaluation timestamp (RFC3339 or unix, optional)
            timeout: query timeout (e.g. '30s', optional)
        """
        params = {"query": promql}
        if ts:
            params["time"] = ts
        if timeout:
            params["timeout"] = timeout
        return self._request("/api/v1/query", params=params)

    # ── Range Query ──────────────────────────────────────────────────────────

    def query_range(self, promql, start=None, end=None, step=None, timeout=None):
        """Execute a range PromQL query.

        Args:
            promql: PromQL expression
            start: start time (unix ts or RFC3339, default: 1 hour ago)
            end: end time (unix ts or RFC3339, default: now)
            step: resolution step (e.g. '15s', '1m', default: auto)
            timeout: query timeout
        """
        now = time.time()
        if start is None:
            start = str(now - 3600)
        elif isinstance(start, str) and start.startswith("-"):
            secs = _parse_duration(start)
            start = str(now - secs) if secs else start
        if end is None:
            end = str(now)
        if step is None:
            # Auto-calculate: ~250 data points
            try:
                duration = float(end) - float(start)
                step = f"{max(1, int(duration / 250))}s"
            except (ValueError, TypeError):
                step = "60s"
        params = {"query": promql, "start": start, "end": end, "step": step}
        if timeout:
            params["timeout"] = timeout
        return self._request("/api/v1/query_range", params=params)

    # ── Series & Labels ──────────────────────────────────────────────────────

    def series(self, match, start=None, end=None):
        """Find time series matching a label set selector."""
        now = time.time()
        params = {
            "match[]": match,
            "start": start or str(now - 3600),
            "end": end or str(now),
        }
        return self._request("/api/v1/series", params=params)

    def labels(self):
        """Get all label names."""
        return self._request("/api/v1/labels")

    def label_values(self, label_name):
        """Get all values for a given label."""
        label_enc = urllib.parse.quote(label_name, safe="")
        return self._request(f"/api/v1/label/{label_enc}/values")

    # ── Targets ──────────────────────────────────────────────────────────────

    def targets(self, state=None):
        """Get current scrape targets.

        Args:
            state: filter by state ('active', 'dropped', 'any')
        """
        params = {}
        if state:
            params["state"] = state
        return self._request("/api/v1/targets", params=params)

    # ── Rules & Alerts ───────────────────────────────────────────────────────

    def rules(self, rule_type=None):
        """Get alerting and recording rules.

        Args:
            rule_type: 'alert' or 'record'
        """
        params = {}
        if rule_type:
            params["type"] = rule_type
        return self._request("/api/v1/rules", params=params)

    def alerts(self):
        """Get active alerts."""
        return self._request("/api/v1/alerts")

    # ── Metadata ─────────────────────────────────────────────────────────────

    def metadata(self, metric=None, limit=None):
        """Get metric metadata (type, help text, unit).

        Args:
            metric: specific metric name (optional)
            limit: max entries per metric
        """
        params = {}
        if metric:
            params["metric"] = metric
        if limit:
            params["limit"] = str(limit)
        return self._request("/api/v1/metadata", params=params)

    # ── Config ───────────────────────────────────────────────────────────────

    def config(self):
        """Get Prometheus runtime configuration."""
        return self._request("/api/v1/status/config")


# ── CLI ──────────────────────────────────────────────────────────────────────

def _format_instant(result):
    """Format instant query results as readable text."""
    data = result.get("data", {})
    result_type = data.get("resultType", "")
    results = data.get("result", [])

    if not results:
        return "No results."

    lines = []
    if result_type == "vector":
        for item in results:
            metric = item.get("metric", {})
            name = metric.get("__name__", "")
            labels = ", ".join(f'{k}="{v}"' for k, v in metric.items() if k != "__name__")
            ts, val = item.get("value", [0, ""])
            label_str = f"{{{labels}}}" if labels else ""
            lines.append(f"  {name}{label_str}  →  {val}")
    elif result_type == "scalar":
        ts, val = data.get("result", [0, ""])
        lines.append(f"  scalar: {val}")
    else:
        lines.append(json.dumps(results, indent=2))

    return "\n".join(lines)


def _format_range(result):
    """Format range query results as readable text."""
    data = result.get("data", {})
    results = data.get("result", [])

    if not results:
        return "No results."

    lines = []
    for item in results:
        metric = item.get("metric", {})
        name = metric.get("__name__", "")
        labels = ", ".join(f'{k}="{v}"' for k, v in metric.items() if k != "__name__")
        values = item.get("values", [])
        label_str = f"{{{labels}}}" if labels else ""
        lines.append(f"  {name}{label_str}  ({len(values)} samples)")
        # Show first/last 3 data points
        show = values[:3] + (["  ..."] if len(values) > 6 else []) + values[-3:] if len(values) > 6 else values
        for v in show:
            if isinstance(v, list):
                from datetime import datetime, timezone
                ts_str = datetime.fromtimestamp(v[0], tz=timezone.utc).strftime("%H:%M:%S")
                lines.append(f"    [{ts_str}] {v[1]}")
            else:
                lines.append(f"    {v}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Prometheus CLI client")
    sub = parser.add_subparsers(dest="command")

    # query
    p_q = sub.add_parser("query", help="Instant query")
    p_q.add_argument("promql", help="PromQL expression")
    p_q.add_argument("--time", dest="ts", help="Evaluation timestamp")
    p_q.add_argument("--timeout", help="Query timeout")
    p_q.add_argument("--raw", action="store_true", help="Output raw JSON")

    # query_range
    p_qr = sub.add_parser("query_range", help="Range query")
    p_qr.add_argument("promql", help="PromQL expression")
    p_qr.add_argument("--start", default="-1h", help="Start time (default: -1h)")
    p_qr.add_argument("--end", help="End time (default: now)")
    p_qr.add_argument("--step", help="Resolution step (default: auto)")
    p_qr.add_argument("--timeout", help="Query timeout")
    p_qr.add_argument("--raw", action="store_true", help="Output raw JSON")

    # series
    p_s = sub.add_parser("series", help="Find series by label matcher")
    p_s.add_argument("match", help="Series selector, e.g. {__name__=~\"http_.*\"}")

    # labels
    sub.add_parser("labels", help="List all label names")

    # label_values
    p_lv = sub.add_parser("label_values", help="List values for a label")
    p_lv.add_argument("label", help="Label name")

    # targets
    p_t = sub.add_parser("targets", help="List scrape targets")
    p_t.add_argument("--state", choices=["active", "dropped", "any"], help="Filter state")

    # alerts
    sub.add_parser("alerts", help="List active alerts")

    # rules
    p_r = sub.add_parser("rules", help="List rules")
    p_r.add_argument("--type", dest="rule_type", choices=["alert", "record"], help="Filter type")

    # metadata
    p_m = sub.add_parser("metadata", help="Get metric metadata")
    p_m.add_argument("metric", nargs="?", help="Metric name (optional)")
    p_m.add_argument("--limit", type=int, help="Max entries per metric")

    # config
    sub.add_parser("config", help="Get Prometheus config")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = get_client()

    if args.command == "query":
        result = client.query(args.promql, ts=args.ts, timeout=args.timeout)
        if args.raw:
            print(json.dumps(result, indent=2))
        else:
            status = result.get("status", "unknown")
            print(f"Status: {status}")
            print(_format_instant(result))

    elif args.command == "query_range":
        result = client.query_range(args.promql, start=args.start, end=args.end,
                                     step=args.step, timeout=args.timeout)
        if args.raw:
            print(json.dumps(result, indent=2))
        else:
            status = result.get("status", "unknown")
            print(f"Status: {status}")
            print(_format_range(result))

    elif args.command == "series":
        result = client.series(args.match)
        data = result.get("data", [])
        print(f"Found {len(data)} series:")
        for s in data[:50]:
            print(f"  {s}")

    elif args.command == "labels":
        result = client.labels()
        data = result.get("data", [])
        print(f"Labels ({len(data)}):")
        for l in sorted(data):
            print(f"  {l}")

    elif args.command == "label_values":
        result = client.label_values(args.label)
        data = result.get("data", [])
        print(f"Values for '{args.label}' ({len(data)}):")
        for v in sorted(data):
            print(f"  {v}")

    elif args.command == "targets":
        result = client.targets(state=args.state)
        active = result.get("data", {}).get("activeTargets", [])
        print(f"Active targets ({len(active)}):")
        for t in active:
            health = t.get("health", "?")
            job = t.get("labels", {}).get("job", "?")
            url = t.get("scrapeUrl", "?")
            print(f"  [{health}] {job}  {url}")

    elif args.command == "alerts":
        result = client.alerts()
        alerts_list = result.get("data", {}).get("alerts", [])
        print(f"Active alerts ({len(alerts_list)}):")
        for a in alerts_list:
            state = a.get("state", "?")
            name = a.get("labels", {}).get("alertname", "?")
            print(f"  [{state}] {name}")

    elif args.command == "rules":
        result = client.rules(rule_type=getattr(args, "rule_type", None))
        groups = result.get("data", {}).get("groups", [])
        for g in groups:
            print(f"Group: {g.get('name', '?')}")
            for r in g.get("rules", []):
                rtype = r.get("type", "?")
                rname = r.get("name", "?")
                print(f"  [{rtype}] {rname}")

    elif args.command == "metadata":
        result = client.metadata(metric=args.metric, limit=args.limit)
        data = result.get("data", {})
        for name, entries in data.items():
            for e in entries:
                mtype = e.get("type", "?")
                help_text = e.get("help", "")
                print(f"  {name} ({mtype}): {help_text}")

    elif args.command == "config":
        result = client.config()
        yaml_str = result.get("data", {}).get("yaml", "")
        print(yaml_str[:2000] if yaml_str else json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
