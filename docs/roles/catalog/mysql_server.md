# Role: mysql_server

MySQL Server is an open-source relational database management system by Oracle.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade MySQL Server (installs `vcredist14` first) |
| `off` | Uninstall MySQL Server |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that MySQL Server is installed |

---

## Configuration

No user-configurable variables.

Example:

```yaml
win_workman_tasks:
  - mysql_server
  - mysql_server-off
```

---

## Schema details

Software name: `MySQL Server`
Provider: `msi`
Installer: `mysql-9.7.0-winx64.msi`
Version: `9.7.0`
Homepage: https://www.mysql.com/

---

## Notes

**Dependency**: the `on` action automatically installs
[`vcredist14`](vcredist14.md) (Visual C++ Redistributable) before proceeding,
which is a runtime requirement for MySQL Server on Windows.

**Upgrade behaviour**: `uninstall_before_upgrade` is enabled. MySQL Server MSI
installers do not support in-place major version upgrades; the existing version
is removed cleanly before the new one is installed.

Verify that `searchName` matches the `DisplayName` in the Windows Uninstall registry
before deploying to a new OS version:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
  Where-Object { $_.DisplayName -like 'MySQL Server 9*' } |
  Select-Object DisplayName, DisplayVersion
```
