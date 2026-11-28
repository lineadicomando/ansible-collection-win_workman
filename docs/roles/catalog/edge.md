# edge — Microsoft Edge

Microsoft Edge Enterprise MSI (`registry` provider), pinned version and checksum,
64-bit by default; the task argument `32bit` selects the x86 MSI. The role installs
and upgrades Edge but never removes it. Adds a lockdown policy set and per-host
profile removal.

## Actions

| Action | Does |
|---|---|
| `off` | Deliberate no-op (message only at `-v`): Windows components depend on Edge, and removing it, even with the enterprise uninstall string, left a lab machine unstable |
| `privacy-on` | Writes policies under `HKLM\SOFTWARE\Policies\Microsoft\Edge`: no sign-in, sync, first-run and import wizard, history saving, password manager, autofill, metrics; browsing data cleared on exit; extension blocklist `*` plus allow/force lists |
| `privacy-off` | Removes those values and the whole `Policies\Microsoft\Edge` key |
| `rm-profile` | Kills `msedge.exe`, deletes `AppData\Local\Microsoft\Edge` of every local profile, removes every desktop shortcut to `msedge.exe` |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_edge_shortcuts` | `false` | Create the Public Desktop and Start Menu shortcuts |
| `win_workman_edge_shortcut_url` | `""` | URL appended to the shortcut arguments |
| `win_workman_edge_shortcut_no_first_run` | `true` | Add `--disable-search-engine-choice-screen --no-default-browser-check --no-first-run` to the shortcut |
| `win_workman_edge_extension_allowlist` | `[]` | With `privacy-on`, IDs users may still install despite the blocklist (`ExtensionInstallAllowlist`) |
| `win_workman_edge_extension_forcelist` | `[]` | With `privacy-on`, extensions installed for every user, not removable (`ExtensionInstallForcelist`); entry is `<id>;<update URL>` |

## Notes

- Edge looks a bare extension ID up in the Edge Add-ons store. A Chrome Web Store
  extension in the forcelist needs the Web Store update URL after its ID:
  `ghbmnnjooekpmoecnnnilnnbdlolhkhi;https://clients2.google.com/service/update2/crx`
  (Google Docs Offline). In the allowlist, the same extension also needs the user to
  turn on "Allow extensions from other stores" in `edge://extensions`.
- Unlike chrome, the blocklist is always set with `privacy-on` and cookies are always
  cleared on exit; there is no variable to opt out.
- `msedge.exe` is force-killed before install.
- Edge installs under `%ProgramFiles(x86)%` on 64-bit Windows whatever the MSI
  architecture; the shortcut paths follow that (mapping it like chrome pointed them at
  a path that does not exist).
- Edge updates itself past the pinned MSI: `version_file` is `msedge.exe`, so `on`
  skips an older MSI instead of reinstalling it. See
  [pkg_utils](../core/pkg_utils.md#programs-that-update-themselves-version_file).
