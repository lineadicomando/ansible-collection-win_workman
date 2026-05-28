# Role: wallpaper

> **Work in progress** — preliminary draft.

Manages the desktop wallpaper across all local user profiles, including offline
(not-yet-logged-in) profiles via registry hive mounting. Also controls whether
users can change the wallpaper (lock/unlock).

---

## Actions

| Action | Description |
|---|---|
| `on` | Set wallpaper for all profiles **and** lock it (combines `set` + `lock`) |
| `off` | Reset wallpaper to the Windows default for all profiles and unlock it (combines `reset` + `unlock`) |
| `set` | Copy and apply wallpaper to all profiles without locking |
| `reset` | Restore the default Windows wallpaper for all profiles |
| `lock` | Prevent users from changing the wallpaper via Group Policy |
| `unlock` | Remove the wallpaper change restriction |

All actions that modify profile registry keys first force-log off interactive
sessions via `pkg_utils/logoff`.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_wallpaper_source` | `{{ role_path }}/files/default_wallpaper` | Controller-side source file or directory |
| `win_workman_wallpaper_dir` | `C:\ProgramData\Wallpaper` | Target directory on Windows host |
| `win_workman_wallpaper_path` | `{{ win_workman_wallpaper_dir }}\wallpaper.png` | Full destination path on Windows host |
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
currently loaded (offline users). Hives are mounted and unmounted as needed.

Set `win_workman_wallpaper_profiles_include_default: false` to skip the
`%SystemDrive%\Users\Default` profile.

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
