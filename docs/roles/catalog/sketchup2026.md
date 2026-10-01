# Role: sketchup2026

> **Work in progress** — preliminary draft.

Manages SketchUp 2026, a 3D modeling software for architecture, urban planning,
interior design, and construction. Supports standard package operations: install,
uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade SketchUp 2026 |
| `off` | Uninstall SketchUp 2026 |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that SketchUp 2026 is installed |
| `license` | Deploy `activation_info.txt` to pre-fill the classic/network license; on changed credentials also remove `SketchUp.lic` |
| `unlicense` | Remove the deployed `activation_info.txt` and the activated `SketchUp.lic` |

---

## Configuration

Installation needs no variables. The `license` action reads:

| Variable | Default | Description |
|---|---|---|
| `win_workman_sketchup2026_serial_number` | `''` | Classic/network serial number (keep it in a vault) |
| `win_workman_sketchup2026_auth_code` | `''` | Classic/network authorization code (keep it in a vault) |
| `win_workman_sketchup2026_allow_reactivation` | `true` | Adds the `allow_reactivation` flag so a renewed license re-activates on its own |
| `win_workman_sketchup2026_program_data_dir` | `C:\ProgramData\SketchUp\SketchUp 2026` | Directory SketchUp reads `activation_info.txt` from |
| `win_workman_sketchup2026_force_close` | `false` | Kill a running SketchUp/LayOut instead of failing when a license change is due |

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - sketchup2026
  - sketchup2026-license
```

---

## Schema details

Software name: `SketchUp 2026`  
Provider: `registry`  
Installer: `SketchUp_2026_*.exe` (version varies)  
Homepage: https://www.sketchup.com/

---

## Notes

SketchUp is an intuitive 3D modeling tool with a large library of pre-made models
and textures. Free and Pro versions available. Pro version requires license activation.

Trimble offers no command-line activation. The only documented mass-deployment
mechanism is the `activation_info.txt` file, which the `license` action writes.
Trimble's docs describe it as a *pre-fill* that a user then confirms with **Add
License**; in practice, on SketchUp 2026 the first launch reads the file and
activates the license with no interaction at all.

The activated license lives in `SketchUp.lic`, next to `activation_info.txt`, and wins
over it for as long as it exists. When `license` deploys different credentials it
removes `SketchUp.lic`, so the next launch activates the new license; this was verified
switching a workstation between two network licenses. `unlicense` removes both files.

A running instance keeps its seat on the license it started with, so `license` and
`unlicense` fail on a host where SketchUp or LayOut is open and a change is due,
leaving the files untouched. `win_workman_sketchup2026_force_close: true` kills the
processes instead, losing unsaved work. A seat extracted for offline use is not
detected and stays taken until the extraction expires.

Trimble documents seat removal only through **Help > License > Remove License**. Run
`unlicense` before `off`: whether the uninstaller removes `SketchUp.lic` on its own has
not been verified. With both files gone, `off` leaves nothing under
`C:\ProgramData\SketchUp`.

Reference: https://help.sketchup.com/en/admin/managing-network-license
