"""Reporting helpers for generating human-readable findings."""

from __future__ import annotations

from pathlib import Path


def write_summary(path: str | Path, text: str) -> None:
    """Write a text file containing the report summary."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
