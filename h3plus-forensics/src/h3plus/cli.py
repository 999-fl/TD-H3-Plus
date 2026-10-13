"""Command line interface for the H3 Plus analysis scaffolding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h3plus.compare_versions import compare_files
from h3plus.entropy import entropy_for_file
from h3plus.inventory import discover_files, write_inventory_csv, write_inventory_json
from h3plus.firmware_package import component_manifest
from h3plus.pe_analysis import inspect_pe
from h3plus.reporting import write_summary
from h3plus.string_extract import extract_strings
from h3plus.ui_patch import patch_single_ascii_label


def cmd_inventory(args: argparse.Namespace) -> None:
    """Generate inventory outputs for a directory."""
    inventory = write_inventory_json(args.directory, args.output_json)
    write_inventory_csv(args.directory, args.output_csv)
    print(json.dumps({"count": inventory["count"], "output_json": str(args.output_json)}, indent=2))


def cmd_inspect(args: argparse.Namespace) -> None:
    """Inspect one file and dump a minimal manifest."""
    manifest = component_manifest(args.file, [(0, args.file_size)])
    print(json.dumps(manifest, indent=2))


def cmd_compare(args: argparse.Namespace) -> None:
    """Compare two input files."""
    print(json.dumps(compare_files(args.file_a, args.file_b), indent=2))


def cmd_strings(args: argparse.Namespace) -> None:
    """Extract printable strings from a file."""
    print(json.dumps(extract_strings(args.file), indent=2))


def cmd_analyze(args: argparse.Namespace) -> None:
    """Run a minimal analysis summary."""
    files = discover_files(args.directory)
    items = "\n".join(f"- {item['path']} ({item['size_bytes']} bytes)" for item in files[:20])
    summary = (
        "H3 Plus analysis scaffold\n"
        "========================\n"
        f"Files discovered: {len(files)}\n\n"
        f"Sample files:\n{items}\n\n"
        f"Entropy sample: {entropy_for_file(files[0]['path']) if files else 0}\n"
    )
    write_summary(args.output, summary)
    print(summary)


def cmd_patch_spectrum_label(args: argparse.Namespace) -> None:
    """Patch the Spectrum UI label with strict source guards."""
    result = patch_single_ascii_label(
        args.source,
        args.output,
        search_text=args.search_text,
        replacement_text=args.replacement_text,
        expected_sha256=args.expected_sha256,
        expected_offset=args.expected_offset,
    )
    result["offset_hex"] = f"0x{result['offset']:X}"
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="H3 Plus forensic analysis CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inv = subparsers.add_parser("inventory", help="Inventory a directory")
    inv.add_argument("directory")
    inv.add_argument("--output-json", default="results/inventory.json")
    inv.add_argument("--output-csv", default="results/inventory.csv")
    inv.set_defaults(func=cmd_inventory)

    inspect = subparsers.add_parser("inspect", help="Inspect a firmware file")
    inspect.add_argument("file")
    inspect.add_argument("--file-size", type=int, default=None)
    inspect.set_defaults(func=cmd_inspect)

    compare = subparsers.add_parser("compare", help="Compare two files")
    compare.add_argument("file_a")
    compare.add_argument("file_b")
    compare.set_defaults(func=cmd_compare)

    strings = subparsers.add_parser("strings", help="Extract strings from one file")
    strings.add_argument("file")
    strings.set_defaults(func=cmd_strings)

    analyze = subparsers.add_parser("analyze", help="Run a minimal analysis over a directory")
    analyze.add_argument("directory")
    analyze.add_argument("--output", default="results/summary.txt")
    analyze.set_defaults(func=cmd_analyze)

    patch = subparsers.add_parser(
        "patch-spectrum-label",
        help="Patch Spectrum label in a copied decrypted app image",
    )
    patch.add_argument("source", help="Source decrypted app image")
    patch.add_argument("output", help="Output patched image path")
    patch.add_argument("--search-text", default="Spectrum")
    patch.add_argument("--replacement-text", default="SpecView")
    patch.add_argument(
        "--expected-sha256",
        default="819d1ad327954e2a76f792d90340a50061f026cb7d3b61a37ece591c5636ea1d",
    )
    patch.add_argument("--expected-offset", type=lambda value: int(value, 0), default=0x8A2CC)
    patch.set_defaults(func=cmd_patch_spectrum_label)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
