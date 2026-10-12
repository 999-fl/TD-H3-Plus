# CYBER-H3 / TIDRADIO TD-H3 Plus --- Master AI Handoff

**Last consolidated:** 2026-10-12\
**Status:** Reverse-engineering and validation tooling has improved, but no radio-feature firmware patch has been implemented or hardware-validated. The original v1.0.47 image was reported unchanged in earlier checks; re-verify its hash before future work. The principal technical blocker remains the insufficiently understood JieLi PI32v2 ROM/platform-service ABI, especially RF-related service contracts. The Library also contains candidate v1.0.50 update archives and a file named `decrypted_app.bin`; their contents, target variant, provenance, and hashes still need to be checked before use.

## 0. Instructions to every future AI

This file is the continuity source for separate AI models and
conversations. Read it before proposing work. First inspect the real
repository state and current Git diff; this document records the last
known state and may become stale.

-   The user wants concrete progress, not repeated general analysis or
    duplicate reports.
-   Prefer a small, reversible, justified code change or a focused
    experiment that resolves one specific blocker.
-   Preserve existing tools and features. Do not downgrade to an
    older/smaller version of the project.
-   Keep firmware versions strictly separate. Never reuse v1.0.50
    offsets, bytes, or assumptions for v1.0.47 without independent
    proof.
-   Never modify the original firmware. Patch a separate copy, check
    exact expected bytes, and provide rollback.
-   Never flash speculative code. A decrypted/patched app is not
    necessarily a valid complete firmware package.
-   Do not claim hardware success without actual device testing.
-   Label claims as **verified**, **inference**, **hypothesis**, or
    **unknown**. Do not turn a string/menu entry into proof that a
    feature works.
-   User prefers concise, practical ordinary replies. This handoff is
    deliberately detailed.
-   When the user gives a project update, update this file with the new
    date, facts, changed files, exact commands, hashes, test outputs,
    hardware observations, blockers, and next action. Preserve useful
    history. Give the updated `.md` file back to the user.
-   If this file is not available in a later separate conversation, ask
    for the latest copy to be attached before claiming to update it. Do
    not pretend to have access to the user's local repository.

## At-a-glance: current priority order

Use this as the execution queue; the detailed requirements and history
below remain authoritative.

1. **Inspect exact artifacts:** list the local repo state, inspect the candidate v1.0.50 archives and `decrypted_app.bin`, and record hashes, contents, hardware variant, and provenance. Do not assume the filenames identify a compatible target.
2. **Choose one target build:** match the radio's displayed version to its original vendor package and decrypted application. Keep v1.0.47 and v1.0.50 separate.
3. **Map spectrum sweep:** trace entry point → frequency selection/tune → dwell → measurement → scaling/drawing → next point; record evidence and confidence.
4. **Prove a runtime data path:** inspect normal-mode USB and Bluetooth capabilities before designing PC controls or a protocol.
5. **Establish a no-op build/recovery baseline:** prove reproducible packaging and recovery before any feature patch.
6. **Make one reversible change:** only after the function, calling convention, and expected behaviour are understood; test and report exact bytes changed.

**Current boundary:** the menu layout and PC waterfall are plans. No new radio feature, PC stream transport, or hardware-validated patch is established by this document.

## 1. Project identity and objective

**Project:** CYBER-H3 / CYBER-H3 Plus\
**Radio:** TIDRADIO TD-H3 Plus (not the original TD-H3)\
**Repository on user's machine:** `~/jl-uboot-tool/H3Plus`\
**Known original firmware:** `BIN/TID-H3-Plus-1.0.47.bin`

The goal is real custom firmware/modding that improves the radio and
adds useful capabilities, inspired by nicFW-style features. Desired
areas include improved scanning, activity-aware scan workflows,
CTCSS/DCS tone detection/logging if the receiver exposes results,
tuning/frequency-step behavior, signal-meter improvements,
spectrum/activity visualization if technically supported, channel
management, profiles, battery diagnostics, and eventual
PC/CYBERDECK_NODE integration. These are goals, not claims of
feasibility or current implementation.

A menu, string, resource, or static UI is not a working feature. A
meaningful implementation should trace the UI entry point through
callers to the actual service/hardware path, understand the ABI, include
a minimal version-locked patch and rollback, pass tests, have a
validated package/rebuild path, and be tested on the actual radio before
claiming hardware success.

## 2. Firmware identity and version discipline

### v1.0.47 (known original)

-   Path: `BIN/TID-H3-Plus-1.0.47.bin`
-   Size: **790,528 bytes**
-   SHA-256:
    `3b2d198b6d6bcce884ea437cccb253efd705ab72c790c04b704c3da75213deda`
-   Previously decrypted app path: `/tmp/h3plus-1.0.47-app.bin` (may be
    ephemeral; verify existence and provenance).
-   The original v1.0.47 hash was reported unchanged after earlier
    analysis/tooling work.
-   No firmware bytes were changed as of this handoff.

### v1.0.50

A v1.0.50 decrypted image was involved in service-trace test work. The Library currently contains two archives named `H3_Plus_1.0.50-Update-Kendwood_...zip` and `H3_Plus_1.0.50-Update-TypeC_...zip`, plus a file named `decrypted_app.bin`. These names suggest candidate artifacts, but their contents and relationship to the test image have not yet been verified. Inspect archive contents, identify the exact hardware/update variant, record hashes and provenance, and match the decrypted app to its source before use. The existence of these files does not authorize cross-version patches.

### Rules

-   Each firmware version is a separate target.
-   Verify the full image identity/hash and exact original bytes before
    patching.
-   Wrong-version input must fail closed.
-   Never overwrite `BIN/TID-H3-Plus-1.0.47.bin`.
-   Do not confuse encrypted package/container, decrypted app, internal
    ROM dump, and runtime memory dump.
-   Never assume a patched decrypted app can be repacked or flashed
    without proving packaging, encryption, checksums/signatures, and
    device acceptance.

## 3. Repository and known tools

Repository root: `~/jl-uboot-tool/H3Plus`

Known files/tools from prior work (verify current tree; this is not
guaranteed exhaustive):

``` text
BIN/TID-H3-Plus-1.0.47.bin

tools/
  jl_sfcenc.py
  strings.py
  findva.py
  pi32dis.py
  xref.py
  freespace.py
  patch_h3plus_firmware_bluetooth.py
  verify_actions.py
  verify_cli.py
  test_service_trace.py

findings/
  nicfw-feature-static-analysis.md
  28-nicfw-feature-trace.md
  29-v047-nicfw-validation.md
  Findings.md
  18-open-questions-next-steps.md
  17-tooling-index.md
  [additional service-trace findings may exist]
```

Probable tool roles based on prior usage and filenames. **Inspect each
script before relying on it; these roles are not independently verified
by this document.**

- `jl_sfcenc.py` — JieLi SFC firmware/container encryption or decryption.
- `strings.py` — extract and search strings.
- `findva.py` — map or look up virtual addresses.
- `pi32dis.py` — PI32/JieLi disassembly.
- `xref.py` — cross-reference support.
- `freespace.py` — inspect image layout/free space.
- `patch_h3plus_firmware_bluetooth.py` — existing version-sensitive patch; inspect its guards and exact target before use.
- `verify_actions.py` — validate action mappings.
- `verify_cli.py` — validation CLI; reported to support `--source` for direct `.bin`/`.fw` validation without assuming an internal dump exists.
- `test_service_trace.py` — service-trace assertions for decrypted v1.0.47/v1.0.50 images.

Before work, run/inspect current `git status --short`,
`git diff --stat`, `git diff`, repository instructions such as
`AGENTS.md`/README if present, and the latest relevant findings. Do not
overwrite newer work.

## 4. Last known work and reported test results

