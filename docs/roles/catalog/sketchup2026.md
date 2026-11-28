# sketchup2026 — SketchUp 2026

Installs SketchUp 2026 (`/silent /FEATURES=it`) and deploys its classic/network
license.

## Actions

| Action | Does |
|---|---|
| `on` | Installs [vcredist14](vcredist14.md) first, then SketchUp; unlike other roles, `nodep` does not skip the dependency |
| `license` | Writes `activation_info.txt` (serial, auth code, `allow_reactivation`); when its content changes, also removes `SketchUp.lic` |
| `unlicense` | Removes `activation_info.txt` and `SketchUp.lic` |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_sketchup2026_serial_number` | `''` | Classic/network serial number (vault); required by `license` |
| `win_workman_sketchup2026_auth_code` | `''` | Authorization code (vault); required by `license` |
| `win_workman_sketchup2026_allow_reactivation` | `true` | Adds `allow_reactivation`, so a renewed license re-activates on its own |
| `win_workman_sketchup2026_program_data_dir` | `C:\ProgramData\SketchUp\SketchUp 2026` | Where `activation_info.txt` and `SketchUp.lic` live |
| `win_workman_sketchup2026_process_names` | `[SketchUp, LayOut, Style Builder]` | Processes that block a license change |
| `win_workman_sketchup2026_force_close` | `false` | Kill those processes instead of failing (unsaved work is lost) |

## Notes

- Trimble offers no command-line activation; `activation_info.txt` is the only
  documented mass-deployment mechanism
  (<https://help.sketchup.com/en/admin/managing-network-license>). Trimble describes
  it as a pre-fill confirmed with **Add License**; on SketchUp 2026 the first launch
  reads it and activates with no interaction at all. SketchUp still has to be opened
  once per workstation.
- The activated license lives in `SketchUp.lic` and wins over `activation_info.txt`
  while it exists. Removing it on changed credentials makes the next launch activate
  the new license: verified 2026-10-01 moving a workstation between two network
  licenses.
- A running instance keeps its seat on the license it started with: `license` and
  `unlicense` fail, files untouched, when one of the processes runs and a change is
  due. The check runs only when there is something to change.
- Seat removal is documented only through **Help > License > Remove License**; whether
  `unlicense` releases the seat vendor-side is not verified. A seat extracted for
  offline use is not detected and stays taken until it expires.
- Run `unlicense` before `off`: whether the uninstaller removes `SketchUp.lic` is not
  verified. With both files gone, `off` leaves nothing under `C:\ProgramData\SketchUp`.
