# Role: vlc

> **Work in progress** — preliminary draft.

Manages VLC Media Player, a free and open-source multimedia player. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade VLC |
| `off` | Uninstall VLC |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that VLC is installed |

---

## Configuration

No variables. VLC is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - vlc
  - vlc-off
```

---

## Schema details

Software name: `VLC Media Player`  
Provider: `registry`  
Installer: `vlc-*.exe` (version varies)  
Homepage: https://www.videolan.org/

---

## Notes

VLC supports a wide range of audio and video formats. Can also function as a
streaming server and supports subtitles. Known for handling corrupted or incomplete media files.
