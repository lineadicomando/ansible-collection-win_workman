# Role: peazip

> **Work in progress** — preliminary draft.

Manages PeaZip, a free and open-source file archiver and file manager supporting
over 200 archive formats. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade PeaZip |
| `off` | Uninstall PeaZip |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that PeaZip is installed |

---

## Configuration

No variables. PeaZip is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - peazip
  - peazip-off
```

---

## Schema details

Software name: `PeaZip`  
Provider: `registry`  
Installer: `peazip-*.WIN64.exe` (version varies)  
Homepage: https://github.com/peazip/PeaZip/

---

## Notes

PeaZip supports over 200 archive formats including 7z, zip, rar, tar, and many
others. Provides both a GUI file manager and command-line tools. Uses Inno Setup
for installation.
