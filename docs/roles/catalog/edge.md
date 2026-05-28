# Role: edge

> **Work in progress** — preliminary draft.

Manages Microsoft Edge policies and user data. Because Edge ships pre-installed
with Windows 11, this role focuses on configuration rather than installation.

---

## Actions

| Action | Description |
|---|---|
| `on` | Apply Edge configuration via `pkg_workflow` (no-op if already current) |
| `off` | **Not supported** — Edge cannot be uninstalled on Windows 11; the action is intercepted and handled gracefully |
| `privacy-on` | Apply privacy Group Policy (disables telemetry, syncing, sign-in prompts) |
| `privacy-off` | Remove privacy Group Policy |
| `rm-profile` | Force-close Edge and delete all user profile folders |
| `download` | Download the Edge installer to storage |
| `info` | Report installation state |

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_edge_shortcuts` | `false` | Create desktop shortcuts for Edge |
| `win_workman_edge_shortcut_url` | `""` | URL appended to the desktop shortcut |
| `win_workman_edge_shortcut_no_first_run` | `true` | Adds `--no-first-run` and related flags to the shortcut |

---

## Notes

- `off` is intercepted before reaching `pkg_utils` and handled with a
  graceful no-op or warning, since Edge removal is not supported by Microsoft
  on Windows 11.
- `rm_data` removes `%LOCALAPPDATA%\Microsoft\Edge` for every local user
  profile and cleans up all Edge shortcuts from user desktops.
