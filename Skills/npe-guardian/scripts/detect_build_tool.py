#!/usr/bin/env python3
from pathlib import Path
import sys


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    if (root / "pom.xml").exists():
        print("maven")
        return 0

    gradle_files = (
        "build.gradle",
        "build.gradle.kts",
        "settings.gradle",
        "settings.gradle.kts",
    )
    if any((root / name).exists() for name in gradle_files):
        print("gradle")
        return 0

    print("unknown")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
