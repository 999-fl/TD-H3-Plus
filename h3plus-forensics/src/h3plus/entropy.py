"""Entropy and byte-distribution utilities."""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path


def shannon_entropy(blob: bytes) -> float:
    """Compute Shannon entropy for a byte buffer."""
    if not blob:
        return 0.0
    counts = Counter(blob)
    total = len(blob)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def entropy_for_file(path: str | Path) -> float:
    """Compute the entropy of a file."""
    return shannon_entropy(Path(path).read_bytes())
