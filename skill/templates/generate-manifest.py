#!/usr/bin/env python3
"""Scans a directory and generates a skeleton layer.yaml manifest.

Usage:
    python generate-manifest.py <scan_dir> [--output <file>]

Examples:
    python generate-manifest.py src/features
    python generate-manifest.py src/features --output documentation/frontend.yaml
"""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

ENTRY_CANDIDATES = [
    "index.ts", "index.tsx", "index.js", "index.jsx",
    "main.py", "__init__.py", "app.py",
    "mod.rs", "lib.rs", "main.rs",
    "main.go",
]


def find_entry(folder: Path) -> str:
    for candidate in ENTRY_CANDIDATES:
        if (folder / candidate).exists():
            return candidate
    # Fallback: first file in folder
    files = sorted(f for f in folder.iterdir() if f.is_file())
    return files[0].name if files else "TODO"


def scan_directory(scan_dir: Path) -> dict:
    blocks = {}
    for child in sorted(scan_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name == "__pycache__":
            continue
        block_name = child.name
        entry = find_entry(child)
        blocks[block_name] = {
            "code_path": child.as_posix(),
            "entry": entry,
            "summary": "TODO: describe this block",
            "depends_on": [],
            "related_blocks": [],
            "api_calls": [],
            "adr": [],
            "gotchas": [],
            "notes": "",
            "last_modified_context": "",
        }
    return blocks


def main():
    parser = argparse.ArgumentParser(description="Generate skeleton layer.yaml from directory")
    parser.add_argument("scan_dir", help="Directory to scan for blocks")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    scan_dir = Path(args.scan_dir)
    if not scan_dir.exists():
        print(f"ERROR: {scan_dir} does not exist")
        sys.exit(1)

    blocks = scan_directory(scan_dir)
    if not blocks:
        print(f"No subdirectories found in {scan_dir}")
        sys.exit(1)

    manifest = {"blocks": blocks}
    output = yaml.dump(manifest, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(f"# Map of blocks — generated skeleton, review and fill in\n{output}", encoding="utf-8")
        print(f"Generated {args.output} with {len(blocks)} blocks")
    else:
        print(output)


if __name__ == "__main__":
    main()
