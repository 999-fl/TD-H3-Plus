"""String extraction helpers for ASCII and UTF-16 text."""

from __future__ import annotations

from pathlib import Path


def extract_ascii_strings(blob: bytes, min_len: int = 4) -> list[tuple[int, str]]:
    """Return printable ASCII strings with offsets."""
    out: list[tuple[int, str]] = []
    current = bytearray()
    for offset, value in enumerate(blob):
        if 32 <= value < 127:
            current.append(value)
        else:
            if len(current) >= min_len:
                out.append((offset - len(current), current.decode("ascii", errors="ignore")))
            current.clear()
    if len(current) >= min_len:
        out.append((len(blob) - len(current), current.decode("ascii", errors="ignore")))
    return out


def extract_utf16le_strings(blob: bytes, min_len: int = 2) -> list[tuple[int, str]]:
    """Return UTF-16LE strings with offsets, when valid."""
    out: list[tuple[int, str]] = []
    for offset in range(0, len(blob) - 1, 2):
        chunk = blob[offset : offset + 2]
        if chunk[0] == 0x00 and chunk[1] == 0x00:
            continue
        try:
            text = chunk.decode("utf-16le")
        except UnicodeDecodeError:
            continue
        if len(text) >= min_len and all(32 <= ord(ch) < 127 or ch in "\r\n\t" for ch in text):
            out.append((offset, text))
    return out


def extract_strings(path: str | Path) -> dict[str, list[tuple[int, str]]]:
    """Extract ASCII and UTF-16 strings from a file."""
    blob = Path(path).read_bytes()
    return {
        "ascii": extract_ascii_strings(blob),
        "utf16le": extract_utf16le_strings(blob),
    }
