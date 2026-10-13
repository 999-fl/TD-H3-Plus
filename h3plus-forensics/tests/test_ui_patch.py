import hashlib

import pytest

from h3plus.ui_patch import patch_single_ascii_label


def test_patch_single_ascii_label_updates_expected_offset(tmp_path):
    source = tmp_path / "input.bin"
    output = tmp_path / "output.bin"
    source.write_bytes(b"\x00\x01Spectrum\x00tail")

    result = patch_single_ascii_label(
        source,
        output,
        search_text="Spectrum",
        replacement_text="SpecView",
        expected_offset=2,
        expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    )

    assert result["offset"] == 2
    assert b"SpecView" in output.read_bytes()
    assert b"Spectrum" not in output.read_bytes()


def test_patch_single_ascii_label_rejects_hash_mismatch(tmp_path):
    source = tmp_path / "input.bin"
    output = tmp_path / "output.bin"
    source.write_bytes(b"Spectrum")

    with pytest.raises(ValueError, match="source hash mismatch"):
        patch_single_ascii_label(
            source,
            output,
            search_text="Spectrum",
            replacement_text="SpecView",
            expected_sha256="00" * 32,
        )
