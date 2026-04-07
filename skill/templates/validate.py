#!/usr/bin/env python3
"""Validates project documentation manifests against filesystem + cross-refs."""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "documentation"
ADR_DIR = DOCS / "adr"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def collect_all_blocks() -> dict:
    """Load all layer manifests. Returns {block_name: (layer_file, block_data)}."""
    project = load_yaml(DOCS / "project.yaml")
    all_blocks = {}
    for layer_name, layer_path in (project.get("layers") or {}).items():
        layer = load_yaml(ROOT / layer_path)
        for block_name, block_data in (layer.get("blocks") or {}).items():
            if block_name in all_blocks:
                print(f"WARN: duplicate block '{block_name}' across layers")
            all_blocks[block_name] = (layer_path, block_data)
    return all_blocks


def collect_adr_files() -> dict:
    """Returns {adr_number: (path, affects_list)}."""
    if not ADR_DIR.exists():
        return {}
    adrs = {}
    for adr_file in ADR_DIR.glob("*.md"):
        name = adr_file.stem  # e.g. "004-client-side-filtering"
        try:
            num = int(name.split("-")[0])
        except (ValueError, IndexError):
            continue
        affects = []
        with open(adr_file, encoding="utf-8") as f:
            for line in f:
                if line.lower().startswith("affects:"):
                    raw = line.split(":", 1)[1].strip().strip("[]")
                    affects = [x.strip() for x in raw.split(",") if x.strip()]
                    break
        adrs[num] = (adr_file, affects)
    return adrs


def validate() -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    all_blocks = collect_all_blocks()
    all_adrs = collect_adr_files()

    # 1. code_path + entry must exist
    for block_name, (layer, block) in all_blocks.items():
        code_path_str = block.get("code_path", "")
        if not code_path_str:
            errors.append(f"{block_name}: code_path is empty")
            continue
        code_path = ROOT / code_path_str
        if not code_path.exists():
            errors.append(f"{block_name}: code_path not found: {code_path_str}")
            continue
        entry_str = block.get("entry", "")
        if not entry_str:
            errors.append(f"{block_name}: entry field is missing")
            continue
        entry = code_path / entry_str
        if not entry.exists():
            errors.append(f"{block_name}: entry not found: {entry_str}")

    # 2. depends_on / related_blocks point to existing blocks
    for block_name, (_, block) in all_blocks.items():
        for ref_field in ("depends_on", "related_blocks"):
            for ref in block.get(ref_field, []) or []:
                if ref not in all_blocks:
                    errors.append(f"{block_name}.{ref_field}: unknown block '{ref}'")

    # 3. adr: [N] must point to existing ADR files
    for block_name, (_, block) in all_blocks.items():
        for adr_num in block.get("adr", []) or []:
            if adr_num not in all_adrs:
                errors.append(f"{block_name}.adr: ADR-{adr_num:03d} file not found")

    # 4. ADR Affects: must match block.adr (two-way consistency)
    for adr_num, (adr_path, affects) in all_adrs.items():
        for block_ref in affects:
            if block_ref not in all_blocks:
                errors.append(f"ADR-{adr_num:03d} Affects unknown block: {block_ref}")
                continue
            block_adr = all_blocks[block_ref][1].get("adr", []) or []
            if adr_num not in block_adr:
                errors.append(
                    f"ADR-{adr_num:03d} lists '{block_ref}' in Affects, "
                    f"but block doesn't reference adr: [{adr_num}]"
                )

    # 5. Warnings for empty critical fields
    for block_name, (_, block) in all_blocks.items():
        summary = block.get("summary", "") or ""
        if not summary or "TODO" in summary.upper():
            warnings.append(f"{block_name}: summary is empty or TODO")

    # 6. Orphan detection — folders not covered by any manifest block
    covered_paths = set()
    parent_dirs = set()
    for block_name, (_, block) in all_blocks.items():
        cp = block.get("code_path", "")
        if cp:
            covered_paths.add(Path(cp).as_posix())
            parent_dirs.add(Path(cp).parent.as_posix())

    for parent in parent_dirs:
        parent_path = ROOT / parent
        if not parent_path.exists():
            continue
        for child in sorted(parent_path.iterdir()):
            if not child.is_dir():
                continue
            relative = child.relative_to(ROOT).as_posix()
            if relative not in covered_paths:
                warnings.append(f"orphan: {relative} not in any manifest block")

    return errors, warnings


if __name__ == "__main__":
    errors, warnings = validate()
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("OK: all manifests valid")
