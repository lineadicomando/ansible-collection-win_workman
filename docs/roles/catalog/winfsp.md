# Role: winfsp

> **Work in progress** — preliminary draft.

Manages WinFsp (Windows File System Proxy), a framework for implementing file systems
in Windows userspace. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade WinFsp |
| `off` | Uninstall WinFsp |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that WinFsp is installed |

---

## Configuration

No variables. WinFsp is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - winfsp
  - winfsp-off
```

---

## Schema details

Software name: `WinFsp`  
Provider: `registry`  
Installer: `winfsp*.exe` (version varies)  
Homepage: https://github.com/billziss-gh/winfsp

---

## Notes

WinFsp is required by many cloud storage integrations and network file system clients.
Enables implementation of custom file systems in user-mode applications.