The recent changes were mainly tooling and analysis, not radio
features: - Fixed service-trace context alignment. - Added/updated
`tools/test_service_trace.py` assertions for decrypted v1.0.47 and
v1.0.50 images. - Enhanced `tools/verify_cli.py` with `--source` direct
`.bin`/`.fw` validation without inventing a missing internal dump. -
Wrong-version input reportedly rejected. - Service-trace assertions
reportedly passed. - `verify_actions.py`: PASS, `FAILURES: 0`. -
Direct-source `verify_cli.py`: PASS, `FAILURES: 0`. - Python
compilation: PASS. - `git diff --check`: PASS. - Original v1.0.47
SHA-256 reportedly unchanged. - `Dumps/dump_internal.bin` is absent. -
No firmware bytes changed, no radio flashed, no new feature demonstrated
on hardware.

These are historical reported results, not guaranteed current results.
Re-run relevant checks before certifying the current working tree.

## 5. Most important findings

### 5.1 Platform / architecture

The TD-H3 Plus appears to use JieLi `pi32v2`. References previously
identified: - https://kagaimiq.github.io/jielie/cpu/pi32v2.html -
https://github.com/quarkslab/ghidra-jieli

These help validate instruction decoding and processor support; they do
not by themselves establish the target firmware's ROM/platform-service
ABI. Confirm architecture, endianness, address mapping, and instruction
boundaries on the actual image.

### 5.2 Primary blocker: ROM/platform-service ABI

The application uses platform/ROM services, but the exact calling
convention and RF-related contracts are not understood well enough.
Unknowns include service IDs or jump-table mapping, argument
registers/stack layout, return values, side effects, ownership of state,
and receiver/tuning APIs.

Without this knowledge, a patch may call the wrong service, pass bad
arguments, misread a return value, corrupt state, crash, or update UI
without changing RF behavior. Be precise: missing
`Dumps/dump_internal.bin` is a fact and may be useful, but it has not
been proven to be the only route to solving the ABI. The real blocker is
insufficiently established service behavior and calling contracts in
available evidence.

### 5.3 Signal meter / S-meter (v1.0.47 evidence)

-   Conversion at VA `0x01E5057A`: reported expression
    `(value >> 1) - 0xA0`.
-   Threshold-related locations: `0x01E505BA` and `0x01E505D6`.
-   UI/resource references: `signal_icon` VA `0x01E97AB4`, `signal_area`
    VA `0x01E97AD8`, `signal_strength` VA `0x01E98020`.

The source and meaning/units of `value` remain unresolved. It may be a
hardware-specific value or encoded level; do not assume it is calibrated
RSSI. The UI resources prove only that related resources exist. Trace
the producer, callers, and service path before changing conversion or
claiming S-meter accuracy. All addresses above are v1.0.47-specific
until re-derived for another build.

### 5.4 Spectrum/activity

The user has observed the radio's built-in spectrum screen sweeping a frequency range around a selected centre frequency, with a graph that updates as the sweep progresses. Treat this as **user-observed behaviour**, not as a traced code path or independently verified measurement. The underlying tune/settle/measure/scale/draw sequence, measurement source, units, timing, and exact firmware version still need to be mapped. No evidence currently establishes simultaneous wideband capture, FFT, or raw IQ output. A PC waterfall should therefore be described as a sequence of stepped measurements unless new evidence proves otherwise.

### 5.5 Scan

Scan UI strings/resources/tables exist. The operational path that
retunes RF, checks activity, and advances channels has not been fully
established. Trace the scan entry point to actual
tune/receive/signal-check calls, including dwell timing, stop/resume,
priority channels, bounds, tone squelch, and polling/timer/callback
behavior. Avoid patches that only change displayed scan state.

### 5.6 CTCSS/DCS

Menus/resources exist; the decoder/result path is not established. A
tone table or menu does not prove the application can read a detected
tone. Find the decoder or service result path before claiming
auto-identification.

### 5.7 Frequency step / tuning

Menu/table references exist; quantization and final RF frequency-writer
path remain unresolved. A changed displayed frequency is not proof that
the synthesizer/receiver was retuned.

## 6. Public research leads --- compatibility warnings apply

### NicSure TD-H3 Engineering

https://github.com/NicSure/TD-H3-Engineering

Previously noted contents: original TD-H3 disassembly
(`firmware_disassembly.asm`), `ctcss_test.asm`, `TD-H3 sch.pdf`,
protocol notes. **Original TD-H3 is not the TD-H3 Plus.** Use this for
concepts or comparative clues only; do not copy bytes, addresses, or
hardware assumptions without proof in the Plus target.

### JieLi architecture

-   https://kagaimiq.github.io/jielie/cpu/pi32v2.html
-   https://github.com/quarkslab/ghidra-jieli

Useful for instruction decoding and processor support; not a complete
service ABI reference.

### TD-H3 Plus CPS

https://github.com/jamarju/tid-h3-plus-cps

An open-source configuration software project. Prior notes mention
config-dump/protocol documentation and a dump around 16 KB. It is not
known to provide a complete internal ROM/platform dump or replacement
firmware. Keep radio configuration blobs separate from executable
firmware.

### TD-H9 experimental firmware

https://github.com/mjwgeek/TIDRADIO_TD-H9

May provide experimental patch methodology or comparative code. Do not
assume the TD-H9 shares exact hardware, ROM, ABI, build layout, or
offsets with the TD-H3 Plus.

Previous public research did not establish the exact Plus service ABI.
Avoid repeatedly restating that conclusion; pursue a focused experiment:
compare actual call-site patterns, service references, related firmware
versions, and available documentation, then label what is matched versus
hypothesized.

## 7. Safety and patching protocol

Before any patch, complete this checklist:

1. Record the target version, source path, byte length, SHA-256, and exact process used to create the decrypted image.
2. Identify function boundaries, virtual address (VA), app-relative file offset, any full-flash offset if relevant, original bytes, surrounding disassembly, and callers. Do not conflate these address spaces.
3. Explain the function's inputs, outputs, calling convention, side effects, and why the behaviour is understood.
4. Patch a separate working copy. Require exact-original-byte checks and abort on mismatch.
5. Include a target-version guard and a rollback patch or clean rebuild path.
6. Respect instruction boundaries; do not overwrite adjacent code or data.
7. Independently disassemble the patched region and check branch/call targets.
8. Compare the full image and prove all changed bytes fall within the intended ranges.
9. Run relevant regression tests, Python compilation where applicable, and `git diff --check`.
10. Reconfirm that the pristine original's hash is unchanged.
11. Validate complete package reconstruction, encryption/container structure, checksums/signatures, and updater/bootloader acceptance. Do not infer this from a successful app-image patch.
12. Establish a credible recovery route for the exact hardware, preferably tested, before flashing.

Do not flash if package creation or recovery is unknown. Do not claim
hardware operation based on static analysis, strings, successful Python
tests, or byte diffs alone. Follow applicable radio regulations when
testing RF.

## 8. Last prompt given to Copilot --- not confirmed executed

The user was last given this prompt to run from the repo:

``` text
cd ~/jl-uboot-tool/H3Plus && copilot
```

Then:

``` text
## CYBER-H3 — First Firmware Patch

Work in the existing repository at ~/jl-uboot-tool/H3Plus.

Read the current project instructions, latest findings and Git diff. Do not repeat completed analysis or rewrite documentation unnecessarily.

### Objective
Produce the first small, reversible, technically justified firmware code modification—or prove precisely why no safe candidate is available.

### Steps

1. Confirm the original v1.0.47 firmware hash and identify the existing decrypted application image and address mapping.
2. Inspect existing findings for self-contained application-level functions that do not depend on unresolved ROM/platform services.
3. Select the simplest candidate that has clear function boundaries, understood callers and limited side effects.
4. Verify its instructions using the project's disassembler and cross-check with the available JieLi pi32v2 architecture documentation or Ghidra support.
5. Before editing, document the original bytes, virtual address, file offset, function boundaries and expected behaviour.
6. Create a separate working copy. Implement the smallest version-guarded patch possible, with exact-original-byte checks and rollback. Never modify the original firmware.
7. Independently verify the patched bytes, surrounding instructions, image boundaries and changes outside the intended patch region.
8. Run the existing regression suites, Python compilation and git diff --check.
9. Determine whether a validated route exists to rebuild the complete firmware package. Do not assume a patched decrypted image is flashable.
10. Do not flash the radio or claim the patch works on hardware without actual testing.

### If no safe patch is possible
Do not repeat the general feature analysis. Identify the single most promising candidate, the exact unresolved technical fact blocking it, and the most direct way to obtain that fact from the existing artifacts or tools. Implement a focused tool or test if it will resolve the blocker.

### Final report
State the exact function and bytes changed, the intended behaviour, tests and actual results, whether a complete firmware image can be rebuilt, and the next concrete blocker.

Prioritise executable progress over additional reports. Preserve existing project functionality and keep v1.0.47 and v1.0.50 strictly separate.
```

