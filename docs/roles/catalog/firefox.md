# firefox — Mozilla Firefox

Mozilla Firefox, NSIS installer (`registry` provider, `/S`, uninstall through the
helper), one installer per language. 64-bit by default; the task argument `32bit`
selects the `win32` build under `%ProgramFiles(x86)%`. Adds a lockdown policy set and
per-host profile removal.

## Actions

| Action | Does |
|---|---|
| `on-<lang>`, `download-<lang>`, ... | Any standard action takes a language token from `win_workman_firefox_allowed_langs` (`it`, `de`, `en_GB`, `pt_BR`, ...) to pick the installer: `firefox-on-de` |
| `privacy-on` | Writes policies under `HKLM\SOFTWARE\Policies\Mozilla\Firefox`: no Firefox Accounts, profile import, password saving or manager, autofill, telemetry; first-run page `about:blank`; all extensions blocked (`ExtensionSettings`); cookies, cache and history cleared on shutdown, locked |
| `privacy-off` | Removes those values and the whole `Policies\Mozilla\Firefox` key |
| `rm-profile` | Kills `firefox.exe`, deletes `AppData\Local\Mozilla\Firefox` and `AppData\Roaming\Mozilla\Firefox` of every local profile |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_firefox_shortcuts` | `false` | Create the Public Desktop and Start Menu shortcuts |
| `win_workman_firefox_shortcut_url` | `""` | URL appended to the shortcut arguments |
| `win_workman_firefox_private` | `false` | Add `--private-window` to the shortcut |
| `win_workman_firefox_kiosk` | `false` | Add `--kiosk` to the shortcut |
| `win_workman_default_lang` | `en_US` (pkg_utils) | Fallback language when neither a token nor detection gives one |

## Notes

- Language: a token in the task string wins; otherwise every action first reads the
  host locale (`pkg_utils` `detect_lang`, one PowerShell call) and `set_fact`s
  `win_workman_default_lang` when it maps to an allowed language. A `set_fact` beats
  inventory variables, so `win_workman_default_lang` in `group_vars` is ignored on
  any host whose locale is recognised; use the token or `-e` to force a language.
- Unlike chrome and edge, the privacy set has no allow/force list for extensions and
  no variable to keep cookies.
- Nothing closes Firefox before install or uninstall:
  `win_workman_firefox_before_act_ps_script` is defined in `vars/main.yaml` but the
  schema does not use it (see `docs/todo/package-workflow.md`).
- No checksum is pinned for the installer.
