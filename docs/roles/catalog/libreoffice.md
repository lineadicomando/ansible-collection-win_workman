# libreoffice — LibreOffice

Installs LibreOffice from the TDF x64 MSI, Still branch by default, Fresh on request.

## Actions

| Action | Does |
|---|---|
| `<action>-fresh` | Any standard action on the Fresh branch instead of Still (`libreoffice-on-fresh`, `libreoffice-info-fresh`, `libreoffice-download-fresh`) |
| `rm_data` | Force-closes `soffice.bin` and deletes `AppData\Roaming\LibreOffice` in every local profile (resets per-user settings) |

## Notes

- Still is the branch TDF recommends for institutions. Both branch versions, full
  versions and checksums are in `vars/main.yaml`, keyed `still` / `fresh`.
- TDF publishes no checksum file, only a detached GPG signature: the pinned sha256
  are those of MSIs whose `.asc` verifies against the LibreOffice Build Team key
  (fingerprint in `vars/main.yaml`).
- `searchName` matches any release (`LibreOffice [0-9]*.[0-9]*.[0-9]*.[0-9]*`):
  every LibreOffice MSI shares one UpgradeCode, so a new version replaces the
  installed one and `on` has to see that one to upgrade it. Four dotted numbers keep
  out the help packs (`LibreOffice 26.2 Help Pack (...)`).
- The Online Update feature installs the *LibreOffice Maintenance Service*
  (`update_service.exe`), which the MSI never removes: its `uninstall_updateservice`
  action cannot run under `REMOVE=ALL`. `off` deletes the service, its
  `HKLM\SOFTWARE\LibreOffice\MaintenanceService` key (and the parent key if empty)
  and, via `cleanup_paths`, `%ProgramFiles%\LibreOffice`. The feature is not left out
  at install time: with `REMOVE=gm_o_Onlineupdate` the MSI installs nothing on a new
  product (unnamed features keep their current, absent, state), and `ADDLOCAL=ALL`
  would add every optional feature.
- Tested 2026-11-25 on a Windows test VM with 26.2.6 installed: info saw it, on
  upgraded it to 26.2.7, a second on was a no-op, is_present passed, and after off no
  service, registry key, directory, shortcut or uninstall entry was left. Fresh was
  upgraded to 26.8.3 from 26.2.7 and removed in an earlier run.
