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

---

## Configuration

No variables. SketchUp 2026 is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - sketchup2026
  - sketchup2026-off
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
