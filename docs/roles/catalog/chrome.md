# Role: chrome

> **Work in progress** — preliminary draft.

Manages Google Chrome (Enterprise MSI). Supports 32-bit and 64-bit variants,
shortcut customisation, privacy policy enforcement, and user-data removal.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Chrome |
| `off` | Uninstall Chrome |
| `download` | Download installer to storage |
| `info` | Report installation state |
| `privacy-on` | Apply privacy Group Policy (disables telemetry, syncing, etc.) |
| `privacy-off` | Remove privacy Group Policy |
| `rm-profile` | Force-close Chrome and delete all user profile folders |

---

## Architecture selection

The installer architecture is resolved from the task string argument:

| Task string | Arch | Installer |
|---|---|---|
| `chrome-on` *(default)* | `64bit` | `googlechromestandaloneenterprise64.msi` |
| `chrome-on-32bit` | `32bit` | `googlechromestandaloneenterprise.msi` |

The token `32bit` must appear anywhere in `argv` (position 2+).

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_chrome_shortcuts` | `false` | Create desktop shortcuts for Chrome |
| `win_workman_chrome_shortcut_url` | `""` | URL appended to the desktop shortcut arguments |
| `win_workman_chrome_shortcut_no_first_run` | `true` | Adds `--disable-search-engine-choice-screen --no-default-browser-check --no-first-run` to the shortcut |
| `win_workman_chrome_block_extensions` | `true` | With `privacy-on`, block installation of all extensions (`ExtensionInstallBlocklist = *`); `false` leaves extension installs allowed and removes an existing blocklist |
| `win_workman_chrome_extension_allowlist` | `[]` | With `privacy-on` and extensions blocked, IDs of the extensions users may still install from the Web Store (`ExtensionInstallAllowlist`) |
| `win_workman_chrome_extension_forcelist` | `[]` | With `privacy-on`, extensions installed for every user, who cannot remove them (`ExtensionInstallForcelist`), blocked or not; an entry is a Web Store ID or `<id>;<update URL>` |
| `win_workman_chrome_clear_site_data_on_exit` | `true` | With `privacy-on`, clear cookies and site data when Chrome closes; `false` keeps them, cache and history are cleared either way |

The shortcut command line is assembled as:

```
[--disable-search-engine-choice-screen --no-default-browser-check --no-first-run] [win_workman_chrome_shortcut_url]
```

---

## Notes

- Before install and before uninstall, any running `chrome.exe` process is
  force-killed via a PowerShell pre-action script embedded in the schema.
- `rm_data` removes `%LOCALAPPDATA%\Google\Chrome` for every local user profile
  and cleans up profile-specific shortcuts from all desktops.
- Google Updater can move Chrome past the enterprise MSI, which Google
  may still be serving the previous release, and can leave Chrome without
  an uninstall entry. The schema sets `version_file` to `chrome.exe`, so `on`
  does nothing when that file is already at the MSI's version or newer, instead
  of failing with rc 1603 ("a newer version is already installed"). See
  [pkg_utils](../core/pkg_utils.md#programs-that-update-themselves-version_file).
- No checksum is defined for the installer: Chrome Enterprise is fetched
  directly from Google's CDN at the URL encoded in `vars/main.yaml`.
