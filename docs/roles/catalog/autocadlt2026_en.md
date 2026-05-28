# Role: autocadlt2026_en

> **Work in progress** — preliminary draft.

Manages AutoCAD LT 2026 (English), a professional 2D CAD (Computer-Aided Design)
software for architecture, engineering, and construction. Supports standard package
operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade AutoCAD LT 2026 (English) |
| `off` | Uninstall AutoCAD LT 2026 (English) |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that AutoCAD LT 2026 (English) is installed |

---

## Configuration

No variables. AutoCAD LT 2026 is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - autocadlt2026_en
  - autocadlt2026_en-off
```

---

## Schema details

Software name: `AutoCAD LT 2026 (English)`  
Provider: `registry`  
Installer: `AutoCAD_LT_2026_*.exe` (version varies)  
Homepage: https://www.autodesk.com/products/autocad-lt/

---

## Notes

AutoCAD LT is a professional 2D drafting and design tool. English language version
is optimized for international use. Requires Autodesk account for licensing.
