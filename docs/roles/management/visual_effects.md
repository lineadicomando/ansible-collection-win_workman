# Role: visual_effects

Sets the Windows visual effects — **System Properties > Advanced > Performance >
Settings > Visual Effects** — across all local user profiles, including offline
(not-yet-logged-in) profiles and the Default profile used for new users.

The point is speed on old hardware: on an older PC with integrated graphics
and little RAM, turning the effects off gives a clearly more responsive
desktop. Shadows, fades and animations all go through the Desktop
Window Manager, which competes with applications for the same GPU and memory.

---

## Actions

| Action | Description |
|---|---|
| `set` | Apply a preset to every profile *(default action)* |
| `reset` | Restore the effects of a fresh Windows 11 profile (same as `set-default`) |
| `on` | Alias for `set` — applies `win_workman_visual_effects_preset` |
| `off` | Alias for `reset` |
| `info` | Report the preset of every profile, without changing anything |

The preset is passed as the task argument: `visual_effects-set-balanced`. When
no argument is given, `win_workman_visual_effects_preset` is used. An unknown
preset fails the play before touching the registry.

## Presets

| Effect (dialog entry) | `minimal` | `balanced` | `full` | `default` |
|---|---|---|---|---|
| Animate controls and elements inside windows | off | off | on | on |
| Animate windows when minimising and maximising | off | off | on | on |
| Animations in the taskbar | off | off | on | on |
| Enable Peek | off | off | on | on |
| Fade or slide menus into view | off | off | on | on |
| Fade or slide ToolTips into view | off | off | on | on |
| Fade out menu items after clicking | off | off | on | on |
| Save taskbar thumbnail previews | off | off | on | off |
| Show shadows under mouse pointer | off | off | on | on |
| Show shadows under windows | off | off | on | on |
| Slide open combo boxes | off | off | on | on |
| Smooth-scroll list boxes | off | off | on | on |
| Show thumbnails instead of icons | off | **on** | on | on |
| Show window contents while dragging | off | **on** | on | on |
| Show translucent selection rectangle | off | **on** | on | on |
| Use drop shadows for icon labels on the desktop | off | **on** | on | on |
| Smooth edges of screen fonts | **on** | **on** | on | on |
| Radio button shown in the dialog | Custom | Custom | Best appearance | Let Windows choose |

- `minimal` — the lightest setting that keeps text readable. Windows' own
  "Adjust for best performance" also turns font smoothing off, which makes text
  visibly worse for no measurable gain, so the role does not offer it.
- `balanced` — no motion and no shadows, but keeps the effects that cost little
  and help everyday use: thumbnails in Explorer, window contents while
  dragging (an outline alone confuses users who are not used to it), the
  selection rectangle and readable icon labels on any wallpaper.
- `full` — "Adjust for best appearance".
- `default` — what a fresh Windows 11 profile has.

`info` reports the name of the preset a profile matches, or:

| Value | Meaning |
|---|---|
| `custom` | matches no preset, e.g. boxes changed by hand |
| `unset` | neither `UserPreferencesMask` nor `VisualFXSetting` exists: the profile was never customised, Windows writes its defaults at first logon |

A missing `VisualFXSetting` counts as `0` (let Windows choose), so an untouched
profile reports `default`.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_visual_effects_preset` | `minimal` | Preset applied when the task string carries no argument |
| `win_workman_visual_effects_profiles_include_default` | `true` | Also apply to the Default profile (used for new users) |

---

## Registry values

All per-user, written into each profile hive. `...` is
`Software\Microsoft\Windows\CurrentVersion`.

| Key (under `HKCU`) | Value | Type | `minimal` | `balanced` | `full` | `default` |
|---|---|---|---|---|---|---|
| `...\Explorer\VisualEffects` | `VisualFXSetting` | dword | `3` | `3` | `1` | `0` |
| `Control Panel\Desktop` | `UserPreferencesMask` | binary | `90 00 03 80 10 00 00 00` | `90 00 03 80 10 00 00 00` | `9e 2c 07 80 12 00 00 00` | `9e 1e 07 80 12 00 00 00` |
| `Control Panel\Desktop` | `DragFullWindows` | string | `0` | `1` | `1` | `1` |
| `Control Panel\Desktop` | `FontSmoothing` | string | `2` | `2` | `2` | `2` |
| `Control Panel\Desktop\WindowMetrics` | `MinAnimate` | string | `0` | `0` | `1` | `1` |
| `...\Explorer\Advanced` | `TaskbarAnimations` | dword | `0` | `0` | `1` | `1` |
| `...\Explorer\Advanced` | `ListviewAlphaSelect` | dword | `0` | `1` | `1` | `1` |
| `...\Explorer\Advanced` | `ListviewShadow` | dword | `0` | `1` | `1` | `1` |
| `...\Explorer\Advanced` | `IconsOnly` | dword | `1` | `0` | `0` | `0` |
| `Software\Microsoft\Windows\DWM` | `EnableAeroPeek` | dword | `0` | `0` | `1` | `1` |
| `Software\Microsoft\Windows\DWM` | `AlwaysHibernateThumbnails` | dword | `0` | `0` | `1` | `0` |

`UserPreferencesMask` holds most of the boxes as one bit each. Every mask in the
table is the one Windows itself writes, never computed bit by bit: `minimal`,
`balanced` and `full` were read back after setting the same boxes in the
dialog, `default` from a fresh Windows 11 profile. `full` and `default` have
different masks even though every box stored in the mask is ticked in both:
the second byte also carries bits the dialog does not show, which is why the
role copies Windows' masks instead of building them.

`reset` writes every value rather than just `VisualFXSetting=0`: Windows turns
the radio button into individual settings only when the dialog is confirmed,
never at logon, so the value alone would change nothing.

Transparency effects (**Settings > Personalisation > Colours**,
`Themes\Personalize\EnableTransparency`) are not part of this dialog and are
left alone.

---

## How profile targeting works

Same as [`display_scale`](display_scale.md): the role collects every local
profile through `pkg_utils/profiles`, skips those with an active interactive
session, and loops `win_regedit` over the rest. `set` and `reset` force a
logoff first, so in practice no profile is skipped.

The new effects take effect at the **next logon**. No reboot is required.

`info` does not force a logoff: it reads loaded hives in place and mounts the
offline ones, reporting `unavailable` for any hive it cannot open.

---

## Usage

```yaml
# Old lab PCs: lightest preset for every user, present and future
win_workman_tasks:
  - visual_effects-set-minimal

# Lab default declared once, applied on every run
win_workman_visual_effects_preset: balanced
win_workman_tasks:
  - visual_effects

# Back to the Windows defaults
win_workman_tasks:
  - visual_effects-reset

# Check before changing anything
win_workman_tasks:
  - visual_effects-info
```

---

## Notes

- Users can still change the boxes from the dialog: there is no policy for
  them. Re-running `visual_effects` puts the preset back; `info` shows who
  changed them (`custom`).
- The role does not apply the change to an open session: that would take
  `SystemParametersInfo` calls from inside the user's session, which an SSH
  connection cannot reach. Hence the logoff.
