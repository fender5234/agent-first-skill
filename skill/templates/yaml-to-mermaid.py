#!/usr/bin/env python3
"""Generates a Mermaid dependency graph from YAML manifests.

Usage:
    python yaml-to-mermaid.py [--output <file>]

Reads documentation/project.yaml, loads all layer manifests,
and outputs a Mermaid graph of depends_on and related_blocks.
"""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "documentation"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def collect_blocks() -> dict:
    project = load_yaml(DOCS / "project.yaml")
    all_blocks = {}
    for layer_name, layer_path in (project.get("layers") or {}).items():
        layer = load_yaml(ROOT / layer_path)
        for block_name, block_data in (layer.get("blocks") or {}).items():
            all_blocks[block_name] = (layer_name, block_data)
    return all_blocks


def generate_mermaid(all_blocks: dict) -> str:
    lines = ["graph LR"]

    # Group blocks by layer using subgraphs
    layers = {}
    for block_name, (layer_name, _) in all_blocks.items():
        layers.setdefault(layer_name, []).append(block_name)

    for layer_name, blocks in layers.items():
        lines.append(f"    subgraph {layer_name}")
        for b in blocks:
            summary = all_blocks[b][1].get("summary", "")
            label = f'{b}["{b}<br/><small>{summary}</small>"]'
            lines.append(f"        {label}")
        lines.append("    end")

    # Edges: depends_on = solid arrow, related_blocks = dashed
    for block_name, (_, block_data) in all_blocks.items():
        for dep in block_data.get("depends_on", []) or []:
            if dep in all_blocks:
                lines.append(f"    {block_name} --> {dep}")
        for rel in block_data.get("related_blocks", []) or []:
            if rel in all_blocks:
                lines.append(f"    {block_name} -.-> {rel}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate Mermaid graph from YAML manifests")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    all_blocks = collect_blocks()
    if not all_blocks:
        print("No blocks found. Check documentation/project.yaml and layer manifests.")
        sys.exit(1)

    mermaid = generate_mermaid(all_blocks)

    if args.output:
        Path(args.output).write_text(f"```mermaid\n{mermaid}\n```\n", encoding="utf-8")
        print(f"Mermaid graph written to {args.output} ({len(all_blocks)} blocks)")
    else:
        print(mermaid)


if __name__ == "__main__":
    main()
