# brave — Brave Browser

Brave Browser, 64-bit system-level install (`registry` provider) from the vendor's
`latest/brave_installer-x64.exe`.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_brave_shortcuts` | `false` | Create the Public Desktop and Start Menu shortcuts |
| `win_workman_brave_shortcut_url` | `""` | URL appended to the shortcut arguments |
| `win_workman_brave_shortcut_no_first_run` | `true` | Add `--disable-search-engine-choice-screen --no-default-browser-check --no-first-run` to the shortcut |

## Notes

- No `version` and no checksum: with no version `on` treats an installed Brave as
  older and runs the installer again at every run. `download` keeps the file already
  in storage, so delete it there to fetch a newer release.
- `searchName` is `*Brave*`, wide enough to match any program with Brave in its name.
- Nothing closes a running Brave before uninstall; `off` deletes
  `BraveSoftware\Brave-Browser` afterwards (`cleanup_paths`).
