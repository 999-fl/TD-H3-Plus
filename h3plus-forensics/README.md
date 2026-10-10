# H3 Plus Firmware Forensics

This repository contains the original evidence files under `H3 Plus 0226/...` and a Python analysis scaffold intended for further forensic work.

The repository was reviewed through the GitHub API only; the environment available to this session did not include a local PE inspection toolchain or a full Python runtime. That limitation is captured in the generated `results/*.json` and `results/*.txt` outputs.

## Scope of the evidence reviewed

The repo includes:
- Three Type-C firmware packages: `TID-H3-PlusV1.0.43.fw`, `TID-H3-PlusV1.0.45.fw`, `TID-H3-Plus-1.0.47.fw`
- Three standalone `.bin` files in the legacy updater folder: `TID-H3-PlusV1.0.43.bin`, `TID-H3-PlusV1.0.45.bin`, `TID-H3-Plus-1.0.47.bin`
- Updater binaries: `H3 Plus updata.exe` and `Update App.exe`
- Documentation and an update note: `1.0.45 Updated content.txt`

The actual forensic investigation is intentionally evidence-based and conservative. Claims that require binary-level parsing or PE inspection remain marked as unverified unless they are directly supported by repo artifacts.

## Project structure

- `src/h3plus/` – reusable forensic utilities
- `tests/` – synthetic unit tests for parsing and comparison logic
- `results/` – inventory, format, and verification outputs derived from the repository evidence
- `docs/` – technical findings and investigation notes

## Quick start

```bash
cd h3plus-forensics
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m h3plus.cli inventory "/path/to/input-directory"
```

## Important note

The early findings listed in the investigation brief are treated as hypotheses, not accepted facts. The outputs in this repo record only what is directly verifiable from the repository contents available in this session.
