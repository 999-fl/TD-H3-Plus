# H3 Plus investigation log

- 2026-10-10: Inspected repository tree via GitHub API and observed the available evidence set.
- 2026-10-10: Confirmed the presence of three firmware packages and three standalone .bin files.
- 2026-10-10: Confirmed the presence of both `H3 Plus updata.exe` and `Update App.exe`.
- 2026-10-10: Reviewed the note file `1.0.45 Updated content.txt`; it documents version updates but does not establish binary structure.
- 2026-10-10: No local Windows PE tooling or Python runtime was available in this session, so the project was scaffolded and documented conservatively.
- 2026-10-12: Re-audited the checked-out repository with local Python 3, `sha256sum`, `file`, and `unzip`.
- 2026-10-12: Verified the pristine v1.0.47 standalone image at 790,528 bytes with SHA-256 `3b2d198b6d6bcce884ea437cccb253efd705ab72c790c04b704c3da75213deda`; no bytes were changed.
- 2026-10-12: Confirmed the v1.0.50 Type-C candidate is `TD-H3-PlusV1.0.50.fw` (827,808 bytes, SHA-256 `ab843948ab79871ae911f74688208096b1438d16e660783e7c3adcf3acf416d8`) and the Kenwood candidate is `TD-H3-PlusV1.0.50.bin` (823,296 bytes, SHA-256 `0dd16ac8a26b58ef62c4681ac8ee018cfd6a276b81eb2049b33f834da016b40e`). They have different first bytes and no aligned identity was established; treat them as separate, unverified update artifacts rather than interchangeable images.
- 2026-10-12: The bundled Type-C instructions require PTT+3 and `Update App.exe`; the Kenwood instructions require PTT+1, a CH340 serial path, `updata.exe`, baud 1,000,000, and explicitly say not to update UBOOT. This supports distinct delivery paths, not binary compatibility.
- 2026-10-12: `decrypted_app.bin` exists at 802,784 bytes with SHA-256 `819d1ad327954e2a76f792d90340a50061f026cb7d3b61a37ece591c5636ea1d`. It contains one ASCII `1.0.50` marker at offset `0x9B871` and `TD-H3` markers, but no source manifest or byte-for-byte relationship to either candidate was found. Classification: **SUPPORTED HYPOTHESIS** for v1.0.50 application; provenance and compatibility remain **UNKNOWN**.
- 2026-10-12: Added the measured hashes and artifact paths to `results/input_hashes.sha256`. No firmware, updater, or decrypted image was modified.
- 2026-10-12: Validation passed: `sha256sum -c results/input_hashes.sha256` (6/6), `python3 -m compileall` (pass), `pytest -q` (7 passed), comparison CLI smoke check (pass), and `git diff --check` (pass). `pytest` was installed from the existing `requirements.txt` because it was absent from the environment.
