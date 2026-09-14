# Role: audacity

> **Work in progress** — preliminary draft.

Manages Audacity, a free and open-source multi-track audio editor and recorder.
Supports standard package operations: install, uninstall, download, and info
queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Audacity |
| `off` | Uninstall Audacity |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Audacity is installed |

---

## Configuration

No variables. Audacity is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - audacity
  - audacity-off
```

---

## Schema details

Software name: `Audacity`  
Provider: `msi`  
Installer: `audacity-win-4.0.0-x86_64.msi`  
Homepage: https://www.audacityteam.org

---

## Notes

Audacity 4.0 is the first release of the new major line and the first shipped as an
MSI; the 3.x releases were NSIS installers. Only the x86_64 package is covered —
upstream also publishes an arm64 MSI.

The MSI carries a WiX `MajorUpgrade`, so a newer 4.x build replaces the installed one
in place and `uninstall_before_upgrade` is not needed.

`searchName` is scoped to `Audacity 4*` because the registry `DisplayName` is the MSI
`ProductName`, `Audacity 4.0`. An existing Audacity 3.x install is therefore neither
detected nor removed by this role, and the two would end up side by side: uninstall
3.x separately if that is not wanted.

The MSI creates the desktop and Start Menu shortcuts itself, so the schema declares
none — but it ships without an `ALLUSERS` property, so on its own it puts them in the
profile of whichever user runs the installer, which over SSH is the Ansible account and
not the people using the machine. The role therefore passes `ALLUSERS=1`, which moves
them to `%Public%\Desktop` and `%ProgramData%`. Verified on a lab VM: without the
argument the only shortcuts created were under `C:\Users\maint`.

The application lands in `%ProgramFiles%\Audacity 4\bin\Audacity4.exe`.
