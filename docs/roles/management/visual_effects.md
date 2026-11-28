# visual_effects — Visual effects presets

Sets the Visual Effects of System Properties > Advanced > Performance in every local
profile, including users who never logged on and the Default profile, by writing each
profile hive. Takes effect at the next logon, no reboot. The point is speed on old
PCs with integrated graphics and little RAM: shadows, fades and animations go through
the Desktop Window Manager, which competes with applications for GPU and memory.

## Actions

| Action | Does |
|---|---|
| `set[-<preset>]` (default) | Apply the preset (argument, else `win_workman_visual_effects_preset`) to every profile; an unknown preset fails before the registry is touched |
| `reset` | Same as `set-default` |
| `on` | Alias of `set` (no argument: uses the variable) |
| `off` | Alias of `reset` |
| `info` | Report the preset each profile matches; changes nothing, no logoff |

`set` and `reset` force a logoff first (`pkg_utils` `logoff`); profiles still loaded
are skipped with a warning. `info` reads loaded hives in place, loads offline ones
with `reg load` (`unavailable` if it cannot), and reports a preset name, `custom`
(matches none, e.g. boxes changed by hand) or `unset` (neither `UserPreferencesMask`
nor `VisualFXSetting` exists: never customised, Windows writes its defaults at first
logon). A missing `VisualFXSetting` counts as `0`, so an untouched profile reports
`default`.

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
| Radio button (`VisualFXSetting`) | Custom (3) | Custom (3) | Best appearance (1) | Let Windows choose (0) |

- `minimal`: Windows' own "Adjust for best performance" also turns font smoothing
  off, which makes text visibly worse for no measurable gain, so it is not offered.
- `balanced`: no motion, no shadows, but keeps the cheap effects that help everyday
  use; window contents while dragging stays because an outline alone confuses users.
- `full` is "Adjust for best appearance"; `default` is a fresh Windows 11 profile.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_visual_effects_preset` | `minimal` | Preset when the task string carries none: `minimal`, `balanced`, `full`, `default` |
| `win_workman_visual_effects_profiles_include_default` | `true` | Include the Default profile |

## Notes

- Values written (data per preset in `vars/main.yaml`): `Control Panel\Desktop`
  `UserPreferencesMask`, `DragFullWindows`, `FontSmoothing`, `WindowMetrics\MinAnimate`;
  `Explorer\Advanced` `TaskbarAnimations`, `ListviewAlphaSelect`, `ListviewShadow`,
  `IconsOnly`; `DWM` `EnableAeroPeek`, `AlwaysHibernateThumbnails`;
  `Explorer\VisualEffects\VisualFXSetting`.
- Every `UserPreferencesMask` is the one Windows writes itself, never computed bit by
  bit: `minimal`, `balanced`, `full` read back after setting the same boxes in the
  dialog, `default` from a fresh profile. `full` and `default` differ although every
  box in the mask is ticked in both: the second byte carries bits the dialog does not
  show.
- `reset` writes every value, not just `VisualFXSetting=0`: Windows turns the radio
  button into settings only when the dialog is confirmed, never at logon.
- Transparency (Settings > Personalisation > Colours, `EnableTransparency`) is not
  part of the dialog and is left alone.
- There is no policy for these boxes: users can change them; re-running the role puts
  the preset back, `info` shows who changed them (`custom`).
- An open session is not updated: that needs `SystemParametersInfo` from inside the
  user's session, which SSH cannot reach. Hence the logoff.