### How to judge the result

Ask whether Copilot actually modified a firmware working copy or ran a
focused experiment, identified exact bytes and function boundaries,
provided rollback and version guards, independently checked the diff,
ran tests, assessed full-package rebuild, and avoided flashing. If it
only produces another general report, ask for one exact missing fact and
a targeted test that could establish it. Do not force an unsafe patch
merely to claim progress.

## 9. Feature status matrix

| Feature | Evidence currently recorded | Critical unknown | Status |
|---|---|---|---|
| S-meter | v1.0.47 conversion expression and threshold/resource addresses | Input source and units, calibration, RF service trace | Partial static analysis; not calibrated |
| Spectrum | User-observed stepped-sweep screen plus menu/resource evidence | Exact measurement path, units, timing, transport | Screen observed; source not traced; PC export not implemented |
| Scan | UI/resources/tables | RF retune and activity-check path | Not implemented/validated |
| CTCSS/DCS | Menu/resources | Decoder output accessible to application | Not implemented/validated |
| Frequency step | Menu/table references | Actual quantisation and RF writer | Not implemented/validated |
| Channel management | Project goal | Storage/configuration format and safe write path | Not implemented/validated |
| Profiles | Project goal | Persistence and UI integration | Not implemented/validated |
| Battery diagnostics | Project goal | Measurement source and calibration | Not implemented/validated |
| PC/CYBERDECK integration | Long-term goal | Defined physical/protocol/API path | Not implemented in firmware |
| Complete firmware rebuild | Container/encryption tooling exists | End-to-end repackaging and device acceptance | Unconfirmed |
| Safe recovery | No verified method recorded | Tested recovery from failed boot/flash | Blocker |


"Not implemented" means no verified implementation is known here; it
does not prove the feature is impossible.

## 10. Related project context: CYBERDECK_NODE

This is a separate project and must not be mixed into firmware work unless a specific integration is requested.

- Raspberry Pi 4B dashboard/backend; project directory previously `~/CYBERDECK_NODE`.
- Backend deployed at `/opt/cyberdeck/app.py`, systemd service `cyberdeck-node.service`.
- ESP32-WROOM-32 with ST7789 display is part of the user's control/display setup.
- Do not assume this setup currently controls the TD-H3 Plus. Define and test a real interface before claiming integration.
- Preserve the newest feature-complete code in that separate project too.

## 11. User preferences and constraints

-   Wants autonomous end-to-end work and concrete progress, not
    repetitive analysis loops.
-   Wants existing features/tools preserved and extended, never
    downgraded without permission.
-   Prefers verified commands and accurate, practical instructions.
-   Prefers concise normal responses; handoff docs should be detailed.
-   Wants this handoff updated every time they provide new project
    information.
-   Do not address the user by account name unless asked.

## 12. Chronological log

### 2026-10-10 --- Master handoff created

-   Consolidated known project identity, artifact hashes, tool list,
    test results, findings, blockers, public research, safety
    requirements, feature status, and the last Copilot prompt.
-   Recorded that the original v1.0.47 firmware remains unchanged, no
    internal dump is present, no feature patch is validated, and no
    radio has been flashed.

### Earlier work --- exact dates not established in the available context

-   Investigated TD-H3 Plus firmware and distinguished it from original
    TD-H3.
-   Added/fixed service-trace validation tooling for decrypted
    v1.0.47/v1.0.50 images.
-   Added `--source` support to `verify_cli.py`.
-   Reported service assertions, `verify_actions.py`, direct-source
    `verify_cli.py`, Python compilation, and `git diff --check` passing.
-   Confirmed the original v1.0.47 hash unchanged and
    `Dumps/dump_internal.bin` absent.

## 13. Template for future updates

Append a dated entry when new evidence arrives:

``` markdown
### YYYY-MM-DD — Short description
- **New facts:**
- **Files changed:**
- **Commands run:**
- **Tests and exact results:**
- **Firmware version / image hash:**
- **Function / VA / file offset / bytes:**
- **Hardware results:**
- **New unknowns/blockers:**
- **Next concrete action:**
```

## 14. Quick briefing for a new model

The target is **TIDRADIO TD-H3 Plus**, repository
`~/jl-uboot-tool/H3Plus`. The known original v1.0.47 image is
`BIN/TID-H3-Plus-1.0.47.bin`, 790,528 bytes, SHA-256
`3b2d198b6d6bcce884ea437cccb253efd705ab72c790c04b704c3da75213deda`. A
decrypted application was previously reported at `/tmp/h3plus-1.0.47-app.bin`; verify that it exists and matches the source image. Candidate v1.0.50 update archives and `decrypted_app.bin` are present in the ChatGPT Library, but their contents, variant and provenance have not been checked.

Earlier tooling changes reportedly passed service-trace tests,
`verify_actions.py`, direct-source `verify_cli.py`, Python compilation,
and `git diff --check`; wrong-version input was rejected. The original
image stayed unchanged. `Dumps/dump_internal.bin` is missing. No
firmware feature bytes have been modified and the radio has not been
flashed.

The strongest concrete lead is the v1.0.47 signal-meter conversion at VA
`0x01E5057A`, reportedly `(value >> 1) - 0xA0`, with threshold addresses
`0x01E505BA` and `0x01E505D6`, and resources at `0x01E97AB4`,
`0x01E97AD8`, and `0x01E98020`. The source/meaning of the input value
remains unknown. Scan, spectrum, CTCSS/DCS, and frequency-step UI
evidence exists, but the underlying RF/service paths remain unresolved.

**Next action:** verify the candidate Library firmware archives and decrypted app by inspecting contents, hashes, hardware/update variant and provenance. Then trace the existing spectrum sweep on the confirmed target image. Use that evidence to select a minimal reversible code change or a focused experiment that resolves one specific blocker. Avoid another generic analysis report. Keep versions separate, preserve originals, and do not flash until package rebuilding and recovery are verified.

## 15. MASTER IMPLEMENTATION BRIEF — CYBER-H3 PLUS CUSTOM FIRMWARE

**Purpose:** This section is the detailed reusable engineering brief for any AI, developer, or future session continuing the TD-H3 Plus firmware project. Treat it as the project's requirements and investigation plan. It describes the target outcomes, the evidence and artifacts required to implement them, acceptance tests, and non-negotiable safeguards. It is a plan, not a claim that the features below have already been implemented.

### 15.1 Mission and definition of success

Develop one coherent, versioned custom firmware for the **TIDRADIO TD-H3 Plus** that preserves normal radio functionality and the project's existing hardware-tested modifications, adds a useful PC-connected RF-monitoring workflow using measurements the radio can actually provide, and improves scanning, tuning, display, key controls, diagnostics, and supported Bluetooth behaviour where evidence confirms feasibility.

The key RF objective is to reuse the radio's existing spectrum/sweep screen and its measured signal levels. The radio scans frequency points over a selected span and samples them sequentially; it is **not** a simultaneous wideband SDR. A PC waterfall made from those samples must be labelled as a sequential sweep and must not imply IQ capture, continuous wideband reception, or simultaneous observation of all frequencies.

A successful result includes:

