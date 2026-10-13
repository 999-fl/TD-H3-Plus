"""Helpers for guarded, reversible UI string patching."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 digest of a file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def patch_single_ascii_label(
    source_path: str | Path,
    output_path: str | Path,
    *,
    search_text: str,
    replacement_text: str,
    expected_sha256: str | None = None,
    expected_offset: int | None = None,
) -> dict[str, int | str]:
    """Patch one ASCII label in a copied firmware blob with strict guards."""
    if len(search_text) != len(replacement_text):
        raise ValueError("search_text and replacement_text must have identical length")

    source = Path(source_path)
    data = source.read_bytes()

    if expected_sha256:
        observed_sha256 = hashlib.sha256(data).hexdigest()
        if observed_sha256.lower() != expected_sha256.lower():
            raise ValueError(
                f"source hash mismatch: expected {expected_sha256}, observed {observed_sha256}"
            )

    search_bytes = search_text.encode("ascii")
    replacement_bytes = replacement_text.encode("ascii")

    first_index = data.find(search_bytes)
    if first_index < 0:
        raise ValueError(f"search text not found: {search_text!r}")
    second_index = data.find(search_bytes, first_index + 1)
    if second_index >= 0:
        raise ValueError(f"search text is not unique: {search_text!r}")

    if expected_offset is not None and first_index != expected_offset:
        raise ValueError(
            f"offset mismatch: expected 0x{expected_offset:X}, observed 0x{first_index:X}"
        )

    patched = bytearray(data)
    patched[first_index : first_index + len(search_bytes)] = replacement_bytes

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(patched)

    return {
        "offset": first_index,
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "output_sha256": hashlib.sha256(patched).hexdigest(),
        "search_text": search_text,
        "replacement_text": replacement_text,
    }
