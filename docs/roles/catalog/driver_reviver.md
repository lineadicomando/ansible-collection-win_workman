# driver_reviver — Driver Reviver

Driver Reviver, commercial driver updater by ReviverSoft (Corel), NSIS installer
(`registry` provider, uninstall through the helper with `Uninstall.exe /S`). It
installs as a trial: it scans and lists outdated drivers, but applying them needs a
registration code entered in the GUI. The role deploys it, it does not activate it.

## Notes

- Install switches: besides the NSIS `/S`, the vendor's `/NO_UI` and
  `/DISABLEPOSTPAGES`; without them the setup still opens its post-install pages and
  launches the application at the end.
- The setup binary is 32-bit but switches to the 64-bit registry view: the product
  lands in `C:\Program Files\ReviverSoft\Driver Reviver` and its key is
  `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Driver Reviver`, not under
  `Program Files (x86)` / `WOW6432Node`.
- The vendor link `https://www.reviversoft.com/downloads/DriverReviverSetup.exe`
  redirects to the current build; the schema pins the resolved URL so the checksum
  stays valid when a new release is published.
- What the install leaves, verified on a Windows 11 x64 target:

  | Item | Value |
  |---|---|
  | Install tree | `C:\Program Files\ReviverSoft\Driver Reviver` (~40 MB) |
  | Uninstall entry | `Driver Reviver`, publisher `Corel Corporation` |
  | Shortcuts | `%Public%\Desktop\Driver Reviver.lnk` and Start Menu `ReviverSoft\Driver Reviver` |
  | Scheduled tasks | `Start Driver Reviver Schedule`, `… Update`, `… Check Driver Update`, `… First Schedule`, `… for User(logon)` |
  | Companion | `C:\Program Files\ReviverSoft\Smart Monitor` (~26 MB) |
  | Service | `ReviverSoft Smart Monitor Service`, Automatic, running |

  The installer creates the shortcuts and the scheduled tasks and `Uninstall.exe`
  removes them, so the schema declares none.
- Bundled Smart Monitor: the notification component shared by the Reviver products,
  with an auto-start service and a tray application, registers **no Uninstall
  entry**. It is invisible to `detect_sw` and to *Apps & features*, and
  `driver_reviver-off` leaves it in place (another Reviver product would also need
  it). To remove it once no other Reviver product is installed:

  ```powershell
  Stop-Service 'ReviverSoft Smart Monitor Service'
  & 'C:\Program Files\ReviverSoft\Smart Monitor\Uninstall.exe' /S _?='C:\Program Files\ReviverSoft\Smart Monitor'
  ```
