#!/usr/bin/env python3
"""
COSYmanuals Raw Dumps Check Script
----------------------------------
Scans all files under manuals/ (.html and .md) for raw unparsed teacher_notes dumps.
Fails with exit code 1 if any file contains:
  - 'pronunciation: [{',
  - '&quot;point&quot;',
  - or a line starting with 'code: "' or 'code: &quot;'
Exits with code 0 if all files under manuals/ are clean.
"""

import sys
from pathlib import Path

FORBIDDEN_CONTAINS = [
    'pronunciation: [{',
    '&quot;point&quot;',
]


def check_file(filepath):
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    violations = []
    for pattern in FORBIDDEN_CONTAINS:
        if pattern in content:
            violations.append(pattern)

    for line in content.splitlines():
        l = line.strip()
        if l.startswith('code: "') or l.startswith('code: &quot;') or l.startswith("code: '"):
            violations.append(l[:30])
            break

    return violations


def main():
    manuals_dir = Path("manuals")
    if not manuals_dir.exists():
        print("Error: manuals directory not found.")
        sys.exit(1)

    files = sorted(list(manuals_dir.glob("**/*")))
    target_files = [f for f in files if f.is_file() and f.suffix in ('.html', '.md')]

    failures = {}
    for filepath in target_files:
        violations = check_file(filepath)
        if violations:
            failures[str(filepath)] = violations

    if failures:
        print(f"\n❌ FAIL: Found raw teacher_notes dumps in {len(failures)} files under manuals/:")
        for filepath, patterns in failures.items():
            print(f"  - {filepath}: {', '.join(patterns)}")
        sys.exit(1)
    else:
        print(f"\n✅ PASS: Scanned {len(target_files)} files under manuals/. All files are clean of raw dumps.")
        sys.exit(0)


if __name__ == "__main__":
    main()
