# chrome — Google Chrome

Google Chrome Enterprise MSI (`registry` provider), 64-bit by default; the task
argument `32bit` (anywhere after the action, `chrome-on-32bit`) selects the x86 MSI
and `%ProgramFiles(x86)%`. Adds a lockdown policy set and per-host profile removal.

## Actions

| Action | Does |
|---|---|
| `privacy-on` | Writes policies under `HKLM\SOFTWARE\Policies\Google\Chrome`: no sign-in, sync, extra profiles, profile picker, guest mode, first-run and import wizard, password manager, autofill, metrics; extension blocklist `*` (see variables), allow/force lists; cookies (optional), cache and history cleared on exit |
| `privacy-off` | Removes those values and the whole `Policies\Google\Chrome` key |
| `rm-profile` | Kills `chrome.exe`, deletes `AppData\Local\Google\Chrome` of every local profile, removes desktop shortcuts to `chrome.exe` with `--profile-directory` |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_chrome_shortcuts` | `false` | Create the Public Desktop and Start Menu shortcuts |
| `win_workman_chrome_shortcut_url` | `""` | URL appended to the shortcut arguments |
| `win_workman_chrome_shortcut_no_first_run` | `true` | Add `--disable-search-engine-choice-screen --no-default-browser-check --no-first-run` to the shortcut |
| `win_workman_chrome_block_extensions` | `true` | With `privacy-on`, `ExtensionInstallBlocklist = *`; `false` removes the blocklist and the allowlist |
| `win_workman_chrome_extension_allowlist` | `[]` | With `privacy-on` and extensions blocked, Web Store IDs users may still install (`ExtensionInstallAllowlist`) |
| `win_workman_chrome_extension_forcelist` | `[]` | With `privacy-on`, extensions installed for every user, not removable, blocked or not (`ExtensionInstallForcelist`); entry is an ID or `<id>;<update URL>` |
| `win_workman_chrome_clear_site_data_on_exit` | `true` | With `privacy-on`, also clear cookies and site data on exit; `false` keeps Google sign-ins and offline data |

## Notes

- Google Docs Offline (`ghbmnnjooekpmoecnnnilnnbdlolhkhi`) is the usual list entry:
  the context-menu copy and paste in Docs and Sheets relies on it.
- List policies are written as values `1..n`; values past `n` are dropped, an empty
  list removes the subkey, so a shorter list leaves nothing stale.
- `chrome.exe` is force-killed before uninstall only (the install hook is commented
  out in `vars/main.yaml`).
- No `version` and no checksum: the MSI is Google's current one from its CDN. With no
  version `on` treats an installed Chrome as older and runs the MSI again; the
  `download` step keeps the file already in storage, so delete it there to fetch a
  newer release.
- Google Updater moves Chrome past the MSI Google serves, sometimes leaving no
  uninstall entry: `version_file` is `chrome.exe`, so `on` skips the MSI when the
  executable is the same or newer instead of failing with rc 1603 ("a newer version
  is already installed"). A Chrome found only that way cannot be removed by `off`. See
  [pkg_utils](../core/pkg_utils.md#programs-that-update-themselves-version_file).
- `off` also deletes the `Google\Chrome` program directory (`cleanup_paths`).
