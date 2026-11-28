# opera — Opera Browser

Opera, 64-bit system-level install (`registry` provider, `/allusers=1`) under
`%ProgramFiles%\Opera`, version and sha256 pinned in `vars/main.yaml`.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_opera_shortcuts` | `false` | Create the Public Desktop and Start Menu shortcuts (`Browser Opera.lnk`) |
| `win_workman_opera_shortcut_url` | `""` | URL appended to the shortcut arguments |
| `win_workman_opera_shortcut_no_first_run` | `true` | Add `--disable-search-engine-choice-screen --no-default-browser-check --no-first-run` to the shortcut |

## Notes

- Uninstall: the registered `UninstallString`, `opera.exe /uninstall`, exits at once
  with rc 0 and removes nothing, whatever the arguments. `off` therefore first kills
  `opera` and `opera_autoupdate`, then runs the real uninstaller,
  `installer.exe --uninstall --runimmediately --deleteuserprofile=0` from the
  versioned subfolder that `installation_status.json` names (falling back to the
  highest subfolder holding an `installer.exe`), waits up to 60 s for the
  `Opera Stable*` entry to go, and fails if it stays or rc is not 0. pkg_utils' own
  uninstall step then finds nothing; `cleanup_paths` takes the few files left. The
  scheduled autoupdate tasks go with it.
- The script waits on the installer process only (`WaitForExit`, 120 s): with
  `Start-Process -Wait` it waited for a process the uninstaller leaves running and
  never returned.
- Bump the checksum with `win_workman_opera_version`: Opera publishes it at the
  installer URL plus `.sha256sum`.
