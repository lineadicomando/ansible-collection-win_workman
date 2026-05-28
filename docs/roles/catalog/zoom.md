# Role: zoom

> **Work in progress** — preliminary draft.

Manages Zoom, a cloud-based unified communications platform for video conferencing,
webinars, and team collaboration. Supports standard package operations: install,
uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Zoom |
| `off` | Uninstall Zoom |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Zoom is installed |

---

## Configuration

No variables. Zoom is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - zoom
  - zoom-off
```

---

## Schema details

Software name: `Zoom`  
Provider: `registry`  
Installer: `ZoomInstaller.exe` (version varies)  
Homepage: https://www.zoom.us/

---

## Notes

Zoom client supports HD video/audio, screen sharing, and recording capabilities.
Requires internet connection for functionality. Can be pre-configured with SSO
for enterprise deployments.
