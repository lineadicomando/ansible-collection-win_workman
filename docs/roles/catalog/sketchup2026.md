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
| `license` | Deploy `activation_info.txt` to pre-fill the classic/network license |
| `unlicense` | Remove the deployed `activation_info.txt` |

---

## Configuration

Installation needs no variables. The `license` action reads:

| Variable | Default | Description |
|---|---|---|
| `win_workman_sketchup2026_serial_number` | `''` | Classic/network serial number (keep it in a vault) |
| `win_workman_sketchup2026_auth_code` | `''` | Classic/network authorization code (keep it in a vault) |
| `win_workman_sketchup2026_allow_reactivation` | `true` | Adds the `allow_reactivation` flag so a renewed license re-activates on its own |
| `win_workman_sketchup2026_program_data_dir` | `C:\ProgramData\SketchUp\SketchUp 2026` | Directory SketchUp reads `activation_info.txt` from |

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

Removing a seat is GUI-only (**Help > License > Remove License**), and uninstalling
SketchUp does *not* free it — `unlicense` only deletes the pre-fill file. Always
remove the license from the workstation before reimaging it.

Reference: https://help.sketchup.com/en/admin/managing-network-license
