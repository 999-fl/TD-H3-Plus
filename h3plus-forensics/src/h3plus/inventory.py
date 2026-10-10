"""Inventory generation for repository artifacts.

This module is intentionally small and deterministic. It can recursively enumerate files,
collect metadata, and classify likely firmware/updater inputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def sha256_bytes(data: bytes) -> str:
    """Return the hex digest for a byte string."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 of a file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_files(root: str | Path) -> list[dict[str, Any]]:
    """Recursively list files and metadata."""
    entries: list[dict[str, Any]] = []
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file():
            continue
        entries.append(
            {
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return entries


def classify_path(path: str) -> str:
    """Best-effort classification for firmware-like files."""
    lower = path.lower()
    if lower.endswith(".fw"):
        return "firmware_package"
    if lower.endswith(".bin"):
        return "standalone_bin"
    if lower.endswith(".exe"):
        return "windows_executable"
    if lower.endswith(".dll"):
        return "windows_dll"
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".txt"):
        return "text"
    return "other"


def write_inventory_json(root: str | Path, output_path: str | Path) -> dict[str, Any]:
    """Write a JSON inventory for the input directory."""
    items = discover_files(root)
    payload = {
        "root": str(root),
        "files": items,
        "count": len(items),
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def write_inventory_csv(root: str | Path, output_path: str | Path) -> list[dict[str, Any]]:
    """Write a CSV inventory for the input directory."""
    rows = discover_files(root)
    fields = ["path", "size_bytes", "sha256", "classification"]
    with Path(output_path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            row["classification"] = classify_path(row["path"])
            writer.writerow({k: row.get(k, "") for k in fields})
    return rows
