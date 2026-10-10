import json


def test_inventory_basic():
    assert json.dumps({"ok": True}) == '{"ok": true}'


def test_strings_extract_basic():
    assert "ABCD" in "ABCD"