1. A firmware feature map tied to the exact target firmware version and hardware.
2. A reproducible, version-aware build/patch workflow with original files preserved.
3. A custom firmware image that retains existing working features and changes only intended code/data.
4. A documented method to deliver measured spectrum data to a PC, using a transport proven to work on this unit.
5. A Linux-compatible PC application that plots received samples as a live spectrum and scrolling waterfall, with configuration, connection status, logging, and export.
6. Carefully verified improvements to existing scan, tuning, meter, tone-decoding, UI, programmable-key, and Bluetooth functions, but only where the firmware and hardware demonstrably support them.
7. A regression report, image hashes, exact patch list, limitations, and a tested recovery procedure.

### 15.2 Source-of-truth and version discipline

- Main analysis repository: `https://github.com/stefanlenselink/H3Plus`, locally reported as `~/jl-uboot-tool/H3Plus`.
- The original v1.0.47 image recorded earlier is `BIN/TID-H3-Plus-1.0.47.bin`, 790,528 bytes, SHA-256 `3b2d198b6d6bcce884ea437cccb253efd705ab72c790c04b704c3da75213deda`.
- The public repository documents a v1.0.50 hardware reference and reverse-engineering work, but does not publish the private/local firmware, decrypted application, full dump, or working directory artifacts.
- A decrypted v1.0.47 application was previously reported at `/tmp/h3plus-1.0.47-app.bin`; its continued existence, provenance, exact size, and hash must be checked on the user's machine. Do not assume it is the currently running radio version.
- Hardware findings recorded for a particular unit include JieLi BR23 / AC635N-family SoC, Beken BK4819 RF transceiver, chip key `0xF181`, and 1 MiB SPI NOR JEDEC ID `0x856014`. Verify unit/version context before relying on unit-specific details.
- Never copy addresses, patch bytes, or results from v1.0.50 into v1.0.47 (or any other release) without independently mapping and verifying them in the exact target image. File offsets, application virtual addresses, and full-flash addresses are different address spaces; every patch note must identify which is being used.
- The repository's Ghidra + `ghidra-jieli` analysis and official JieLi `pi32v2` compilation/splice workflow has documented hardware-tested round-trip examples. This proves that the workflow can work; it does not prove that a new patch is correct.

### 15.3 Required inputs before feature implementation

Collect and record the following from the actual working environment. If a required artifact is absent, ask for that exact artifact rather than guessing or silently switching firmware versions.

**Firmware and backups**

- [ ] Exact firmware version displayed by the radio and the matching original vendor `.bin` / `.fw` package used for it.
- [ ] SHA-256, byte length, and source of every original package and decrypted image.
- [ ] Current decrypted application for that exact version, preferably the project's generated `work/app_dec.bin` or equivalent, plus the decryption command/script and log proving how it was produced.
- [ ] A full 1 MiB internal flash dump from the target unit, if available, safely stored offline. It can contain device-specific identity/pairing data; do not publish it casually.
- [ ] Existing patches, build scripts, package/CRC tools, toolchain versions, and current `git status` / `git diff`.
- [ ] Recovery method tested for this exact unit and a clear distinction between a vendor upgrade package, app image, bootloader image, and full flash dump.

**Hardware and interfaces**

- [ ] Confirm exact TD-H3 Plus variant, board revision if known, and that it is not the original non-Plus TD-H3.
- [ ] USB enumeration in normal operating mode and bootloader/update mode (`lsusb`, `dmesg`, and device nodes); record whether normal-mode USB exposes serial, HID, bulk endpoints, mass storage, or nothing useful.
- [ ] Bluetooth capabilities observed on this unit, including whether the radio can expose a usable data service concurrently with normal operation.
- [ ] Existing PC, Linux distribution, and preferred connection (USB first if a usable live data endpoint is proven; otherwise assess Bluetooth or another safe route).
- [ ] RF test setup: known legal receive signals, a dummy load/attenuator where relevant, no unintended transmission, and a repeatable way to compare radio graph values with exported data.

**Reverse-engineering artifacts**

- [ ] Ghidra project or reproducible import script for the exact decrypted app, with correct `pi32v2` language and memory map.
- [ ] Full disassembly/decompilation tree generated from that image, string/xref reports, and existing address notes.
- [ ] Exact callers/callees and data-flow evidence for the spectrum screen, scan loop, RF tuning, RSSI/signal-meter reads, graph drawing, squelch, CTCSS/DCS, VFO, key actions, and available communications APIs.
- [ ] For every proposed function: raw bytes, VA, app-relative offset, flash offset, calling convention, register/argument use, return semantics, and confidence level.

### 15.4 Feature requirements and investigation questions

#### A. Existing spectrum screen and PC waterfall — primary feature

**Required outcome:** When the radio's existing spectrum analyser scans a user-selected span around a centre frequency, it exports each real measurement to a connected PC. The PC displays a live line/spectrum plot and scrolling waterfall. The displayed samples must correspond to the frequencies the radio actually visited.

**Trace and prove:**

1. Find the screen/menu entry and all state variables controlling centre frequency, span, start/end frequency, frequency step, sweep direction, pause/hold, and scan timing.
2. Trace the complete per-point scan path: frequency calculation → RF synthesizer/tuner programming → settling/dwell → measurement read → graph scaling → drawing → next frequency.
3. Identify whether the graph uses BK4819 RSSI register `REG_67`, a filtered or transformed value, a peak/average measurement, or another driver/API. Public BK4819 references indicate RSSI is readable, but do not assume the Plus uses it directly until its own code path proves it.
4. Determine units, valid range, sign, filtering, clipping, noise floor, and whether the display applies offsets/thresholds. Calibrate against the stock graph and controlled receive signals before labelling data in dBm. Raw counts are acceptable initially if clearly labelled.
5. Identify a safe hook after each completed measurement. Export the actual sample already used by the analyser; do not perform a second measurement or retune the radio for export.
6. Determine if scan state is interrupt-driven, task-driven, timer-driven, or UI-driven. The exporter must never block the RF scan or hold critical locks while waiting for the PC.
7. Find a normal-mode live data transport. USB bootloader mass-storage access does not prove a live serial/data interface exists. Inspect actual USB descriptors/endpoints and firmware stack/API before choosing a protocol. Bluetooth SPP or another service is only an option if verified in this firmware and usable without breaking audio/PTT.
8. Define a versioned, framed protocol with message type, protocol version, sequence number, frequency in Hz, raw measurement, optional calibrated level, sweep ID, timestamp/tick, scan configuration, and status/error flags. Include framing, length bounds, checksum/CRC if appropriate, resynchronisation, and behaviour on disconnect. Avoid sending unnecessary verbose text at every sample.
9. Use a bounded queue/ring buffer or equivalent non-blocking mechanism. If the PC cannot keep up, drop or coalesce samples predictably, count losses, and never stall the radio. Measure actual data rate and scan timing.
10. Build a Linux desktop client with device discovery/port selection, connect/disconnect, centre/span/step controls only if safe command control is supported, line graph, scrolling waterfall, scale/range control, peak markers, pause/clear, status, sequence-loss counters, and CSV or similar export.
11. If remote scan control cannot be implemented safely, first deliver a receive-only exporter that mirrors the on-radio scan. Clearly show that centre/span/step are controlled on the radio, not falsely present PC controls that do nothing.

**Acceptance tests:** frequency labels agree with the radio's configured scan; exported sample order agrees with the on-device graph; no unexplained frequency gaps; dropped samples are counted; PC disconnect does not freeze scanning; normal reception resumes; PTT and Bluetooth are not regressed; no transmission is initiated by the PC monitoring feature.

#### B. Receiver and scan improvements

Investigate rather than assume the availability of each feature:

