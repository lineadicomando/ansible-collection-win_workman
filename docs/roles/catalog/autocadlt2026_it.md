# Role: autocadlt2026_it

> **Work in progress** — preliminary draft.

Manages AutoCAD LT 2026 (Italian), a professional 2D CAD (Computer-Aided Design)
software for architecture, engineering, and construction. Supports standard package
operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade AutoCAD LT 2026 (Italian) |
| `off` | Uninstall AutoCAD LT 2026 (Italian) |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that AutoCAD LT 2026 (Italian) is installed |

---

## Configuration

No variables. AutoCAD LT 2026 is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - autocadlt2026_it
  - autocadlt2026_it-off
```

---

## Schema details

Software name: `AutoCAD LT 2026 (Italian)`  
Provider: `registry`  
Installer: `AutoCAD_LT_2026_*.exe` (version varies)  
Homepage: https://www.autodesk.com/products/autocad-lt/

---

## Notes

AutoCAD LT is a professional 2D drafting and design tool. Italian language version
is localized for Italian-speaking users. Requires Autodesk account for licensing.
