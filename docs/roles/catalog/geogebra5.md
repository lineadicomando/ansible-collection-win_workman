# Role: geogebra5

> **Work in progress** — preliminary draft.

Manages GeoGebra Classic 5, a dynamic mathematics software for geometry, algebra,
calculus, and statistics education. Supports standard package operations: install,
uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade GeoGebra Classic 5 |
| `off` | Uninstall GeoGebra Classic 5 |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that GeoGebra Classic 5 is installed |

---

## Configuration

No variables. GeoGebra Classic 5 is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - geogebra5
  - geogebra5-off
```

---

## Schema details

Software name: `GeoGebra Classic 5`  
Provider: `registry`  
Installer: `GeoGebra-Classic-5-*.exe` (version varies)  
Homepage: https://www.geogebra.org/

---

## Notes

GeoGebra Classic 5 is the stable legacy version of GeoGebra. Suitable for all
educational levels from primary to university mathematics instruction.