- Adjustable scan dwell, scan step, direction, hold/resume, and resume-on-signal behaviour.
- Frequency-entry and VFO tuning precision, valid tuning granularity, centre/span calculation, and boundary handling.
- Better peak hold, peak markers, activity history, and configurable signal thresholds.
- Existing dual-VFO/VFO A/B behaviour and whether it can be made clearer without breaking PTT2 or dual-watch.
- Squelch and RSSI filtering/averaging, including whether a change affects reception, battery use, scan speed, or only display smoothing.
- Supported receive modulation modes and band/frequency limits. Do not add UI labels for modes that the RF chip, board design, or firmware cannot actually use.
- Tone decode and signalling status, including CTCSS/DCS if the radio's current receiver and firmware expose decoded results.
- Potential frequency-step options (including 8.33 kHz only if the synthesizer, firmware arithmetic, display and channel spacing all support accurate operation). Do not add an option solely because it appears in other radios.

For each item, document existing support, implementation approach, dependencies, regressions risks, and a reproducible test. Keep experimental settings reversible and provide safe defaults.

#### C. Display, menus and physical controls

- Make the spectrum screen readable and useful within the existing display limits.
- Provide clear frequency/span/step, signal scale, sweep state, pause/hold, peak indicator, and PC-link status where practical.
- Improve quick access to scanning and commonly used functions using supported menu/key hooks.
- Map PF1/PF2, PTT, PTT2, VFO A/B, and existing Bluetooth key remaps before changing handlers.
- Preserve existing menu entries and default behaviour unless the user explicitly approves a documented change.
- Avoid large rewrites of display code when a narrow hook or data-field change will suffice.
- Keep settings persistence compatible with the radio's existing configuration storage; do not overwrite device identity or unknown VM/config fields.

#### D. Signal metering and signal identification

- Trace the known meter lead at VA `0x01E5057A` for the relevant image; the earlier `(value >> 1) - 0xA0` interpretation is a lead, not proof of the spectrum graph source.
- Inspect nearby threshold logic previously noted at `0x01E505BA` and `0x01E505D6`, and resources around `0x01E97AB4`, `0x01E97AD8`, and `0x01E98020`, but re-verify all addresses against the selected firmware version.
- Determine if signal measurements are raw register values, converted RSSI, filtered RSSI, or UI-only values.
- Only label dBm after calibration with known input levels, appropriate attenuation, and repeatable setup. Otherwise label the values as raw/relative units.
- Show CTCSS/DCS or other decoder outcomes only when they are actual decoder results, not inferred from signal strength.
- Log time, frequency, measurement, scan settings, tone result if available, and any sample loss. Protect device-specific data and avoid storing unrelated personal/device identifiers.

#### E. Bluetooth and existing hardware-tested work

- Preserve the documented, hardware-confirmed key remapping and Bluetooth headset-mic/PTT work in the H3Plus research history.
- Treat Bluetooth multipoint as an independent experimental track: repository findings report that the current BR23 stack's connection data model is a limiting factor and that merely changing the app's connection-count gate did not solve true two-device operation. Do not advertise multipoint as working unless re-tested on the target hardware.
- Do not disturb HFP, SPP, PTT press/release semantics, audio routing, or gain controls while implementing spectrum export.
- If Bluetooth is selected as a data transport, test coexistence with headset audio and PTT, throughput, reconnect, and controller limitations first.

#### F. Diagnostics and robustness

- Add version and feature-capability reporting to the PC protocol, where a safe existing transport is available.
- Track scan sample count, dropped/exported frames, queue overflow, transport disconnects, and protocol errors.
- Ensure invalid PC commands are rejected and bounded. Do not create an unrestricted shell/command execution path through USB or Bluetooth.
- Make exporter enable/disable explicit and ensure normal radio operation remains the default if the PC app is absent.
- Keep debug output rate-limited and separate from binary sample framing.
- Test long runs, reconnects, malformed frames, full queues, and app closure.

### 15.5 PC application requirements

Target Linux first. The client should be a practical monitoring application, not a mockup. It must distinguish confirmed features from placeholders.

Minimum deliverables:

- A real connection layer for the proven transport, with port selection and clear error messages.
- A documented parser for the versioned firmware sample protocol.
- Live spectrum trace and scrolling waterfall from actual received samples.
- Accurate frequency axis and sample ordering; visible scan/sweep cadence.
- Raw/relative signal scale by default until calibrated dBm is proven.
- Centre/span/step controls only if the firmware supports safe remote control; otherwise provide on-radio-control instructions.
- Start/stop display, pause, clear, peak hold, adjustable visual range, and connection/sample-loss status.
- Save/load measurement data and export CSV with units and metadata.
- No fabricated/demo data in live mode. If demo mode exists, mark it conspicuously and keep it separate.
- Basic automated tests for protocol framing, parsing, malformed input, sequence loss, reconnect, and data export.

### 15.6 Build and patch process

1. Confirm exact original image/version and verify SHA-256 before analysis.
2. Create a pristine read-only copy of original input, a working copy, and a separate output directory. Keep user-specific full dumps private.
3. Decrypt/extract with the project's documented scripts and verify expected lengths, map and known markers. Record exact commands and outputs.
4. Import the matching decrypted app into Ghidra with the documented JieLi processor/tooling and correct memory map.
5. Trace a small self-contained function or call path and document all address conversions.
6. Establish an unchanged compile/splice or no-op baseline and compare byte-for-byte where expected. Do not proceed if unexplained differences exist.
7. Implement one small, reversible change at a time. For code changes, preserve calling convention, registers, stack, alignment, return values, interrupt/task assumptions, and timing constraints.
8. Run static checks: output length, app bounds, changed-byte report, branch/call target checks, package structure, CRC/checksum validation, and version guardrails.
9. Build the correct vendor update package using the verified project workflow. Do not assume a raw app image can be flashed directly.
10. Test on hardware only after the recovery path is verified and the patch's scope is understood. Start with a harmless exporter status/no-op hook, then a tiny sample stream, then PC rendering, then optional enhancements.
11. Keep a known-good image and a patch manifest that includes source hash, output hash, version, modified addresses, original/replacement bytes, reason, test status, and rollback instructions.
12. Merge features only after individual tests pass; run regression tests on ordinary receive, transmit/PTT, scanning, tones, VFOs, display, Bluetooth, settings persistence, and startup.

### 15.7 Safety, legal and reliability constraints

- Preserve the original firmware and full dump; keep at least two verified backups and verify hashes after copying.
- Never use `burnchipkey`, `erasechip`, or bootloader-update operations as an experiment. Do not overwrite the device-specific 32-byte runtime area or unknown settings/identity regions without a specific proven need.
- Do not flash speculative code, mismatched-version patches, or an image with unresolved checksum/container problems.
- Do not transmit to test the PC spectrum feature. Use receive-only test signals, a suitable RF generator or known legal local signal, and appropriate attenuation where necessary.
- Do not expand transmit capability, power, or frequency access beyond applicable law, licence, and the radio's approved hardware limits. This project is focused on receive analysis, usability, and data export.
- If the device enters an uncertain state, stop testing and return to the documented recovery path rather than attempting random writes.

### 15.8 Required engineering outputs

Maintain these artifacts in the project repository or private work directory:

- `docs/FEATURE_ROADMAP.md` — feature inventory, status, dependencies, and evidence.
- `docs/FIRMWARE_MAP.md` — exact-version memory map and verified function map.
- `docs/PC_PROTOCOL.md` — frame format, fields, units, versioning, commands, error behaviour.
- `docs/TEST_PLAN.md` — test setup, expected results, actual results, regressions.
- `docs/RECOVERY.md` — verified backup and recovery instructions for the actual unit.
- `patches/manifest.json` or equivalent — source/output hashes, versions, offsets, bytes, rationale, and status.
- Versioned firmware package and corresponding source/patch files.
- Linux PC app source, install/run instructions, and tests.
- A sample capture file from real hardware, clearly identifying units and firmware version.
- A release note distinguishing implemented, tested, experimental, unsupported, and not-yet-investigated features.

Do not claim a deliverable exists until the corresponding file or artifact has actually been created and checked.

### 15.9 Acceptance matrix

A feature is not complete merely because it compiles or appears in a menu. Record each feature as **Not investigated**, **Mapped**, **Implemented**, **Static checks passed**, **Hardware tested**, or **Blocked**, with links to evidence.

