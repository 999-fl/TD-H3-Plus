# Format findings

## Verified repository findings

The repo contains three firmware packages and the corresponding standalone `.bin` files for the same release order. The versions are 1.0.43, 1.0.45, and 1.0.47.

The sizes observed in the repository are:

- `TID-H3-PlusV1.0.43.fw` = 1,068,896 bytes
- `TID-H3-PlusV1.0.45.fw` = 1,072,992 bytes
- `TID-H3-Plus-1.0.47.fw` = 1,081,184 bytes
- `TID-H3-PlusV1.0.43.bin` = 778,240 bytes
- `TID-H3-PlusV1.0.45.bin` = 782,336 bytes
- `TID-H3-Plus-1.0.47.bin` = 790,528 bytes

These numbers are consistent with the earlier investigation note that the standalone `.bin` files are version-specific and not identical in size.

## What remains unverified

The following items require a local ELF/PE or firmware parser and cannot be accepted as confirmed from the repo alone:

- 1,024-byte header boundaries
- embedded component offsets such as `0x400`, `0xC1400`
- file-level checksum validation
- PE imports such as `CryptDecrypt` and `CryptCreateHash`
- any file magic values inside the firmware payloads

The repo does contain an updater binary and a legacy updater binary, but no extracted PE reports, import tables, or Ghidra databases are checked in.

## Conclusion

The repo is suitable for firmware forensics work, but the actual binary structure and updater internals remain unresolved without a local static-analysis environment.
