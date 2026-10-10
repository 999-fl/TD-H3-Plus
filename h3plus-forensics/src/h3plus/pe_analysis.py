"""Very small PE parsing scaffolding.

The goal is to make the static-analysis workflow explicit and structured without
executing untrusted binaries.
"""

from __future__ import annotations

from pathlib import Path


def inspect_pe(path: str | Path) -> dict[str, object]:
    """Return a minimal PE-validation summary.

    This function intentionally avoids executing the file. It only checks whether the
    file begins with the expected MZ signature and returns an explicit note when a PE
    structure is not present.
    """
    blob = Path(path).read_bytes()
    if len(blob) < 2:
        return {"is_pe": False, "reason": "file too small"}
    if blob[:2] != b"MZ":
        return {"is_pe": False, "reason": "missing MZ header"}
    e_lfanew = int.from_bytes(blob[0x3C:0x40], "little")
    if e_lfanew + 4 > len(blob):
        return {"is_pe": False, "reason": "PE header offset out of range"}
    return {
        "is_pe": blob[e_lfanew : e_lfanew + 4] == b"PE\x00\x00",
        "e_lfanew": e_lfanew,
        "size_bytes": len(blob),
        "notes": ["PE detection performed statically without execution"],
    }