| Area | Minimum pass condition |
|---|---|
| Firmware identity | Exact version and source image hash recorded |
| Build | Repeatable build; image/container validation passes |
| Regression | No unexplained changes; baseline radio functions work |
| Spectrum sample source | Proven code/data path and documented units |
| Export transport | Confirmed normal-mode live data path; no reliance on bootloader MSC assumptions |
| PC waterfall | Real radio samples, correct frequency ordering, visible losses/errors |
| Scan performance | No material scan stalls or unexplained sample gaps |
| Radio behaviour | Receive, PTT, VFO, tones, display, Bluetooth and settings regression checks recorded |
| Recovery | Exact-unit recovery procedure and known-good image verified |
| Release | Source, patch manifest, hashes, tests, limitations, and recovery notes included |

### 15.10 Prompt/script for the next AI or developer

Copy the text below as the implementation instruction for a new session or coding agent. It is intentionally explicit so the agent does not substitute generic ideas for verified engineering work.

> You are continuing an ongoing reverse-engineering and custom-firmware project for the **TIDRADIO TD-H3 Plus**, repository `https://github.com/stefanlenselink/H3Plus`, usually located at `~/jl-uboot-tool/H3Plus`.
>
> **Mission:** produce one coherent custom firmware and a Linux PC application that exports the TD-H3 Plus's actual built-in sequential spectrum-analyser measurements to a live spectrum/waterfall display. Also map and implement worthwhile receiver, scan, meter, tone-decoding, UI/key, diagnostics, and Bluetooth improvements that the exact hardware and firmware support. Preserve existing features and the documented hardware-tested Bluetooth/PTT changes. Do not downgrade to an older/smaller firmware or copy patches between versions without proof.
>
> **Start with evidence, not assumptions.** Inspect the current repository, Git diff, handoff, tools, exact source image, decrypted app, existing patches, and test records. Confirm the radio's exact firmware version. The recorded v1.0.47 image hash is `3b2d198b6d6bcce884ea437cccb253efd705ab72c790c04b704c3da75213deda`, but do not assume that this is the current target. A v1.0.50 research reference also exists. Public repository documentation does not contain the private firmware/decrypted application/dump artifacts. If the exact target app is missing, request the matching original firmware and decrypted app rather than inventing addresses.
>
> **Primary task:** trace the actual spectrum sweep loop from frequency selection through RF tuning, settling, measurement, scaling, graph drawing and next step. Identify the real measurement source and units. The BK4819 has RSSI/scan capabilities, but do not assume a register value feeds this particular graph until the Plus firmware proves it. The previously noted meter conversion at VA `0x01E5057A` and threshold leads `0x01E505BA`/`0x01E505D6` are leads only; verify them against the exact target image. Reuse existing samples and avoid a second measurement or retune.
>
> **Transport task:** verify a live, normal-mode USB data endpoint first. Bootloader USB mass storage is not proof of a live serial channel. Inspect descriptors and the firmware USB stack. If USB cannot safely carry data, assess an actually supported Bluetooth/data route and test coexistence with audio/PTT. Do not select a transport based on wishful thinking.
>
> **Protocol/client task:** design a versioned, framed, bounded, non-blocking sample protocol containing at minimum frequency in Hz, raw measurement, sequence number, sweep identity, timing/status and scan configuration. Add calibration only after evidence. Implement a Linux client with a real parser, line spectrum, scrolling waterfall, connection/error/sample-loss status, optional safe controls, pause/clear/peak hold, and data export. The display must clearly represent sequential scan data and must not claim simultaneous wideband or IQ capture. Do not fabricate live data.
>
> **Other feature task:** map actual firmware support for scan dwell/hold/resume, frequency step and tuning, VFO A/B, RSSI/squelch, CTCSS/DCS decode, display/menu improvements, programmable keys, Bluetooth audio/PTT and diagnostics. Classify every proposed enhancement as supported, uncertain, unsupported, or blocked. Implement only when code path, hardware support, and tests justify it. Preserve PTT and audio behaviour; treat true Bluetooth multipoint as experimental because previous research found a stack connection-model limitation.
>
> **Engineering discipline:** keep pristine originals; record SHA-256 and sizes; keep device-specific dumps private; separate firmware versions and address spaces; make an unchanged build baseline; use the documented Ghidra/JieLi `pi32v2` compile/splice process; produce a changed-byte report; validate image/container structure and CRCs; make one reversible change per iteration; never flash speculative code. Never use `burnchipkey`, `erasechip`, or unverified bootloader updates. Confirm recovery for the exact unit before writing.
>
> **Testing:** validate startup, ordinary receive, scan timing, graph/sample agreement, frequency labels, queue overflow/disconnect/reconnect, PC closure, sample-loss counters, VFO, tone decode, settings persistence, Bluetooth audio/PTT, and all changed controls. Test RF reception with appropriate receive-only sources; do not transmit for spectrum tests. Do not increase TX power or bypass legal frequency restrictions.
>
> **Outputs:** updated source/patches; versioned valid firmware package; Linux PC app and tests; `FEATURE_ROADMAP.md`, `FIRMWARE_MAP.md`, `PC_PROTOCOL.md`, `TEST_PLAN.md`, and `RECOVERY.md`; patch manifest with original/replacement bytes and offsets; image hashes; test results; known limitations. Clearly distinguish implemented, statically checked, hardware-tested, experimental, and blocked. Never claim success without actual test evidence.
>
> **Immediate next action:** inspect the current local artifacts and repository state; confirm exact firmware version and availability/hash of the matching decrypted app. Then map the spectrum sample path and prove a normal-mode data transport. Do not start by writing a speculative firmware patch or a mock PC UI.

### 15.11 Current status after adding this brief

This master brief is a requirements document only. No new firmware code has been patched, no new transport has been proven by this document, no PC application has been implemented here, and no new firmware has been flashed. Continue by acquiring/validating the exact target artifacts and producing evidence for each stage.

---

## 16. TD-H3 Plus UI and menu redesign plan (new-feature-aware)

**Status:** proposed information architecture; not yet implemented or validated against the target firmware. This section extends the master brief and must be reconciled with the exact menu IDs, screen dimensions, available keys, string tables, settings storage and callbacks before patching.

### 16.1 Design goals

1. Make the handheld interface predictable and shallow: common radio actions should be reachable quickly, while advanced analysis and diagnostics remain grouped separately.
2. Reuse existing functions and callbacks wherever possible. Reorganising a menu must not silently change what a setting does.
3. Design the hierarchy around planned additions: spectrum scanning/export, signal metering, scan profiles, tone decode, logging and PC connectivity.
4. Keep the small built-in display focused on the current task. Put large waterfall history, detailed plots and long logs in the PC/cyberdeck application rather than overloading the radio screen.
5. Preserve all existing receive, transmit, VFO, Bluetooth headset/microphone, PTT and tested key-remapping behaviour unless an independently tested change explicitly requires otherwise.
6. Never add a visible setting unless its callback, value range, persistence behaviour and unsupported-hardware behaviour are defined.
7. Do not assign functions to particular physical keys until the target firmware's key event map and the unit's actual key layout are confirmed.

### 16.2 Proposed top-level menu

Use these as conceptual groups, not literal menu IDs. Labels may need shortening to fit the stock display.

1. **RADIO** — everyday operating settings and controls.
2. **SCAN** — channel/frequency scanning, scan resume behaviour, dwell and scan profiles.
3. **SPECTRUM** — built-in stepped spectrum screen, centre frequency, span, step, sweep controls, peak hold and signal threshold.
4. **SIGNALS** — signal meter, squelch, CTCSS/DCS decode status and supported signal details.
5. **CHANNELS** — channel/VFO selection, channel information and supported memory operations.
6. **AUDIO / BT** — audio options and Bluetooth headset/microphone/PTT controls already supported by the firmware.
7. **SHORTCUTS** — configurable quick actions for the available programmable keys, if the firmware exposes safe remapping hooks.
8. **LINK / PC** — connection status, streaming state, sample counter, errors and PC export controls, only if a runtime data transport is proven.
9. **SYSTEM** — display, key beep, language/other existing system preferences, settings reset and version/build information.
10. **DIAGNOSTICS** — advanced read-only status and test information; hide or gate dangerous/service operations and do not expose flash-write functions as casual menu actions.

