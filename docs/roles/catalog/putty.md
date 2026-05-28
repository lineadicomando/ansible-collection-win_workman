# Role: putty

PuTTY is a free SSH, Telnet, and serial console client for Windows.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade PuTTY |
| `off` | Uninstall PuTTY |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that PuTTY is installed |

---

## Configuration

No user-configurable variables. The MSI installer runs silently with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - putty
  - putty-off
```

---

## Schema details

Software name: `PuTTY`
Provider: `msi`
Installer: `putty-64bit-0.83-installer.msi`
Homepage: https://www.chiark.greenend.org.uk/~sgtatham/putty/

---

## Notes

The MSI installer is the official 64-bit package distributed by Simon Tatham.
Silent installation is handled automatically by the `msi` provider. The role uses
`uninstall_before_upgrade: true` to ensure clean upgrades between versions.

Verify that `searchName` matches the `DisplayName` in the Windows Uninstall registry
before deploying to a new OS version:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
  Where-Object { $_.DisplayName -like 'PuTTY*' } |
  Select-Object DisplayName, DisplayVersion
```
