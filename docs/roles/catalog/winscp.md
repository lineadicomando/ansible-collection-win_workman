# Role: winscp

WinSCP is an open-source SFTP, FTP, WebDAV, S3, and SCP client for Windows.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade WinSCP |
| `off` | Uninstall WinSCP |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that WinSCP is installed |

---

## Configuration

No user-configurable variables. The MSI installer runs silently with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - winscp
  - winscp-off
```

---

## Schema details

Software name: `WinSCP`
Provider: `msi`
Installer: `WinSCP-6.3.8.msi`
Homepage: https://winscp.net/

---

## Notes

The MSI installer is the official package distributed via SourceForge. Silent
installation is handled automatically by the `msi` provider. The role uses
`uninstall_before_upgrade: true` to ensure clean upgrades between versions.

Verify that `searchName` matches the `DisplayName` in the Windows Uninstall registry
before deploying to a new OS version:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
  Where-Object { $_.DisplayName -like 'WinSCP*' } |
  Select-Object DisplayName, DisplayVersion
```
