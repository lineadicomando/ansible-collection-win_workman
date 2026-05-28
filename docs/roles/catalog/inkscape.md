# Role: inkscape

> **Work in progress** — preliminary draft.

Manages Inkscape, a free and open-source vector graphics editor. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Inkscape |
| `off` | Uninstall Inkscape |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Inkscape is installed |

---

## Configuration

No variables. Inkscape is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - inkscape
  - inkscape-off
```

---

## Schema details

Software name: `Inkscape`  
Provider: `registry`  
Installer: `inkscape-*.exe` (version varies)  
Homepage: https://inkscape.org/

---

## Notes

Inkscape is used for creating and editing SVG (Scalable Vector Graphics) files.
Suitable for logo design, illustrations, diagrams, and icon creation.
