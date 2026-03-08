#!/usr/bin/env python3
"""Build a lightweight inventory for a legacy VB6 / .NET subproject."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


VB6_EXTENSIONS = {".frm", ".bas", ".cls"}
SKIP_FILE_SUFFIXES = (
    ".designer.vb",
    ".designer.cs",
    "AssemblyInfo.vb",
    "AssemblyInfo.cs",
)
PROJECT_TYPES = {
    ".vbp": "vb6",
    ".vbproj": "vbnet",
    ".csproj": "csharp",
}
EVENT_SUFFIXES = (
    "_click",
    "_load",
    "_change",
    "_selectedindexchanged",
    "_textchanged",
    "_dblclick",
    "_command",
    "_timer",
)
CALL_KEYWORDS = {
    "if",
    "then",
    "for",
    "while",
    "switch",
    "select",
    "case",
    "catch",
    "using",
    "return",
    "new",
    "nameof",
    "typeof",
    "when",
    "get",
    "set",
    "raiseevent",
    "msgbox",
    "format",
    "trim",
    "cint",
    "cstr",
    "cdbl",
    "if",
}
SQL_OP_PATTERNS = {
    "SELECT": re.compile(r"\bSELECT\b", re.IGNORECASE),
    "INSERT": re.compile(r"\bINSERT\s+INTO\b", re.IGNORECASE),
    "UPDATE": re.compile(r"\bUPDATE\b", re.IGNORECASE),
    "DELETE": re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE),
    "EXEC": re.compile(r"\bEXEC(?:UTE)?\b", re.IGNORECASE),
}
TABLE_PATTERNS = [
    re.compile(r"\bFROM\s+([A-Za-z_][A-Za-z0-9_\[\].]*)", re.IGNORECASE),
    re.compile(r"\bJOIN\s+([A-Za-z_][A-Za-z0-9_\[\].]*)", re.IGNORECASE),
    re.compile(r"\bINTO\s+([A-Za-z_][A-Za-z0-9_\[\].]*)", re.IGNORECASE),
    re.compile(r"\bUPDATE\s+([A-Za-z_][A-Za-z0-9_\[\].]*)", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\s+([A-Za-z_][A-Za-z0-9_\[\].]*)", re.IGNORECASE),
    re.compile(r"\bEXEC(?:UTE)?\s+([A-Za-z_][A-Za-z0-9_\[\].]*)", re.IGNORECASE),
]
VB_DECL_RE = re.compile(
    r"^\s*"
    r"(?:(?P<visibility>Public|Private|Friend|Protected|Protected Friend|Private Protected)\s+)?"
    r"(?:(?:Shared|Static|Async|Overloads|Overrides|NotOverridable|Overridable|Default)\s+)*"
    r"(?P<kind>Function|Sub|Property\s+Get|Property\s+Set|Property\s+Let)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*"
    r"(?P<params>\([^)]*\))?"
    r"(?:\s+As\s+(?P<return>[A-Za-z0-9_.()]+))?",
    re.IGNORECASE,
)
VB_END_RE = re.compile(r"^\s*End\s+(Function|Sub|Property)\b", re.IGNORECASE)
CS_DECL_RE = re.compile(
    r"^\s*"
    r"(?:(?P<visibility>public|private|protected|internal)\s+)?"
    r"(?:(?:static|virtual|override|sealed|async|partial|new|extern)\s+)*"
    r"(?P<return>[A-Za-z_][A-Za-z0-9_<>\[\],?. ]+?)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*"
    r"\((?P<params>[^)]*)\)"
    r"(?:\s*where\s+[^{]+)?"
    r"\s*(?P<trailer>\{)?\s*$",
    re.IGNORECASE,
)
CS_CTOR_RE = re.compile(
    r"^\s*"
    r"(?:(?P<visibility>public|private|protected|internal)\s+)"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*"
    r"\((?P<params>[^)]*)\)"
    r"(?:\s*:\s*[^{]+)?"
    r"\s*(?P<trailer>\{)?\s*$",
    re.IGNORECASE,
)
STRING_LITERAL_RE = re.compile(r'"([^"\n]*)"')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build inventory artifacts for a legacy VB6/.NET subproject.",
    )
    parser.add_argument("target", help="Path to the target subproject")
    parser.add_argument(
        "--output",
        required=True,
        help="Directory for generated inventory artifacts",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp950", "big5", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def to_posix(path: Path) -> str:
    return path.as_posix()


def rel_path(path: Path, root: Path) -> str:
    return to_posix(path.relative_to(root))


def normalize_name(name: str) -> str:
    return re.sub(r"[\[\]]", "", name).strip().strip(",;")


def project_type_for_file(path: Path) -> str:
    if path.suffix.lower() in VB6_EXTENSIONS:
        return "vb6"
    if path.suffix.lower() == ".vb":
        return "vbnet"
    if path.suffix.lower() == ".cs":
        return "csharp"
    return "unknown"


def source_kind(path: Path, text: str, language: str) -> str:
    lower_text = text.lower()
    suffix = path.suffix.lower()
    if suffix == ".frm":
        return "form"
    if suffix == ".bas":
        return "module"
    if suffix == ".cls":
        return "class"
    if language in {"vbnet", "csharp"}:
        if "inherits form" in lower_text or re.search(r":\s*form\b", lower_text):
            return "form"
        if re.search(r"\bmodule\b", text, re.IGNORECASE):
            return "module"
        if re.search(r"\bclass\b", text, re.IGNORECASE):
            return "class"
    return "code"


def detect_container(path: Path, text: str, language: str) -> str:
    if language == "vb6":
        for pattern in (
            r'Attribute VB_Name = "([^"]+)"',
            r"Begin\s+VB\.Form\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"Begin\s+VB\.[A-Za-z0-9_]+\s+([A-Za-z_][A-Za-z0-9_]*)",
        ):
            match = re.search(pattern, text)
            if match:
                return match.group(1)
    else:
        for pattern in (
            r"\b(?:Public|Friend|Private|Protected)?\s*(?:Partial\s+)?Class\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\b(?:Public|Friend|Private|Protected)?\s*Module\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\b(?:public|internal|private|protected)?\s*(?:partial\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)",
        ):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
    return path.stem


def extract_connection_info(text: str) -> list[dict[str, str]]:
    joined = " ".join(fragment.strip() for fragment in STRING_LITERAL_RE.findall(text))
    if not joined:
        return []
    server_match = re.search(r"(?:Server|Data Source)\s*=\s*([^;]+)", joined, re.IGNORECASE)
    database_match = re.search(
        r"(?:Database|Initial Catalog)\s*=\s*([^;]+)",
        joined,
        re.IGNORECASE,
    )
    if not server_match and not database_match:
        return []
    summary = {}
    if server_match:
        summary["server"] = server_match.group(1).strip()
    if database_match:
        summary["database"] = database_match.group(1).strip()
    return [summary]


def extract_sql_metadata(text: str) -> tuple[list[str], list[str]]:
    fragments = [fragment.strip() for fragment in STRING_LITERAL_RE.findall(text) if fragment.strip()]
    if not fragments:
        return [], []
    joined = " ".join(fragments)
    ops = [name for name, pattern in SQL_OP_PATTERNS.items() if pattern.search(joined)]
    tables: set[str] = set()
    for pattern in TABLE_PATTERNS:
        for match in pattern.findall(joined):
            tables.add(normalize_name(match))
    return sorted(set(ops)), sorted(tables)


def looks_like_event_handler(name: str, declaration: str) -> bool:
    lower_name = name.lower()
    if any(lower_name.endswith(suffix) for suffix in EVENT_SUFFIXES):
        return True
    return " handles " in declaration.lower()


def parse_vb_functions(
    lines: list[str],
    file_rel: str,
    language: str,
    container: str,
) -> list[dict]:
    functions = []
    index = 0
    while index < len(lines):
        match = VB_DECL_RE.match(lines[index])
        if not match:
            index += 1
            continue
        start = index
        end = index
        for probe in range(index + 1, len(lines)):
            if VB_END_RE.match(lines[probe]):
                end = probe
                break
        body_lines = lines[start : end + 1]
        kind = re.sub(r"\s+", "_", match.group("kind").strip().lower())
        name = match.group("name")
        declaration = lines[start].strip()
        sql_ops, tables = extract_sql_metadata("\n".join(body_lines))
        functions.append(
            {
                "name": name,
                "qualified_name": f"{container}.{name}",
                "file": file_rel,
                "language": language,
                "container": container,
                "visibility": (match.group("visibility") or "private").strip(),
                "kind": kind,
                "params": (match.group("params") or "").strip(),
                "return_type": (match.group("return") or "").strip(),
                "start_line": start + 1,
                "end_line": end + 1,
                "is_event_handler": looks_like_event_handler(name, declaration),
                "called_names": [],
                "tables": tables,
                "sql_ops": sql_ops,
                "_body": "\n".join(body_lines),
            }
        )
        index = end + 1
    return functions


def find_brace_start(lines: list[str], start: int) -> int | None:
    for index in range(start, len(lines)):
        if "{" in lines[index]:
            return index
        stripped = lines[index].strip()
        if stripped.endswith(";"):
            return None
    return None


def parse_csharp_functions(lines: list[str], file_rel: str, container: str) -> list[dict]:
    functions = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = CS_DECL_RE.match(line)
        constructor_match = CS_CTOR_RE.match(line)
        if not match and not constructor_match:
            index += 1
            continue
        if match and match.group("name").lower() in CALL_KEYWORDS:
            index += 1
            continue

        if constructor_match and constructor_match.group("name") != container:
            constructor_match = None
        if not match and not constructor_match:
            index += 1
            continue

        name = (
            match.group("name") if match else constructor_match.group("name")
        )
        brace_start = find_brace_start(lines, index)
        if brace_start is None:
            index += 1
            continue

        depth = 0
        end = brace_start
        started = False
        for probe in range(brace_start, len(lines)):
            depth += lines[probe].count("{")
            depth -= lines[probe].count("}")
            if "{" in lines[probe]:
                started = True
            if started and depth == 0:
                end = probe
                break

        body_lines = lines[index : end + 1]
        declaration = lines[index].strip()
        sql_ops, tables = extract_sql_metadata("\n".join(body_lines))
        visibility = "private"
        return_type = ""
        if match:
            visibility = (match.group("visibility") or "private").strip()
            return_type = (match.group("return") or "").strip()
        else:
            visibility = constructor_match.group("visibility").strip()
        functions.append(
            {
                "name": name,
                "qualified_name": f"{container}.{name}",
                "file": file_rel,
                "language": "csharp",
                "container": container,
                "visibility": visibility,
                "kind": "constructor" if not match else "method",
                "params": (match.group("params") if match else constructor_match.group("params")).strip(),
                "return_type": return_type,
                "start_line": index + 1,
                "end_line": end + 1,
                "is_event_handler": looks_like_event_handler(name, declaration),
                "called_names": [],
                "tables": tables,
                "sql_ops": sql_ops,
                "_body": "\n".join(body_lines),
            }
        )
        index = end + 1
    return functions


def parse_ui_controls(path: Path, text: str, file_rel: str, language: str, container: str) -> list[dict]:
    controls = []
    if path.suffix.lower() == ".frm":
        lines = text.splitlines()
        index = 0
        while index < len(lines):
            match = re.match(
                r"^\s*Begin\s+(?P<type>[A-Za-z0-9_.]+)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)",
                lines[index],
            )
            if not match:
                index += 1
                continue
            depth = 1
            caption = ""
            for probe in range(index + 1, len(lines)):
                if re.match(r"^\s*Begin\b", lines[probe]):
                    depth += 1
                if re.match(r"^\s*End\b", lines[probe]):
                    depth -= 1
                    if depth == 0:
                        break
                caption_match = re.search(r'(Caption|Text)\s*=\s*"([^"]*)"', lines[probe])
                if caption_match and not caption:
                    caption = caption_match.group(2)
            controls.append(
                {
                    "file": file_rel,
                    "container": container,
                    "control_name": match.group("name"),
                    "control_type": match.group("type"),
                    "caption": caption,
                    "source": "vb6-form",
                }
            )
            index += 1
        return controls

    vb_pattern = re.compile(
        r"^\s*(?:Private|Friend|Protected|Public)\s+(?:WithEvents\s+)?"
        r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+As\s+(?P<type>[A-Za-z_][A-Za-z0-9_.]*)",
        re.IGNORECASE,
    )
    cs_pattern = re.compile(
        r"^\s*(?:private|protected|internal|public)\s+"
        r"(?P<type>[A-Za-z_][A-Za-z0-9_.<>]*)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*;",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        match = vb_pattern.match(line) if language == "vbnet" else cs_pattern.match(line)
        if not match:
            continue
        controls.append(
            {
                "file": file_rel,
                "container": container,
                "control_name": match.group("name"),
                "control_type": match.group("type"),
                "caption": "",
                "source": "code-declaration",
            }
        )
    return controls


def list_project_files(target: Path) -> list[dict]:
    project_files = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        project_type = PROJECT_TYPES.get(path.suffix.lower())
        if not project_type:
            continue
        project_files.append(
            {
                "path": to_posix(path),
                "relative_path": rel_path(path, target),
                "type": project_type,
            }
        )
    return project_files


def list_source_files(target: Path) -> list[Path]:
    files = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        lower_name = path.name.lower()
        if lower_name.endswith(SKIP_FILE_SUFFIXES):
            continue
        if path.suffix.lower() in VB6_EXTENSIONS or path.suffix.lower() in {".vb", ".cs"}:
            files.append(path)
    return files


def detect_calls(functions: list[dict]) -> list[dict]:
    by_name: dict[str, list[dict]] = defaultdict(list)
    by_container_and_name: dict[tuple[str, str], list[dict]] = defaultdict(list)
    id_map = {}
    for function in functions:
        by_name[function["name"].lower()].append(function)
        by_container_and_name[(function["container"].lower(), function["name"].lower())].append(function)
        id_map[function["function_id"]] = function

    call_pattern = re.compile(
        r"(?:(?P<qualifier>[A-Za-z_][A-Za-z0-9_]*)\s*\.\s*)?(?P<callee>[A-Za-z_][A-Za-z0-9_]*)\s*\(",
    )
    call_keyword_pattern = re.compile(
        r"\bCall\s+(?:(?P<qualifier>[A-Za-z_][A-Za-z0-9_]*)\s*\.\s*)?(?P<callee>[A-Za-z_][A-Za-z0-9_]*)",
        re.IGNORECASE,
    )
    edges = []

    for function in functions:
        seen_edges = set()
        called_names = set()
        body = function.pop("_body")
        matches = list(call_pattern.finditer(body)) + list(call_keyword_pattern.finditer(body))
        for match in matches:
            callee = match.group("callee")
            qualifier = match.group("qualifier") or ""
            if not callee or callee.lower() in CALL_KEYWORDS:
                continue
            if callee == function["name"] and (not qualifier or qualifier.lower() == function["container"].lower()):
                continue
            called_names.add(f"{qualifier}.{callee}" if qualifier else callee)
            candidates = []
            reason = "ambiguous-name"
            confidence = 0.4

            if qualifier:
                candidates = by_container_and_name.get((qualifier.lower(), callee.lower()), [])
                if candidates:
                    reason = "qualified"
                    confidence = 0.95 if len(candidates) == 1 else 0.65

            if not candidates:
                same_container = by_container_and_name.get((function["container"].lower(), callee.lower()), [])
                if same_container:
                    candidates = same_container
                    reason = "same-container"
                    confidence = 0.85 if len(candidates) == 1 else 0.55

            if not candidates:
                candidates = by_name.get(callee.lower(), [])
                if len(candidates) == 1:
                    reason = "unique-name"
                    confidence = 0.8
                elif len(candidates) > 1:
                    reason = "ambiguous-name"
                    confidence = 0.4

            for candidate in candidates:
                edge_key = (function["function_id"], candidate["function_id"], qualifier, callee)
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)
                edges.append(
                    {
                        "source_id": function["function_id"],
                        "target_id": candidate["function_id"],
                        "source_qualified_name": function["qualified_name"],
                        "target_qualified_name": candidate["qualified_name"],
                        "callee_name": callee,
                        "qualifier": qualifier,
                        "confidence": confidence,
                        "reason": reason,
                        "evidence": "inventory-derived",
                    }
                )

        function["called_names"] = sorted(called_names)

    fan_in = Counter(edge["target_id"] for edge in edges)
    fan_out = Counter(edge["source_id"] for edge in edges)
    for function in functions:
        function["fan_in"] = fan_in[function["function_id"]]
        function["fan_out"] = fan_out[function["function_id"]]
    return edges


def write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def csv_safe_function_rows(functions: list[dict]) -> list[dict]:
    rows = []
    for function in functions:
        row = dict(function)
        row["called_names"] = "|".join(function["called_names"])
        row["tables"] = "|".join(function["tables"])
        row["sql_ops"] = "|".join(function["sql_ops"])
        rows.append(row)
    return rows


def build_summary(
    output_dir: Path,
    target: Path,
    project_files: list[dict],
    source_files: list[dict],
    functions: list[dict],
    edges: list[dict],
    sql_operations: list[dict],
    ui_controls: list[dict],
) -> str:
    source_kinds = Counter(source_file["kind"] for source_file in source_files)
    hotspot_functions = sorted(
        functions,
        key=lambda item: (item["fan_in"] + item["fan_out"], item["fan_out"], item["qualified_name"]),
        reverse=True,
    )[:10]

    lines = [
        "# Legacy Inventory Summary",
        "",
        "## Scope",
        f"- Target path: `{to_posix(target)}`",
        f"- Generated at: `{datetime.now().isoformat(timespec='seconds')}`",
        "",
        "## Project files",
    ]
    if project_files:
        lines.extend(f"- `{item['relative_path']}` ({item['type']})" for item in project_files)
    else:
        lines.append("- No project file found under the target path.")

    lines.extend(
        [
            "",
            "## Counts",
            f"- Source files: {len(source_files)}",
            f"- Forms: {source_kinds.get('form', 0)}",
            f"- Modules: {source_kinds.get('module', 0)}",
            f"- Classes: {source_kinds.get('class', 0)}",
            f"- Functions: {len(functions)}",
            f"- Call edges: {len(edges)}",
            f"- SQL-touching functions: {len(sql_operations)}",
            f"- UI controls: {len(ui_controls)}",
            "",
            "## Hotspots",
        ]
    )

    if hotspot_functions:
        for function in hotspot_functions:
            lines.append(
                "- `{name}` in `{file}:{line}` | fan_in={fan_in}, fan_out={fan_out}, sql_ops={sql_ops}".format(
                    name=function["qualified_name"],
                    file=function["file"],
                    line=function["start_line"],
                    fan_in=function["fan_in"],
                    fan_out=function["fan_out"],
                    sql_ops="|".join(function["sql_ops"]) or "-",
                )
            )
    else:
        lines.append("- No function declarations detected.")

    lines.extend(
        [
            "",
            "## Artifacts",
            f"- `{to_posix(output_dir / 'inventory.json')}`",
            f"- `{to_posix(output_dir / 'function-index.csv')}`",
            f"- `{to_posix(output_dir / 'call-edges.csv')}`",
            f"- `{to_posix(output_dir / 'sql-operations.csv')}`",
            f"- `{to_posix(output_dir / 'ui-controls.csv')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    target = Path(args.target).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()

    if not target.exists() or not target.is_dir():
        raise SystemExit(f"Target path not found or not a directory: {target}")

    output_dir.mkdir(parents=True, exist_ok=True)

    project_files = list_project_files(target)
    source_paths = list_source_files(target)

    source_files = []
    functions = []
    ui_controls = []
    connections = []
    sql_operations = []

    for source_path in source_paths:
        text = read_text(source_path)
        file_rel = rel_path(source_path, target)
        language = project_type_for_file(source_path)
        container = detect_container(source_path, text, language)
        kind = source_kind(source_path, text, language)
        source_files.append(
            {
                "path": file_rel,
                "language": language,
                "kind": kind,
                "container": container,
            }
        )
        ui_controls.extend(parse_ui_controls(source_path, text, file_rel, language, container))
        for connection in extract_connection_info(text):
            connections.append(
                {
                    "file": file_rel,
                    "container": container,
                    **connection,
                }
            )

        lines = text.splitlines()
        if language in {"vb6", "vbnet"}:
            parsed = parse_vb_functions(lines, file_rel, language, container)
        elif language == "csharp":
            parsed = parse_csharp_functions(lines, file_rel, container)
        else:
            parsed = []
        functions.extend(parsed)

    for index, function in enumerate(functions, start=1):
        function["function_id"] = f"F{index:04d}"

    edges = detect_calls(functions)

    for function in functions:
        if function["sql_ops"] or function["tables"]:
            sql_operations.append(
                {
                    "function_id": function["function_id"],
                    "qualified_name": function["qualified_name"],
                    "file": function["file"],
                    "sql_ops": "|".join(function["sql_ops"]),
                    "tables": "|".join(function["tables"]),
                }
            )

    inventory = {
        "target_path": to_posix(target),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_files": project_files,
        "source_files": source_files,
        "functions": functions,
        "call_edges": edges,
        "sql_operations": sql_operations,
        "ui_controls": ui_controls,
        "connections": connections,
        "stats": {
            "source_file_count": len(source_files),
            "function_count": len(functions),
            "call_edge_count": len(edges),
            "sql_function_count": len(sql_operations),
            "ui_control_count": len(ui_controls),
        },
    }

    (output_dir / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "inventory_summary.md").write_text(
        build_summary(
            output_dir,
            target,
            project_files,
            source_files,
            functions,
            edges,
            sql_operations,
            ui_controls,
        ),
        encoding="utf-8",
    )

    write_csv(
        output_dir / "function-index.csv",
        csv_safe_function_rows(functions),
        [
            "function_id",
            "qualified_name",
            "file",
            "language",
            "container",
            "visibility",
            "kind",
            "start_line",
            "end_line",
            "is_event_handler",
            "params",
            "return_type",
            "fan_in",
            "fan_out",
            "called_names",
            "tables",
            "sql_ops",
        ],
    )
    write_csv(
        output_dir / "call-edges.csv",
        edges,
        [
            "source_id",
            "target_id",
            "source_qualified_name",
            "target_qualified_name",
            "callee_name",
            "qualifier",
            "confidence",
            "reason",
            "evidence",
        ],
    )
    write_csv(
        output_dir / "sql-operations.csv",
        sql_operations,
        [
            "function_id",
            "qualified_name",
            "file",
            "sql_ops",
            "tables",
        ],
    )
    write_csv(
        output_dir / "ui-controls.csv",
        ui_controls,
        [
            "file",
            "container",
            "control_name",
            "control_type",
            "caption",
            "source",
        ],
    )
    write_csv(
        output_dir / "connections.csv",
        connections,
        [
            "file",
            "container",
            "server",
            "database",
        ],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