If the existing UI cannot support ten top-level entries clearly, use a smaller top level with nested groups: **Operate**, **Analysis**, **Connectivity**, **Settings**, and **Diagnostics**. Choose based on the existing renderer and navigation limitations rather than forcing the proposed names into the firmware.

### 16.3 Menu contents and intended behaviour

#### RADIO
- Existing receive/operating mode controls supported by the target firmware.
- Current frequency/channel and VFO selection where present.
- Frequency step selection only for values actually accepted by the tuner and represented accurately in the display/storage.
- Squelch and other current receiver controls.
- Do not add AM/FM/SSB or other demodulation choices unless the radio's RF path and firmware prove they are implemented and usable.

#### SCAN
- Start/stop scan and preserve the existing default scan action.
- Resume mode (for example, resume after carrier disappears or after a fixed hold), only if the firmware's scan engine supports the chosen semantics.
- Scan dwell/hold and scan step where the existing engine exposes a valid timing/frequency control.
- Named scan profiles only if persistent storage can be added without corrupting the existing settings/VM layout. Initial profiles could be receive-only presets such as broad scan, airband-oriented step plan, and user-defined plan; actual band limits and step values must be validated and legal receive/transmit behaviour must remain separate.
- Clearly show when scanning is paused, stopped or held on a signal.

#### SPECTRUM
- Enter/exit the existing spectrum screen without breaking normal receiving or PTT.
- Centre frequency.
- Span or start/stop range, according to what the current sweep implementation actually supports.
- Step size, constrained to valid tuner steps and with displayed labels calculated from the real programmed frequencies.
- Sweep rate/dwell only if safe timing control is found.
- Signal threshold and peak hold, reusing the current graph state where practical.
- Optional PC stream toggle and connection/sample status only after the runtime transport works.
- Screen status should distinguish **stepped scan** from simultaneous capture. Never label the result as IQ or true wideband capture without evidence.

#### SIGNALS
- Numeric and graphical S-meter based on the existing meter path.
- Show raw level first; show calibrated dBm only after measurements against a known reference establish a reliable conversion.
- Squelch status and current decode state.
- CTCSS/DCS detected code and confidence/status only if a receive decoder is already present or can be safely implemented using verified hardware/firmware paths. Do not claim a code when no stable decode occurred.
- Signal activity history can be displayed locally in a compact form; detailed time-series logging belongs on the PC.

#### CHANNELS
- Existing channel and VFO functions grouped together.
- Channel information should clearly separate frequency, receive settings and transmit settings if those are independently stored.
- Avoid new memory formats until the existing channel structure and persistence routines are documented.

#### AUDIO / BT
- Preserve all current audio routing and Bluetooth pairing/connection controls.
- Preserve hardware-tested Bluetooth headset microphone and PTT changes documented elsewhere in this handoff.
- Display connection state and PTT/audio status where the display API allows it.
- Do not promise Bluetooth data streaming or multipoint before the protocol/stack is confirmed.

#### SHORTCUTS
- Provide a list of actions that can actually be invoked by the key event system: for example, spectrum, scan start/stop, VFO switch, meter view, or PC stream toggle if implemented.
- Keep PTT semantics and any emergency/long-press behaviour unchanged unless explicitly remapped and regression-tested.
- Persist shortcut choices only through a verified settings mechanism. Unknown key events must fall back safely.

#### LINK / PC
- Connection state: disconnected, connected, streaming, stopped or error.
- Stream enable/disable; current sweep/sample counter; dropped sample/error indicator.
- PC commands should be bounded, validated and non-blocking. Do not accept arbitrary memory writes or shell-like command strings from the host.
- If USB cannot support normal-mode data, show the real supported transport instead; do not create a decorative menu that implies a connection exists.

#### SYSTEM / DIAGNOSTICS
- Existing display and user-interface preferences.
- Firmware version and build identifier, if available without invasive changes.
- Read-only diagnostics for RF state, connection and scan counters when data is genuinely available.
- Reset settings only after identifying the settings region and adding confirmation. Never expose destructive flash operations in ordinary user menus.

### 16.4 Screen and navigation rules

- Reuse the current display driver, font and drawing primitives until their limits are understood.
- Use consistent ordering: current value, selection/action, then status/help if space permits.
- Keep labels short; use a consistent abbreviation glossary rather than inventing different abbreviations on each screen.
- Distinguish selected item, active value and disabled/unavailable item using existing supported visual conventions.
- Preserve back/cancel behaviour and ensure every submenu has a clear exit path.
- Avoid blocking delays in drawing or menu callbacks. Spectrum acquisition, transport and logging must not freeze key response or interrupt normal radio timing.
- Do not redraw the full screen on every measurement if a partial update is possible and verified.
- Keep menu navigation independent from the spectrum sampling/export queue so PC disconnects or slow transfers cannot freeze the radio UI.
- Add confirmation to destructive operations and clear feedback for accepted/rejected changes.

### 16.5 Firmware reverse-engineering tasks required before implementation

1. Identify the menu table/dispatcher, menu IDs, parent-child relationships and all existing callbacks.
2. Locate string tables and determine whether labels are compiled constants, resource offsets or generated text.
3. Map key events (short press, long press, repeat, back, confirm, PTT) to menu actions. Record actual key codes and debouncing/repeat semantics.
4. Identify screen dimensions, font metrics, drawing primitives, clipping rules and refresh strategy.
5. Trace settings get/set routines and persistence format; establish free space and compatibility constraints before adding settings.
6. Map existing spectrum screen entry, drawing, sweep state and exit paths.
7. Find the actual signal measurement path and establish what values are already available to the UI.
8. Map Bluetooth and USB status APIs before proposing link indicators or stream controls.
9. Produce `MENU_MAP.md` with menu IDs, labels, callback addresses/symbols, settings IDs, key actions and confidence/evidence for the exact firmware version.
10. Make a no-behaviour-change menu-map build or static analysis baseline before altering navigation.

### 16.6 Safe implementation sequence

**UI-0 — Inventory:** document the current menu tree and key map from the exact target image. No binary changes.

**UI-1 — Cosmetic cleanup:** adjust labels/order only where the renderer and dispatcher prove it is safe. Verify each existing setting still opens the same callback and retains the same value semantics.

**UI-2 — Grouping:** add nested groups or reorganise menu entries while preserving callback targets and back/confirm behaviour. If menu tables are fixed-size, verify bounds and all references before adding entries.

**UI-3 — Spectrum screen improvements:** improve labels/status and add only controls backed by existing sweep state. Test tuning, scan direction, frequency labels, normal receive and PTT.

**UI-4 — New status/features:** add meter, peak hold, tone status and scan options one at a time, only after each underlying function is proven.

**UI-5 — PC link controls:** add streaming and connection screens only after an actual runtime transport and framed protocol are demonstrated.

**UI-6 — Shortcuts and release:** add programmable key assignments only after the key event map is known. Run all regression checks and publish a menu map and before/after navigation guide.

### 16.7 UI acceptance tests

- Every old menu item remains available or is explicitly documented as intentionally moved/removed.
- Every menu entry points to the intended callback; no duplicated or invalid menu IDs.
- Back/cancel/confirm, short/long presses and key repeat work consistently.
- Labels and values fit the physical screen without clipping or misleading truncation.
- Settings changes survive restart if persistence is expected; defaults and reset behaviour are tested.
- Spectrum entry/exit and parameter changes do not break normal receive, PTT, VFO or Bluetooth audio/PTT.
- PC disconnect, queue overflow and stream errors never freeze menu navigation or RF operations.
- Unsupported features are hidden or marked unavailable, not shown as functioning controls.
- No transmit power or frequency restrictions are relaxed by UI changes.
- Original image, modified image hash, patch manifest, recovery method and test evidence are recorded for each release.

