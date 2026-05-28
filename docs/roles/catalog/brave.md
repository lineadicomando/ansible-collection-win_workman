# Role: brave

> **Work in progress** — preliminary draft.

Manages Brave Browser, a privacy-focused Chromium-based web browser. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Brave |
| `off` | Uninstall Brave |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Brave is installed |

---

## Configuration

No variables. Brave is installed with default system-level configuration.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - brave
  - brave-off
```

---

## Schema details

Software name: `Brave Browser`  
Provider: `registry`  
Installer: `brave_installer-x64.exe`  
Homepage: https://brave.com/

---

## Notes

No special configuration or behavior.
