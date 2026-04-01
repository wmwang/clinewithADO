#!/usr/bin/env python3
from pathlib import Path
import re
import sys


BUILD_FILES = (
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
)


PATTERNS = {
    "spotbugs": re.compile(r"spotbugs|com\.github\.spotbugs", re.IGNORECASE),
    "nullaway": re.compile(r"NullAway|error_prone|errorprone|Xep:NullAway", re.IGNORECASE),
    "checker_framework": re.compile(
        r"checkerframework|org\.checkerframework|NullnessChecker", re.IGNORECASE
    ),
}


def read_build_text(root: Path) -> str:
    chunks = []
    for name in BUILD_FILES:
        path = root / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    text = read_build_text(root)

    flags = {
        key: 1 if pattern.search(text) else 0
        for key, pattern in PATTERNS.items()
    }

    print(f"spotbugs={flags['spotbugs']}")
    print(f"nullaway={flags['nullaway']}")
    print(f"checker_framework={flags['checker_framework']}")

    if flags["checker_framework"]:
        print("recommended_mode=deep")
    elif flags["nullaway"]:
        print("recommended_mode=strict")
    else:
        print("recommended_mode=fast")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
