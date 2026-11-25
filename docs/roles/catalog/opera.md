# Role: opera

> **Work in progress** — preliminary draft.

Manages Opera Browser, a Chromium-based web browser with built-in VPN and
battery saver. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Opera |
| `off` | Uninstall Opera |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Opera is installed |

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_opera_version` | `"140.0.6074.36"` | Installer version; update when upgrading |
| `win_workman_opera_shortcuts` | `false` | Create desktop and Start Menu shortcuts |
| `win_workman_opera_shortcut_url` | `""` | URL appended to shortcut arguments |
| `win_workman_opera_shortcut_no_first_run` | `true` | Add `--no-first-run --no-default-browser-check --disable-search-engine-choice-screen` to shortcut |

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_opera_shortcuts: true
win_workman_opera_shortcut_no_first_run: true

win_workman_tasks:
  - opera
  - opera-off
```

---

## Schema details

Software name: `Opera Browser`  
Provider: `registry`  
Installer: `Opera_<version>_Setup_x64.exe` (64-bit only)  
Homepage: https://www.opera.com/

---

## Notes

- Opera is installed at system level (`/allusers=1`) under `%ProgramFiles%\Opera`.
- Any running `opera.exe` process is force-killed before uninstall.
- After uninstall, `%ProgramFiles%\Opera` is removed via `cleanup_paths`.
- `win_workman_opera_version` must be updated manually when a new release is
  available; update both the variable and verify the download URL is reachable.
- The installer sha256 is pinned in `files[].checksum` next to the version:
  a version bump needs a new checksum too, or `download` fails.

### Uninstall

The uninstall entry registers `opera.exe /uninstall`, which exits at once with rc 0 and
removes nothing, whatever the arguments. `off` therefore runs the real uninstaller first,
`installer.exe --uninstall --runimmediately --deleteuserprofile=0` from the versioned
subfolder that `installation_status.json` names, waits for the entry to go and lets
`cleanup_paths` take the few files left in `%ProgramFiles%\Opera`. The scheduled
autoupdate tasks go with it. The script waits on the installer process only: with
`Start-Process -Wait` it waited for a process the uninstaller leaves running and never
returned.

The checksum is pinned next to `win_workman_opera_version` and has to be bumped with it;
Opera publishes it at the installer URL plus `.sha256sum`.
