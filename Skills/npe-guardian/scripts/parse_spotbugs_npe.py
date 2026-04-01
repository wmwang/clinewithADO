#!/usr/bin/env python3
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def rank(priority_text: str) -> int:
    try:
        return int(priority_text)
    except (TypeError, ValueError):
        return 99


def extract_source_lines(bug_instance):
    results = []
    for source_line in bug_instance.findall("SourceLine"):
        results.append(
            {
                "classname": source_line.attrib.get("classname"),
                "sourcepath": source_line.attrib.get("sourcepath"),
                "start": source_line.attrib.get("start"),
                "end": source_line.attrib.get("end"),
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse SpotBugs XML for NPE-focused findings.")
    parser.add_argument("report", help="Path to spotbugs XML report")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Report not found: {report_path}", file=sys.stderr)
        return 1

    tree = ET.parse(report_path)
    root = tree.getroot()

    findings = []
    for bug_instance in root.findall("BugInstance"):
        bug_code = bug_instance.attrib.get("abbrev") or bug_instance.attrib.get("type", "")
        bug_type = bug_instance.attrib.get("type", "")
        category = bug_instance.attrib.get("category", "")
        priority = bug_instance.attrib.get("priority", "")
        if not (bug_code == "NP" or bug_type.startswith("NP_") or bug_type.startswith("RCN_")):
            continue

        long_message = (bug_instance.findtext("LongMessage") or "").strip()
        class_name = None
        method_name = None
        field_name = None

        class_el = bug_instance.find("Class")
        if class_el is not None:
            class_name = class_el.attrib.get("classname")

        method_el = bug_instance.find("Method")
        if method_el is not None:
            method_name = method_el.attrib.get("name")

        field_el = bug_instance.find("Field")
        if field_el is not None:
            field_name = field_el.attrib.get("name")

        source_lines = extract_source_lines(bug_instance)
        findings.append(
            {
                "type": bug_type,
                "category": category,
                "priority": rank(priority),
                "message": long_message,
                "class": class_name,
                "method": method_name,
                "field": field_name,
                "source_lines": source_lines,
            }
        )

    findings.sort(key=lambda item: (item["priority"], item["class"] or "", item["method"] or ""))

    if args.json:
        print(json.dumps(findings, indent=2))
        return 0

    for index, finding in enumerate(findings, start=1):
        location = "unknown"
        if finding["source_lines"]:
            line = finding["source_lines"][0]
            path = line.get("sourcepath") or line.get("classname") or "unknown"
            start = line.get("start") or "?"
            location = f"{path}:{start}"
        print(f"[{index}] {finding['type']} @ {location}")
        if finding["class"]:
            print(f"  class: {finding['class']}")
        if finding["method"]:
            print(f"  method: {finding['method']}")
        if finding["field"]:
            print(f"  field: {finding['field']}")
        print(f"  message: {finding['message']}")

    if not findings:
        print("No NPE-focused SpotBugs findings found.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
