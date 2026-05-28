# Role: nircmd

> **Work in progress** — preliminary draft.

Manages NirCmd, a command-line tool for Windows system utilities and automation.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade NirCmd |
| `off` | Uninstall NirCmd |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that NirCmd is installed |

---

## Configuration

No variables. NirCmd is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - nircmd
  - nircmd-off
```

---

## Schema details

Software name: `NirCmd`  
Provider: `registry`  
Installer: `nircmd*.exe` (version varies)  
Homepage: https://www.nirsoft.net/utils/nircmd.html

---

## Notes

NirCmd provides command-line utilities for controlling Windows system functions
including volume control, monitor control, and clipboard operations.
