# Role: powertoys

> **Work in progress** — preliminary draft.

Installs Microsoft PowerToys, a set of utilities for power users to tune and
streamline their Windows experience. Supports standard package operations:
install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Microsoft PowerToys |
| `off` | Uninstall Microsoft PowerToys |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Microsoft PowerToys is installed |

---

## Variables

No role-specific variables. Standard `pkg_utils` defaults apply.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - powertoys
  - powertoys-off
```

---

## Schema details

Software name: `PowerToys (Preview)`  
Provider: `registry`  
Installer: `PowerToysSetup-0.99.1-x64.exe`  
Homepage: https://github.com/microsoft/PowerToys

---

## Notes

Requires Windows 11. Only the 64-bit installer is provided; there is no 32-bit build.