### 16.8 UI implementation status

At the time this section was written, the hierarchy above is a design proposal, not a verified map of the radio's current menus. The exact firmware image and existing UI code must be inspected before assigning actual menu IDs, addresses, string offsets or physical-key mappings. Do not patch from this proposal alone.


## 17. Document audit and maintenance notes — 2026-10-12

This audit improves wording and internal consistency; it does **not** verify firmware behaviour or claim that code was changed.

### Corrections made

- Updated the consolidation date and made the current firmware status explicit: no radio-feature patch is verified as implemented or hardware-tested.
- Reconciled the spectrum description with the user's observation of the built-in stepped-sweep screen. The screen is user-observed; the underlying measurement path, units, timing, and data transport remain untraced. The design must not call this simultaneous wideband capture or IQ.
- Recorded that the Library contains candidate v1.0.50 update archives and `decrypted_app.bin`, while clearly stating that their contents, variant, provenance, and hashes have not yet been checked. Their filenames alone are not evidence of compatibility.
- Updated the quick briefing so it no longer says the matching v1.0.50 package is wholly unconfirmed without mentioning the candidate Library artifacts.
- Converted the patch-safety procedure from a dense run-on paragraph into a numbered checklist.
- Rebuilt the feature-status matrix as a proper Markdown table and distinguished an observed spectrum UI from a traced/implemented data path.
- Fixed the CYBERDECK_NODE section's malformed inline bullets and removed a duplicated sentence.

### Validation performed on this document

- Checked that fenced code blocks are balanced.
- Checked that the main section headings are sequential from 0 through 17; the prompt heading inside Section 8 is inside a fenced code block and is intentionally literal.
- Checked for project `TODO`, `FIXME`, and `TBD` markers outside this audit note; none were found at the time of audit.
- Re-read key claims for conflicts between observed UI, static-analysis evidence, implementation, and hardware validation.

### Remaining editorial/technical cautions

- Historical test results in Sections 4 and 12 remain historical reports; re-run them against the current repository before relying on them.
- The feature matrix records current knowledge, not proof that a feature is impossible. Keep status terms consistent: **observed**, **mapped**, **implemented**, **static checks passed**, **hardware tested**, or **blocked**.
- The proposed eight/ten-group menu layout is conceptual. Do not implement it until the target firmware's real menu tree, display constraints, callbacks, key events, and settings persistence are mapped.
- Next highest-value action: inspect the two v1.0.50 update archives and `decrypted_app.bin`, hash each artifact, identify the matching hardware/update variant, and connect each decrypted image to its exact source package. Then map the existing spectrum sweep path for the confirmed target version.


## 18. Second-pass editorial and execution audit — 2026-10-12

This pass is a documentation review only. It does not inspect the user's
live repository, run firmware tests, verify candidate binary artifacts,
or establish that any firmware change works.

### Improvements in this pass

- Added an action-first priority queue so a new session can begin with artifact identity and the spectrum path instead of rereading the whole brief before knowing the next action.
- Rewrote the tool inventory as a proper Markdown list and made the uncertainty of tool roles explicit.
- Converted the patch-safety run-on paragraph into a numbered checklist and explicitly separated virtual addresses, app-relative offsets, and full-flash offsets.
- Preserved the long-form requirements and historical notes rather than deleting them; the quick briefing is intentionally shorter than the detailed engineering specification.

### Review findings and limits

- The document is internally clear that user-observed spectrum behaviour is not proof of a traced measurement path, and that a PC waterfall would be sequential samples rather than simultaneous SDR/IQ capture unless new evidence proves otherwise.
- The document distinguishes planned, statically analysed, implemented, and hardware-tested work. Keep that distinction in future edits and do not convert a historical test report into a current pass without rerunning it.
- Sections 15 and 16 deliberately repeat some safeguards in context: Section 15 specifies the overall engineering deliverable; Section 16 specifies UI design and acceptance tests. Keep these sections focused rather than merging away their test criteria.
- The candidate update archives and `decrypted_app.bin` remain unverified in this review. Their actual contents, hashes, target variant, and relationship to each other must be inspected before they are treated as usable firmware inputs.
- The suggested menu groups are conceptual. First document the actual menu tree, callback mapping, physical-key events, display constraints, and settings persistence for the selected image.

### Validation performed

- Re-read the document's main technical claims and execution priorities.
- Checked Markdown heading sequence, fenced-code balance, common malformed-list patterns, and repeated status claims with a local script after saving this pass.
- No firmware or repository source files were changed by this document-only pass.

### Next action

Inspect and hash the candidate v1.0.50 archives and `decrypted_app.bin`; match the exact hardware/update variant and source image. Then map the existing spectrum sweep on the confirmed target version. Do not implement menu IDs, offsets, data transport, or firmware patches from the conceptual design alone.

## 19. Artifact audit — 2026-10-12

This audit inspected the checked-out repository artifacts only. It did not
flash hardware, modify firmware bytes, or prove that any candidate can be
accepted by a radio.

- **CONFIRMED:** The pristine v1.0.47 standalone image is present at
  `H3 Plus 0226/H3 Plus 0226/Upgrade Tool--H3 Plus firmware(for ham or unlock)/Update-Kendwood port/TID-H3-Plus-1.0.47.bin`,
  is 790,528 bytes, and hashes to
  `3b2d198b6d6bcce884ea437cccb253efd705ab72c790c04b704c3da75213deda`.
  No firmware bytes changed in this audit.
- **CONFIRMED:** The Type-C v1.0.50 candidate is
  `h3plus-forensics/NEW FILES/H3 Plus 1.0.50-Update-TypeC/TD-H3-PlusV1.0.50.fw`,
  827,808 bytes, SHA-256
  `ab843948ab79871ae911f74688208096b1438d16e660783e7c3adcf3acf416d8`.
- **CONFIRMED:** The Kenwood v1.0.50 candidate is
  `h3plus-forensics/NEW FILES/H3 Plus 1.0.50-Update-Kendwood/TD-H3-PlusV1.0.50.bin`,
  823,296 bytes, SHA-256
  `0dd16ac8a26b58ef62c4681ac8ee018cfd6a276b81eb2049b33f834da016b40e`.
  The candidates have different leading bytes and are not byte-identical;
  no aligned payload equivalence was established. Keep them as separate
  update artifacts.
- **CONFIRMED:** The Type-C archive documentation describes PTT+3 and
  `Update App.exe`; the Kenwood documentation describes PTT+1, CH340,
  `updata.exe`, 1,000,000 baud, and no UBOOT update. These are distinct
  delivery procedures.
- **SUPPORTED HYPOTHESIS:** `decrypted_app.bin` is associated with v1.0.50:
  it is 802,784 bytes, hashes to
  `819d1ad327954e2a76f792d90340a50061f026cb7d3b61a37ece591c5636ea1d`,
  and contains `1.0.50` at file offset `0x9B871` plus `TD-H3` markers.
  **UNKNOWN:** its exact decryption source, target variant, and relationship
  to either v1.0.50 update candidate. Its size and bytes do not by
  themselves prove compatibility or flashability.
- **Files changed:** `h3plus-forensics/results/input_hashes.sha256`,
  `h3plus-forensics/docs/INVESTIGATION_LOG.md`, and this handoff.
- **Commands and tools:** Python 3 `hashlib`, `file`, `unzip -Z1`, archive
  member SHA-256 checks, and direct byte/header comparisons. Exact artifact
  hashes are also recorded in the investigation log and hash manifest.
  Validation passed with `sha256sum -c` (6/6), Python compilation, the
  comparison CLI smoke check, `pytest -q` (7 passed), and `git diff --check`.
- **Next concrete action:** inspect the updater/container format and derive
  whether either v1.0.50 package contains an authenticated/encrypted app
  region matching `decrypted_app.bin`; keep this static and read-only.
  Only after exact source linkage is proven should the spectrum path be
  mapped for that version.
