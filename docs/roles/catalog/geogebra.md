# Role: geogebra

> **Work in progress** — preliminary draft.

Manages GeoGebra, a dynamic mathematics software for geometry, algebra, calculus,
and statistics education. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade GeoGebra |
| `off` | Uninstall GeoGebra |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that GeoGebra is installed |

---

## Configuration

No variables. GeoGebra is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - geogebra
  - geogebra-off
```

---

## Schema details

Software name: `GeoGebra`  
Provider: `registry`  
Installer: `GeoGebra-Windows-Installer.exe`  
Homepage: https://www.geogebra.org/

---

## Notes

No special configuration or behavior. GeoGebra is primarily used in mathematics
education and may require Java Runtime Environment (JRE) on some systems.
