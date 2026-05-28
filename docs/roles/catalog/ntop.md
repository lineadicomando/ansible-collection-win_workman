# Role: ntop

> **Work in progress** — preliminary draft.

Manages NTop, a Windows port of the Unix `top` command for real-time process
monitoring. Supports standard package operations: install, uninstall, download,
and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade NTop |
| `off` | Uninstall NTop |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that NTop is installed |

---

## Configuration

No variables. NTop is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - ntop
  - ntop-off
```

---

## Schema details

Software name: `NTop`  
Provider: `registry`  
Installer: `ntop*.exe` (version varies)  
Homepage: https://github.com/gsass1/NTop

---

## Notes

NTop provides a real-time process and system resource view in the Windows
terminal, analogous to `top` on Linux/macOS.
