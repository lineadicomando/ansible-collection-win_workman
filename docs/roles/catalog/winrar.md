# winrar — WinRAR

WinRAR, 64-bit self-extracting installer (`registry` provider, `/S`, uninstall through the
helper), one installer per language. No licence key (`rarreg.key`) is deployed:
WinRAR runs as the evaluation version.

## Actions

| Action | Does |
|---|---|
| `on-<lang>`, `download-<lang>`, ... | Any standard action takes a WinRAR language code from `win_workman_winrar_allowed_langs` (`it`, `d`, `fr`, `sc`, `br`, ...; `en` = English) to pick the installer: `winrar-on-it` |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_winrar_shortcut_desktop` | `true` | Create the Public Desktop shortcut |
| `win_workman_winrar_shortcut_startmenu` | `true` | Create the all-users Start Menu shortcut |

## Notes

- Language: a token in the task string wins; otherwise every action, `download`
  included, first reads the host's system locale, UI languages and culture (one
  PowerShell call, so the host must be reachable) and maps them through
  `win_workman_winrar_windows_lang_map` or their two-letter base; English when nothing
  matches. `ro` and `srbcyr` are left out: their installers were still at 7.13.
- After install a script rewrites `HKLM\...\Uninstall\WinRAR archiver` with
  `DisplayName` `WinRAR` and the `ProductVersion` of `WinRAR.exe`, so detection,
  version check and `off` work with the exact `searchName`; `off` deletes that key
  (`cleanup_registry_key`).
- No checksum is pinned for the installers.
