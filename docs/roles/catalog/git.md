# Role: git

Git for Windows is the official Windows port of the Git version control system.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Git for Windows |
| `off` | Uninstall Git for Windows |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Git is installed |

---

## Configuration

No user-configurable variables. The installer runs silently with default settings.

Example:

```yaml
win_workman_tasks:
  - git
  - git-off
```

---

## Schema details

Software name: `Git`
Provider: `registry`
Installer: `Git-2.54.0-64-bit.exe`
Version: `2.54.0`
Homepage: https://gitforwindows.org/

---

## Notes

The installer is an Inno Setup executable. Silent installation uses
`/VERYSILENT /NORESTART /NOCANCEL /SP-`. The same flags apply to uninstall.

Verify that `searchName` matches the `DisplayName` in the Windows Uninstall registry
before deploying to a new OS version:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
  Where-Object { $_.DisplayName -like 'Git' } |
  Select-Object DisplayName, DisplayVersion
```
