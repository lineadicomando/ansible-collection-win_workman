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
| `set` | Copy the image to the host and apply it to all profiles without locking; clears the per-profile wallpaper cache; moves an existing lock onto the new image |
| `reset` | Restore the default Windows wallpaper for all profiles and clear the per-profile wallpaper cache; moves an existing lock onto the default wallpaper |
| `lock` | Prevent users from changing the wallpaper, locking each profile on the wallpaper it has now (see below) |
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
| `win_workman_wallpaper_lock_dir` | `{{ win_workman_wallpaper_dir }}\locked` | Where `lock` copies a picture that lives inside a user profile |
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

`lock` locks every profile on the wallpaper it has **now**: it does not need
`set` first, and it does not impose the role's image. For each profile it reads
`Control Panel\Desktop\Wallpaper` from the profile hive and writes two per-user
policies:

| Key (under `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies`) | Effect |
|---|---|
| `ActiveDesktop\NoChangingWallPaper = 1` | Hides the Background page in Settings and the "Set as desktop background" menu |
| `System\Wallpaper`, `System\WallpaperStyle` | Desktop Wallpaper policy: forces the picture at every logon, even after a theme change |

The picture the policy points at is chosen per profile:

| Current wallpaper | Locked on |
|---|---|
| A file outside the profiles directory (`C:\Windows\Web`, the role's own file) | That file, in place |
| A file inside the user's profile (Pictures, Downloads…) | A copy in `win_workman_wallpaper_lock_dir`, which the user cannot edit or delete |
| A file that no longer exists | The `TranscodedWallpaper` copy Windows is displaying, copied as above |
| Solid colour, slideshow, Spotlight, or no file at all | `win_workman_wallpaper_default_path` (reported as a fallback) |

A profile that is already locked keeps its locked picture when `lock` runs
again. A program the user starts can still change `Control Panel\Desktop` for
the current session through `SystemParametersInfo`, which the policy does not
block: the policy puts the locked picture back at the next logon, and a second
`lock` must not adopt the user's choice.

The policy's `WallpaperStyle` is a different enum from Control Panel's
(Desktop.admx: `0` center, `1` tile, `2` stretch, `3` fit, `4` fill, `5` span),
so the profile's style and tiling are translated, not copied.

`set` and `reset` keep a lock in place: a profile that already carries the
policy is locked again on the wallpaper they just wrote, otherwise the policy
would keep pointing at the old picture. `on` locks on the file `set` just
wrote, whatever was locked before. `off` skips the relock, since `unlock`
follows.

`unlock` removes the three values and leaves `Control Panel\Desktop` alone, so
the profile goes back to the wallpaper it had before the lock. The copies in
`win_workman_wallpaper_lock_dir` stay on disk.

---

## Usage

```yaml
# Freeze whatever wallpaper each user has now
win_workman_tasks:
  - wallpaper-lock

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
