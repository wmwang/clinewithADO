#!/usr/bin/env python3
from pathlib import PurePosixPath
import subprocess
import sys


def run_git_diff(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [line for line in lines if PurePosixPath(line).suffix == ".java"]


def main() -> int:
    base_ref = sys.argv[1] if len(sys.argv) > 1 else ""
    head_ref = sys.argv[2] if len(sys.argv) > 2 else "HEAD"

    if base_ref:
        files = run_git_diff(["diff", "--name-only", "--diff-filter=ACMR", base_ref, head_ref, "--"])
    else:
        working = run_git_diff(["diff", "--name-only", "--diff-filter=ACMR", "--"])
        staged = run_git_diff(["diff", "--name-only", "--diff-filter=ACMR", "--cached", "--"])
        files = sorted(set(working + staged))

    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
