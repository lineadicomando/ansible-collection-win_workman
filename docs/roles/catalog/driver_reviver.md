# Role: driver_reviver

> **Work in progress** — preliminary draft.

Driver Reviver is a commercial driver updater for Windows by ReviverSoft (Corel).
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Driver Reviver |
| `off` | Uninstall Driver Reviver |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Driver Reviver is installed |

---

## Variables

No user-configurable variables. The installer runs silently with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - driver_reviver
  - driver_reviver-off
```

---

## Schema details

Software name: `Driver Reviver`  
Provider: `registry`  
Installer: `DriverReviverSetup_5.44.0.8.exe`  
Version: `5.44.0.8`  
Homepage: https://www.reviversoft.com

---

## Notes

The setup is an NSIS installer. Besides the NSIS `/S` flag the vendor script reads
its own switches: `/NO_UI` and `/DISABLEPOSTPAGES` are the two that matter for an
unattended run — without them the installer still opens the post-install pages and
launches the application at the end. `uninstall_via_helper` runs `Uninstall.exe /S`
directly, the same pattern used by the other NSIS packages in the catalog.

The setup binary is 32-bit but switches to the 64-bit registry view, so on an x64
target the product lands in `C:\Program Files\ReviverSoft\Driver Reviver` and its
Uninstall key is `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Driver Reviver`
— *not* under `Program Files (x86)` / `WOW6432Node`, which is where a 32-bit setup
would normally put them.

**What the install leaves on the machine.** Verified on a Windows 11 x64 target:

| Item | Value |
|---|---|
| Install tree | `C:\Program Files\ReviverSoft\Driver Reviver` (~40 MB) |
| Uninstall entry | `Driver Reviver`, publisher `Corel Corporation` |
| Shortcuts | `%Public%\Desktop\Driver Reviver.lnk` and Start Menu `ReviverSoft\Driver Reviver` |
| Scheduled tasks | `Start Driver Reviver Schedule`, `… Update`, `… Check Driver Update`, `… First Schedule`, `… for User(logon)` |
| Companion | `C:\Program Files\ReviverSoft\Smart Monitor` (~26 MB) |
| Service | `ReviverSoft Smart Monitor Service`, start type Automatic, running |

The shortcuts and the scheduled tasks are created by the installer itself, so none
are declared in the schema.

**Licence.** Driver Reviver installs as a trial: it scans and lists outdated
drivers, but downloading and applying them requires a registration code entered in
the GUI. The role only deploys the product; it does not activate it.

**Bundled Smart Monitor.** The same setup also deploys "ReviverSoft Smart Monitor",
the notification component shared by the Reviver products. It installs a service
that starts automatically and a tray application, but — unlike Driver Reviver — it
registers **no Uninstall entry**, so it does not show up in *Apps & features* and
`detect_sw` cannot see it. `driver_reviver-off` leaves it in place, both because it
is invisible to the package workflow and because another ReviverSoft product on the
same machine would stop working without it. To remove it once no other Reviver
product is installed, call its own uninstaller:

```powershell
Stop-Service 'ReviverSoft Smart Monitor Service'
& 'C:\Program Files\ReviverSoft\Smart Monitor\Uninstall.exe' /S _?='C:\Program Files\ReviverSoft\Smart Monitor'
```

Verify that `searchName` still matches the `DisplayName` in the Uninstall registry
before deploying to a new OS version:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
  Where-Object { $_.DisplayName -like 'Driver Reviver*' } |
  Select-Object DisplayName, DisplayVersion, InstallLocation
```
