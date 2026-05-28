# Role: filezilla

FileZilla Client is a free, open-source FTP, SFTP, and FTPS client for Windows.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade FileZilla Client |
| `off` | Uninstall FileZilla Client |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that FileZilla Client is installed |

---

## Configuration

No user-configurable variables. The installer runs silently with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - filezilla
  - filezilla-off
```

---

## Schema details

Software name: `FileZilla Client`
Provider: `registry`
Installer: `FileZilla_3.70.5_win64-setup.exe`
Version: `3.70.5`
Homepage: https://filezilla-project.org/

---

## Notes

The installer is a 64-bit NSIS setup. Silent installation uses the `/S` flag.
`uninstall_via_helper` is enabled to handle NSIS unregistration reliably.

Verify that `searchName` matches the `DisplayName` in the Windows Uninstall registry
before deploying to a new OS version:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
  Where-Object { $_.DisplayName -like 'FileZilla*' } |
  Select-Object DisplayName, DisplayVersion
```
