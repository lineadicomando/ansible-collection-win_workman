# wallpaper — Desktop wallpaper

Sets, resets and locks the desktop wallpaper in every local profile, including users
who never logged on and the Default profile, by writing each profile hive.

## Actions

| Action | Does |
|---|---|
| `on` (default) | `set` + `lock`: deploy the image, apply it, lock every profile on it |
| `off` | `reset` + `unlock`; the deployed image stays in `win_workman_wallpaper_dir` |
| `set` | Copy the image to `win_workman_wallpaper_path`, write it to every profile (`BackgroundType=0`), clear the wallpaper cache; a profile already locked is relocked on it |
| `reset` | Write `win_workman_wallpaper_default_*` to every profile, clear the cache; a locked profile is relocked on the default |
| `lock` | Lock every profile on the wallpaper it has now (below); needs no prior `set` |
| `unlock` | Remove the three lock values; the profile shows its pre-lock wallpaper again; copies in the lock dir stay |
| `clear_history` | Delete `BackgroundHistoryPath0..4` (the recent images of the Background page) |

Every action first forces a logoff (`pkg_utils` `logoff`): a hive can only be written
while not in use. With autologon the host then sits at the logon screen until the next
restart. Profiles still loaded are skipped with a warning; a hive loaded without an
interactive session (the SSH user) is written in place under `HKU:\<SID>`. `on`/`off`
log off and collect the profiles once and pass `win_workman_wallpaper_profiles_ready`
as an include var (not a fact, which would outlive the action and go stale after a
restart).

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_wallpaper_source` | `{{ role_path }}/files/default_wallpaper.png` | Image on the controller (a file, not a directory) |
| `win_workman_wallpaper_dir` | `C:\ProgramData\Wallpaper` | Target directory on the host |
| `win_workman_wallpaper_path` | `{{ win_workman_wallpaper_dir }}\wallpaper.png` | Destination file, written to the registry |
| `win_workman_wallpaper_lock_dir` | `{{ win_workman_wallpaper_dir }}\locked` | Where `lock` copies a picture that lives inside a profile |
| `win_workman_wallpaper_profiles_include_default` | `true` | Include the Default profile |
| `win_workman_wallpaper_set_style` | `"10"` | Control Panel style: `0` center, `2` stretch, `6` fit, `10` fill, `22` span |
| `win_workman_wallpaper_set_tile` | `"0"` | Tiling `0`/`1` |
| `win_workman_wallpaper_default_path` | `<SystemRoot>\Web\Wallpaper\Windows\img0.jpg` | Wallpaper of `reset` (`ansible_env.SystemRoot`, else `C:\Windows`) |
| `win_workman_wallpaper_default_style` | `"10"` | Style of `reset` |
| `win_workman_wallpaper_default_tile` | `"0"` | Tiling of `reset` |

## How the lock works

`lock` reads each profile's `Control Panel\Desktop\Wallpaper` and writes two per-user
policies under `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies`:

| Value | Effect |
|---|---|
| `ActiveDesktop\NoChangingWallPaper = 1` | Hides the Background page and "Set as desktop background" |
| `System\Wallpaper`, `System\WallpaperStyle` | Desktop Wallpaper policy: forces the picture at every logon, even after a theme change |

| Current wallpaper | Locked on |
|---|---|
| A file outside the profiles directory (`C:\Windows\Web`, the role's file) | That file, in place |
| A file inside the user's profile | A copy in `win_workman_wallpaper_lock_dir`, which the user cannot edit or delete |
| A file that no longer exists | The `TranscodedWallpaper` copy Windows displays, copied as above |
| Solid colour, slideshow, Spotlight, no file | `win_workman_wallpaper_default_path`, reported as a fallback |

- A profile already locked keeps its locked picture on a second `lock`: a program the
  user runs can still change `Control Panel\Desktop` for the session through
  `SystemParametersInfo`, which the policy does not block (it restores the locked
  picture at the next logon), and `lock` must not adopt that choice.
- `on`, `set` and `reset` lock with "follow desktop": the value they just wrote wins
  over the old locked picture. `set`/`reset` touch only profiles already locked;
  `off` skips the relock since `unlock` follows.
- The policy's `WallpaperStyle` is the Desktop.admx enum (`0` center, `1` tile,
  `2` stretch, `3` fit, `4` fill, `5` span), not Control Panel's: style and tiling are
  translated.
- A profile that cannot be locked is reported and fails the task after the others
  are done.

## Notes

- `set` and `reset` delete `Themes\TranscodedWallpaper` and `Themes\CachedFiles` so the
  Background page previews the deployed file, not the last picture the user picked.
