# Role: firefox

> **Work in progress** — preliminary draft.

Manages Mozilla Firefox. Supports locale-aware installation, private-browsing
and kiosk-mode shortcuts, privacy policy enforcement, and user-data removal.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Firefox |
| `off` | Uninstall Firefox |
| `download` | Download installer to storage |
| `info` | Report installation state |
| `privacy-on` | Apply privacy policy (disables telemetry, crash reports, etc.) |
| `privacy-off` | Remove privacy policy |
| `rm-profile` | Force-close Firefox and delete all user profile folders |

---

## Locale detection

Before running any action, the role queries the target host for its system
locale (`Get-WinSystemLocale`, `Get-SystemPreferredUILanguage`, etc.) and
overrides `win_workman_default_lang` with the detected value if one is found.
This selects the correct language-specific installer from the schema.

Set `win_workman_default_lang` explicitly in `group_vars` to override detection.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_firefox_shortcuts` | `false` | Create desktop shortcuts for Firefox |
| `win_workman_firefox_shortcut_url` | `""` | URL appended to the desktop shortcut |
| `win_workman_firefox_private` | `false` | Add `-private` flag to the shortcut (always opens in Private Browsing) |
| `win_workman_firefox_kiosk` | `false` | Add `-kiosk` flag to the shortcut |
| `win_workman_default_lang` | `"en_US"` | Locale used to select the installer; auto-detected from host if not set |

---

## Notes

- `rm_data` removes both `%LOCALAPPDATA%\Mozilla\Firefox` and
  `%APPDATA%\Mozilla\Firefox` for every local user profile.
- Unlike Chrome, Firefox does not use the Enterprise MSI by default; the
  installer URL in `vars/main.yaml` is locale-dependent.
