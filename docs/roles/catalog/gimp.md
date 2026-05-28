# Role: gimp

> **Work in progress** — preliminary draft.

Manages GIMP (GNU Image Manipulation Program), a free and open-source image
editor. Supports standard package operations: install, uninstall, download, and
info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade GIMP |
| `off` | Uninstall GIMP |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that GIMP is installed |

---

## Configuration

No variables. GIMP is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - gimp
  - gimp-off
```

---

## Schema details

Software name: `GIMP`  
Provider: `registry`  
Installer: `gimp-*.exe` (version varies)  
Homepage: https://www.gimp.org/

---

## Notes

GIMP provides tools for photo retouching, image composition, and image authoring.
Supports a wide range of file formats and includes plugin support for extensibility.
