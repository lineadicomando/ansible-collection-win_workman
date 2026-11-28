# display_scale — Display scaling

Sets the display scale (Settings > System > Display > Scale and layout) in every
local profile, including users who never logged on and the Default profile, by
writing each profile hive. Takes effect at the next logon, no reboot.

## Actions

| Action | Does |
|---|---|
| `set[-<percent>]` (default) | Apply the percentage (argument, else `win_workman_display_scale_percent`) to every profile |
| `reset` | Delete `LogPixels`, `Win8DpiScaling` and `PerMonitorSettings`: back to the driver-recommended scale |
| `on` | Alias of `set` (no argument: uses the variable) |
| `off` | Alias of `reset` |
| `info` | Report per profile `LogPixels`, `Win8DpiScaling`, the effective scale (`<n>%` or `recommended`) and per-monitor overrides; changes nothing, no logoff |

Supported percentages, the ones Settings offers: 100, 125, 150, 175, 200, 225, 250,
300, 350, 400 (`LogPixels` = percent × 96 / 100). Any other value fails before the
registry is touched. `set` and `reset` force a logoff first (`pkg_utils` `logoff`);
profiles still loaded are skipped with a warning. `info` reads loaded hives in place,
loads offline ones with `reg load`, and reports `unavailable` for a hive it cannot
open.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_display_scale_percent` | `100` | Percentage when the task string carries none |
| `win_workman_display_scale_profiles_include_default` | `true` | Include the Default profile |
| `win_workman_display_scale_clear_per_monitor` | `true` | `set` deletes `PerMonitorSettings` so the global value applies; `false` leaves the per-monitor choices dormant, back in effect after `reset` (`reset` always deletes them) |

## Notes

- Values under `HKCU\Control Panel\Desktop`: `LogPixels` (DPI, `96` = 100%),
  `Win8DpiScaling` (`1` use `LogPixels`, `0` use the recommended DPI),
  `PerMonitorSettings\<monitor>\DpiValue` (offset relative to the panel's
  recommended step).
- Windows has two exclusive mechanisms: the Scale dropdown writes the per-monitor
  `DpiValue`; custom scaling writes `LogPixels` + `Win8DpiScaling=1`, absolute, for
  every display, winning over the rest. The role writes custom scaling because it can
  be set with no session: `DpiValue` would need the recommended step of the attached
  panel, only readable from a logged-on desktop, while the role works on offline
  hives.
- `set-100` writes `LogPixels=96` with `Win8DpiScaling=0`, which means "recommended"
  (`info` reports it so): on a panel whose recommended step is above 100% it does not
  give 100%.
- With custom scaling on, Settings shows "A custom scale factor is set" and greys out
  the Scale dropdown (Windows' own behaviour with `Win8DpiScaling=1`); the percentage
  left in it is the panel's recommended step, not the applied one. Users cannot change
  the scale: in effect the lock Windows has no policy for (`NoDispCPL` hides the whole
  Display page), so the role has no `lock`/`unlock`. "Turn off custom scaling and
  sign out" does what `reset` does.
- On multi-monitor hosts Windows may recompute per-monitor scaling when a display is
  attached or the layout changes: re-run the role after hardware changes.
