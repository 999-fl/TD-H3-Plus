"""Compare two firmware versions at the byte level."""

from __future__ import annotations

import hashlib
from pathlib import Path


def file_sha256(path: str | Path) -> str:
    """Compute a SHA-256 for a file."""
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compare_files(path_a: str | Path, path_b: str | Path) -> dict[str, object]:
    """Compare two files and summarize the byte-level differences."""
    a = Path(path_a).read_bytes()
    b = Path(path_b).read_bytes()
    if len(a) != len(b):
        differing_ranges = [(0, min(len(a), len(b)))]
    else:
        differing_ranges = []
        start = None
        for index, (left, right) in enumerate(zip(a, b)):
            if left != right:
                if start is None:
                    start = index
                continue
            if start is not None:
                differing_ranges.append((start, index))
                start = None
        if start is not None:
            differing_ranges.append((start, len(a)))
    return {
        "a": str(path_a),
        "b": str(path_b),
        "size_a": len(a),
        "size_b": len(b),
        "sha256_a": file_sha256(path_a),
        "sha256_b": file_sha256(path_b),
        "same_size": len(a) == len(b),
        "same_file": a == b,
        "difference_ranges": differing_ranges,
    }
