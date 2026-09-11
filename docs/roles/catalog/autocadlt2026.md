# Role: autocadlt2026

Installs and removes AutoCAD LT 2026, Autodesk's 2D CAD application. The locale
is auto-detected from the Windows host, so there is a **single** role for all
supported languages — not one role per language.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install AutoCAD LT 2026 (default action) |
| `off` | Uninstall AutoCAD LT 2026 |
| `download` | Download the installer to storage |
| `copy` | Copy the installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that AutoCAD LT 2026 is installed |

`on` and `off` are reimplemented by the role; the remaining actions go through
the standard `pkg_utils` package workflow.

```yaml
win_workman_tasks:
  - autocadlt2026           # install, locale from the host
  - autocadlt2026-on-it     # force the Italian bundle
  - autocadlt2026-off       # uninstall, keeping shared Autodesk components
  - autocadlt2026-off-full  # uninstall and purge all shared Autodesk components
```

---

## Locales

Supported: `en`, `it`. The locale is resolved in this order:

1. an explicit code in the task argv — `autocadlt2026-on-it`;
2. the host locale, read by `pkg_utils/detect_lang` (`it-IT` → `it`);
3. `en` as a fallback.

Each locale is a **separate ODIS bundle with its own GUID**, and the two cannot
coexist on the same host. If a different locale is already installed, `on` fails
with an explicit message instead of installing on top; remove the other one with
`autocadlt2026-off` first.

Detection keys on the product entry (`AutoCAD LT 2026 - Italiano (Italian)`),
not on the ODIS bundle entry (`Autodesk AutoCAD LT 2026 - ...`): the Italian
bundle does not register the latter in the Windows uninstall hive.

---

## Install

The download is two files per locale, roughly **2.7 GB in total** — an SFX
bootstrapper plus its `.7z` payload — copied to every target host. Budget the
time accordingly on a full lab.

The install is skipped when the requested locale is already registered, so the
task is safe to re-run. Presence is decided from the registry only: if
`acadlt.exe` is on disk but the product is not registered, the install runs
again to repair it.

The ODIS SFX spawns `db-bootstrap.exe`, which writes the ODIS metadata the
uninstaller later needs but can block for hours on network calls. The role
therefore launches the SFX without waiting, polls until **both** the registry
entry and `bundleManifest.xml` are present (up to 1800 s), then stops
`db-bootstrap.exe` so the SFX can exit cleanly. After the install it reboots
only if Windows reports a pending restart, then registers the educational
licence through `AdskLicensingInstHelper` running as SYSTEM.

---

## Uninstall

`off` detects the installed locale with a wildcard, aligns the uninstall to it,
and runs the ODIS uninstaller against the bundle manifest. Exit code `1604`
(suspended, reboot needed) counts as success.

Adding `full` — `autocadlt2026-off-full` — also removes the shared Autodesk
stack: Autodesk Access, Genuine Service, Identity Manager, "Open in Desktop",
"Save to Web & Mobile", and finally `C:\Program Files\Autodesk` and
`C:\ProgramData\Autodesk` wholesale. **Use it only when no other Autodesk
product remains on the host** — it will take the others down with it.

---

## Notes

- Autodesk releases install side by side. Running this role on a host that
  already has an older release leaves both installed; use
  [`autocadlt2023`](autocadlt2023.md) first to get a replacement rather than an
  addition.
- The installers come from `edutrial.autodesk.com` with pinned sha256 checksums;
  a licence entitlement is still required for lawful use.
- The role depends on `ansible_remote_tmp` nowhere: the installer is read from
  `win_workman_remote_tmp`, where `pkg_utils/win_copy` puts it.

---

## Schema details

Software name: `Autocad LT 2026 EN` / `Autocad LT 2026 IT`
Registry `searchName`: `AutoCAD LT 2026 - English` / `AutoCAD LT 2026 - Italiano (Italian)`
Installer: `ACDLT_2026_<locale>_win_db_001_002.exe` + `..._002_002.7z`
Homepage: https://www.autodesk.com/products/autocad-lt/
