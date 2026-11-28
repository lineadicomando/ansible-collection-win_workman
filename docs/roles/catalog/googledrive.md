# googledrive — Google Drive for desktop

Installs Google Drive for desktop (`GoogleDriveSetup.exe --silent --skip_launch_new`,
`registry` provider), with a public desktop shortcut and auto-start at logon.

## Actions

| Action | Does |
|---|---|
| `on[-nodep]` | Installs [chrome](chrome.md) first, then Drive; sets `HKLM\Software\Google\DriveFS\AutoStartOnLogin` = 1; `nodep` skips Chrome |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_googledrive_desktop_shortcut` | `true` | Create `%Public%\Desktop\Google Drive.lnk` (to `launch.bat`) |
| `win_workman_googledrive_auto_start` | `true` | On `on`, write `AutoStartOnLogin` = 1 |

## Notes

- No version is pinned and the URL always serves the current release, without a
  checksum. With no target version every `on` counts as an upgrade and runs the
  installer again; it then returns 1638 (another version already installed), which
  the schema accepts as success. Drive updates itself.
- The stored installer is never refreshed: `get_url` without a checksum skips a file
  already in `win_workman_storage_path`. Delete it there to deploy a newer build.
- `off` does not remove the `AutoStartOnLogin` value.
- The defaults file is `defaults/maint.yaml`, which Ansible never loads; the
  `default(true)` in the templates gives the same values, and inventory overrides
  work.
