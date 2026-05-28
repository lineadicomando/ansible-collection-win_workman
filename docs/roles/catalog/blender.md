# Role: blender

Blender is a free and open-source 3D creation suite for modelling, animation,
rendering, and video editing.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Blender |
| `off` | Uninstall Blender |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Blender is installed |

---

## Configuration

No user-configurable variables. The MSI installer runs silently with default settings.

Example:

```yaml
win_workman_tasks:
  - blender
  - blender-off
```

---

## Schema details

Software name: `Blender`
Provider: `msi`
Installer: `blender-5.1.2-windows-x64.msi`
Version: `5.1.2`
Homepage: https://www.blender.org/

---

## Notes

The MSI installer includes a `product_id` for reliable uninstall detection.
Silent installation and removal are handled automatically by the `msi` provider.

Verify that `searchName` matches the `DisplayName` in the Windows Uninstall registry
before deploying to a new OS version:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
  Where-Object { $_.DisplayName -like 'Blender' } |
  Select-Object DisplayName, DisplayVersion
```
