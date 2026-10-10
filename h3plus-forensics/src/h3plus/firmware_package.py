"""Firmware-package layout and static inspection helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def read_bytes(path: str | Path) -> bytes:
    """Read a file without modifying source data."""
    return Path(path).read_bytes()


def file_size(path: str | Path) -> int:
    """Return the size in bytes for a file."""
    return Path(path).stat().st_size


def sha256_hex(blob: bytes) -> str:
    """Return a SHA-256 hex digest."""
    return hashlib.sha256(blob).hexdigest()


def printable_strings(blob: bytes, min_len: int = 4) -> list[tuple[int, str]]:
    """Extract printable ASCII sequences with their offsets."""
    out: list[tuple[int, str]] = []
    current: list[int] = []
    current_offset = 0
    for offset, value in enumerate(blob):
        if 32 <= value < 127:
            current.append(value)
        else:
            if len(current) >= min_len:
                out.append((offset - len(current), bytes(current).decode("ascii", errors="ignore")))
            current = []
    if len(current) >= min_len:
        out.append((current_offset, bytes(current).decode("ascii", errors="ignore")))
    return out


def component_manifest(path: str | Path, boundaries: list[tuple[int, int]]) -> dict[str, Any]:
    """Build a manifest entry for a file using explicit ranges."""
    blob = read_bytes(path)
    file_size_bytes = len(blob)
    components = []
    unaccounted: list[list[int]] = []
    validation_errors: list[str] = []
    next_cursor = 0
    for index, (start, end) in enumerate(boundaries, start=1):
        if start != next_cursor:
            unaccounted.append([next_cursor, start])
            validation_errors.append(f"gap or overlap around component {index}: expected start {next_cursor:#x}, got {start:#x}")
        if end > file_size_bytes:
            validation_errors.append(f"component {index} exceeds file size: end {end:#x} > {file_size_bytes:#x}")
        chunk = blob[start:end]
        components.append(
            {
                "name": f"component_{index}",
                "start_offset": start,
                "end_offset_exclusive": end,
                "length_bytes": len(chunk),
                "sha256": sha256_hex(chunk),
                "boundary_confidence": "hypothesis",
                "notes": [],
            }
        )
        next_cursor = end
    if next_cursor != file_size_bytes:
        unaccounted.append([next_cursor, file_size_bytes])
        validation_errors.append(f"unaccounted bytes remain: {next_cursor:#x} to {file_size_bytes:#x}")
    return {
        "source_file": str(path),
        "size_bytes": file_size_bytes,
        "sha256": sha256_hex(blob),
        "components": components,
        "unaccounted_ranges": unaccounted,
        "validation_errors": validation_errors,
    }


def write_manifest(path: str | Path, raw_manifest: dict[str, Any]) -> None:
    """Persist a manifest as JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(raw_manifest, indent=2), encoding="utf-8")
