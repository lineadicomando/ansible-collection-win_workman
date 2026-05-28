# Role: p7zip

> **Work in progress** — preliminary draft.

Manages 7-Zip, a free and open-source file archiver with high compression ratio.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade 7-Zip |
| `off` | Uninstall 7-Zip |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that 7-Zip is installed |

---

## Configuration

No variables. 7-Zip is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - p7zip
  - p7zip-off
```

---

## Schema details

Software name: `7-Zip`  
Provider: `registry`  
Installer: `7z*.exe` (version varies)  
Homepage: https://www.7-zip.org/

---

## Notes

7-Zip supports .7z, .zip, .rar, and many other archive formats. Integrates with
Windows Explorer for easy context menu access.
