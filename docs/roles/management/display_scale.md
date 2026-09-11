# Role: display_scale

> **Work in progress** — preliminary draft.

Sets the Windows display scaling percentage (**Settings > System > Display >
Scale and layout**) across all local user profiles, including offline
(not-yet-logged-in) profiles via registry hive mounting.

---

## Actions

| Action | Description |
|---|---|
| `set` | Apply a scale percentage to all profiles *(default action)* |
| `reset` | Restore the scale recommended by the display driver |
| `on` | Alias for `set` — applies `win_workman_display_scale_percent` |
| `off` | Alias for `reset` |
| `info` | Report the scale configured in every profile, without changing anything |

The percentage is passed as the task argument: `display_scale-set-150`. When no
argument is given, `win_workman_display_scale_percent` is used.

Supported percentages — the same ones offered by the Settings panel:

| % | `LogPixels` | % | `LogPixels` |
|---|---|---|---|
| 100 | 96 | 225 | 216 |
| 125 | 120 | 250 | 240 |
| 150 | 144 | 300 | 288 |
| 175 | 168 | 350 | 336 |
| 200 | 192 | 400 | 384 |

Any other value fails the play with an explicit message before touching the
registry.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_display_scale_percent` | `100` | Percentage applied when the task string carries no argument |
| `win_workman_display_scale_profiles_include_default` | `true` | Also apply to the Default profile (used for new users) |
| `win_workman_display_scale_clear_per_monitor` | `true` | Remove per-monitor overrides so the global value takes effect |

---

## Registry values

The scale is a **per-user** setting, written into each profile hive under
`Control Panel\Desktop`:

| Value | Type | Meaning |
|---|---|---|
| `LogPixels` | dword | DPI: `96` = 100%, `144` = 150%, … |
| `Win8DpiScaling` | dword | `1` = use `LogPixels`, `0` = use the driver-recommended DPI |
| `PerMonitorSettings\<monitor>\DpiValue` | dword | Per-monitor override, **relative** to the recommended step |

Windows exposes two mutually exclusive scaling mechanisms:

- the **Scale dropdown** in Settings writes `PerMonitorSettings\<monitor>\DpiValue`,
  an offset *relative* to whatever the driver recommends for that specific panel;
- **custom scaling** writes `LogPixels` + `Win8DpiScaling=1`, an absolute value
  that applies to every display and takes precedence over everything else.

This role writes the second one, because it is the only mechanism that can be
set deterministically with no interactive session: `DpiValue` would first
require reading the recommended step of the attached panel, which is only
available from a logged-on desktop — whereas the role works on offline hives, so
that never-used profiles and `Default` are covered too.

### What this looks like in Settings

Once the role has run, the Display settings page shows the notice *"A custom
scale factor is set"* and the **Scale dropdown is greyed out**: that is Windows'
own behaviour whenever `Win8DpiScaling=1`, not a side effect of how the role
writes the value. The percentage still visible in the disabled dropdown is the
panel's recommended step, not the applied one — the applied value is the one
`display_scale-info` reports.

A practical consequence worth knowing: while custom scaling is active, users
**cannot change the scale** from Settings. On classroom workstations this is
effectively the `lock` behaviour that Windows offers no policy for. The
*"Turn off custom scaling and sign out"* link in that notice does exactly what
`display_scale-reset` does.

`PerMonitorSettings` is deleted by default so that no stale per-monitor override
survives the change. Set `win_workman_display_scale_clear_per_monitor: false` to
leave existing per-monitor choices in place — they stay dormant while custom
scaling is on, and come back into effect after a `reset`.

---

## How profile targeting works

The role collects all local user profiles on the host (via `pkg_utils/profiles`)
and applies registry changes to each one — including profiles whose hive is not
currently loaded. Profiles belonging to users with an active session are
skipped, so `set` and `reset` force a logoff first (via `pkg_utils/logoff`).

The new scale takes effect at the **next logon**. No reboot is required.

The `info` action does not force a logoff: it reads the currently-loaded hives
in place and mounts the offline ones read-only, reporting `unavailable` for any
hive it cannot open.

---

## Usage

```yaml
# Classroom workstations on 24" 1080p panels: 125%
win_workman_tasks:
  - display_scale-set-125

# Lab default declared once, applied on every run
win_workman_display_scale_percent: 150
win_workman_tasks:
  - display_scale

# Back to what the driver recommends
win_workman_tasks:
  - display_scale-reset

# Check before changing anything
win_workman_tasks:
  - display_scale-info
```

---

## Notes

- The role offers no `lock`/`unlock` pair — unlike `wallpaper` — because none is
  needed: custom scaling already disables the Scale dropdown, and `reset` is the
  way back. Windows has no policy for this (`NoDispCPL` hides the whole Display
  page, which is a blunter tool).
- On multi-monitor hosts, Windows may still recompute per-monitor scaling when a
  display is attached or the layout changes. Re-run the role after hardware
  changes rather than assuming the value sticks.
