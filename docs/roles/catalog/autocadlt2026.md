# autocadlt2026 — AutoCAD LT 2026

Installs and removes AutoCAD LT 2026 (ODIS bundle from `edutrial.autodesk.com`, pinned
sha256; a licence entitlement is still required). One role for all locales: `en`,
`it`.

## Actions

| Action | Does |
|---|---|
| `on[-<lang>]` | Install (default action); no-op if the locale is already registered |
| `off` | Uninstall the installed locale, keeping the shared Autodesk stack |
| `off-full` | Uninstall and purge the shared Autodesk stack |

`on` and `off` are reimplemented; the other standard actions go through pkg_utils.

## Locales

Resolved in this order: an explicit code in the task (`autocadlt2026-on-it`); the host
locale from `pkg_utils/detect_lang` (`it-IT` → `it`); `en`. Each locale is a separate
ODIS bundle with its own GUID, and the two cannot coexist: `on` fails if the other one
is installed (remove it with `autocadlt2026-off` first). `off` detects the installed
locale by wildcard and aligns to it.

Detection keys on the product entry (`AutoCAD LT 2026 - Italiano (Italian)`), not on
the ODIS bundle entry (`Autodesk AutoCAD LT 2026 - ...`), which the Italian bundle does
not register in the uninstall hive.

## Install

- Two files per locale, about 2.7 GB in total (SFX bootstrapper plus `.7z` payload),
  copied to every host: budget the time on a full lab.
- Presence is decided by the registry alone: with `acadlt.exe` on disk but no
  registration, the install runs again (and re-extracts the `.pit` the licence helper
  needs).
- The SFX spawns `db-bootstrap.exe`, which writes the ODIS metadata the uninstaller
  needs but can block for hours on network calls. The role starts the SFX without
  waiting, polls until both the registry entry and `bundleManifest.xml` exist (up to
  1800 s), then stops `db-bootstrap.exe` so the SFX exits.
- Then it reboots only if a restart is pending, and registers the educational licence
  with `AdskLicensingInstHelper register` run as SYSTEM.

## Uninstall

- The ODIS uninstaller runs against the bundle manifest found by the known bundle GUID;
  exit codes `0` and `1604` (suspended, reboot needed) count as success. It waits on
  the uninstaller process alone, up to `win_workman_autocadlt2026_uninstall_timeout`
  (1800 s): `Start-Process -Wait` waits for the job object, which `ADPClientService.exe`
  keeps open for minutes after the removal.
- `off-full` also removes Autodesk Access, Genuine Service, Identity Manager, "Open in
  Desktop", "Save to Web & Mobile", and finally `C:\Program Files\Autodesk` and
  `C:\ProgramData\Autodesk` wholesale. Use it only when no other Autodesk product
  remains; never to tidy up before an install, since it wipes healthy components the
  install has to put back.
- The shared components are matched by display-name pattern, wildcarded to stay
  locale-independent (`Salva su Autodesk Web & Mobile` / `Save to Autodesk Web &
  Mobile`), and their GUIDs resolved at run time (`tasks/find_products.yaml`): pinned
  GUIDs went stale and `win_package` silently skipped them. Autodesk Access is not an
  MSI: its package manifest is derived from the id detected for it, and its uninstall
  runs only if that manifest is on disk.

## Notes

- Releases install side by side: run [autocadlt2023](autocadlt2023.md)`-off` first to
  replace rather than add.
- The installer is read from `win_workman_remote_tmp` (where `pkg_utils/win_copy`
  puts it), not from `ansible_remote_tmp`.
- Locale data, GUIDs, product key and timeout are in `vars/main.yaml` (role vars, not
  overridable from the inventory).
