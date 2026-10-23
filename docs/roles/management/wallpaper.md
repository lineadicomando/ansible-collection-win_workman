# Role: wallpaper

Manages the desktop wallpaper across all local user profiles, including offline
(not-yet-logged-in) profiles via registry hive mounting. Also controls whether
users can change the wallpaper (lock/unlock).

---

## Actions

| Action | Description |
|---|---|
| `on` *(default)* | Set the wallpaper for all profiles **and** lock it (`set` + `lock`) |
| `off` | Restore the Windows default wallpaper for all profiles and unlock it (`reset` + `unlock`) |
| `set` | Copy the image to the host and apply it to all profiles without locking; clears the per-profile wallpaper cache |
| `reset` | Restore the default Windows wallpaper for all profiles and clear the per-profile wallpaper cache |
| `lock` | Prevent users from changing the wallpaper (see below); fails if the image is not deployed |
| `unlock` | Remove the wallpaper lock |
| `clear_history` | Clear the "Recent images" list of the Background settings page in all profiles |

Every action first force-logs off the interactive sessions via
`pkg_utils/logoff`, because a profile hive can only be written while it is not
in use. On hosts with autologon the machine then sits at the logon screen until
the next restart; the new wallpaper shows at the next logon.

`off` restores the default wallpaper but leaves the deployed image under
`win_workman_wallpaper_dir`.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_wallpaper_source` | `{{ role_path }}/files/default_wallpaper.png` | Image file on the controller (a file, not a directory) |
| `win_workman_wallpaper_dir` | `C:\ProgramData\Wallpaper` | Target directory on the Windows host |
| `win_workman_wallpaper_path` | `{{ win_workman_wallpaper_dir }}\wallpaper.png` | Full destination path, written to the registry |
| `win_workman_wallpaper_profiles_include_default` | `true` | Also apply to the Default profile (used for new users) |
| `win_workman_wallpaper_set_style` | `"10"` | Wallpaper style: `0`=centered, `2`=stretched, `6`=fit, `10`=fill, `22`=span |
| `win_workman_wallpaper_set_tile` | `"0"` | Tiling: `0`=disabled, `1`=enabled |
| `win_workman_wallpaper_default_path` | `%SystemRoot%\Web\Wallpaper\Windows\img0.jpg` | Wallpaper path used by the `reset` action |
| `win_workman_wallpaper_default_style` | `"10"` | Style applied by the `reset` action |
| `win_workman_wallpaper_default_tile` | `"0"` | Tile setting applied by the `reset` action |

---

## How profile targeting works

The role collects all local user profiles on the host (via `pkg_utils/profiles`)
and applies registry changes to each one — including profiles whose hive is not
currently loaded (offline users). Hives are mounted and unmounted as needed; a
hive that is already loaded without an interactive session (the SSH user, for
instance) is written in place under `HKU:\<SID>`.

Set `win_workman_wallpaper_profiles_include_default: false` to skip the
`%SystemDrive%\Users\Default` profile.

`on` and `off` log off and collect the profiles once, then run their two
actions with `win_workman_wallpaper_profiles_ready: true` as an include var so
the steps are not repeated. Standalone actions always log off and collect afresh.

---

## How the lock works

`lock` writes two per-user policies into every profile:

| Key (under `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies`) | Effect |
|---|---|
| `ActiveDesktop\NoChangingWallPaper = 1` | Hides the Background page in Settings and the "Set as desktop background" menu |
| `System\Wallpaper`, `System\WallpaperStyle` | Desktop Wallpaper policy: forces `win_workman_wallpaper_path` at every logon, even after a theme change |

Because the second policy points every logon at the deployed file, `lock`
refuses to run when that file is missing on the host: run `set` (or `on`)
first. `unlock` removes all three values.

---

## Usage

```yaml
# Set a custom wallpaper and prevent users from changing it
win_workman_tasks:
  - wallpaper-on
win_workman_wallpaper_source: "files/company_wallpaper.png"

# Only apply wallpaper without locking
win_workman_tasks:
  - wallpaper-set

# Restore Windows default and allow customisation
win_workman_tasks:
  - wallpaper-off
```
