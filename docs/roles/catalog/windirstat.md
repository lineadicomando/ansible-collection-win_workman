# Role: windirstat

> **Work in progress** — preliminary draft.

Manages WinDirStat, a free tool to analyze disk usage by scanning directories and
visualizing space usage. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade WinDirStat |
| `off` | Uninstall WinDirStat |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that WinDirStat is installed |

---

## Configuration

No variables. WinDirStat is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - windirstat
  - windirstat-off
```

---

## Schema details

Software name: `WinDirStat`  
Provider: `registry`  
Installer: `windirstat*.exe` (version varies)  
Homepage: https://windirstat.net/

---

## Notes

WinDirStat visualizes disk usage with a graphical treemap to quickly identify
large folders and files consuming disk space.
