# Role: wu (Windows Update)

Manages Windows Update behaviour: run pending updates, pause/resume the update schedule,
and inspect or adjust the maximum allowed pause duration.

---

## Actions

> **Default action: `run`** — bare `wu` (no action token) runs pending updates.

| Action | Description |
|---|---|
| `run` | Search, download, and install available updates; reboots if required, then reports the outcome (see below) |
| `on` | Resume Windows Update (alias for `resume`) |
| `off` | Pause Windows Update at maximum duration (alias for `pause` at max days) |
| `pause` | Pause quality and feature updates for `win_workman_wu_pause_days` days |
| `resume` | Remove the update pause (resume immediately) |
| `max_pause_days` | Read or set `FlightSettingsMaxPauseDays`; without args reports the current value, with a duration sets the cap |
| `is_paused` | Report whether updates are paused and, if so, the expiry timestamp |
| `policy_standard` | Restore standard Windows Update Group Policy (reverts Ansible-managed policy) |
| `policy_ansible_managed` | *(removed)* Raises an error; use `pause` or `off` instead |

### `run` report

win_updates reports `ok` both when nothing was found and when a reboot finished
installing updates Windows had staged on its own, so the recap alone cannot say
what happened. At the end of `run` each host prints:

```
Build: 25H2 26200.9457 -> 26200.9550
Updates: 2 found, 1 installed, 1 failed
[installed] 2026-09 Cumulative Update (KB5124010)
[failed 0x80240020] ... - WU_E_NO_INTERACTIVE_USER
Pause had expired before the run: Windows may have installed updates on its own
```

The same data is left in the `win_workman_wu_report` fact (`build_before`,
`build_after`, `found`, `installed`, `failed`, `reboot_required`, `updates`,
`filtered`). The report is printed even when the install task fails, and the host
is marked failed when single updates fail although win_updates itself succeeded.

### `max_pause_days` duration syntax

An optional unit suffix controls how the numeric argument is interpreted:

| Suffix | Meaning |
|---|---|
| *(omitted)* or `d` / `day` / `days` | days |
| `w` / `week` / `weeks` | weeks (× 7) |
| `m` / `month` / `months` | months (× 28) |

Passing `0` resets the cap to the role default (`win_workman_wu_default_max_pause_days`).

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_wu_pause_days` | `7` | Days to pause updates when using `pause` |
| `win_workman_wu_default_max_pause_days` | `35` | Maximum pause cap; used by `off` and as reset target for `max_pause_days 0` |
| `win_workman_restart` | `true` | Allow reboot when `run` requires it |
| `win_workman_wu_unpause` | `false` | Resume updates before running `run` (useful when updates are kept paused between runs) |

---

## Usage

```yaml
# Install available updates, rebooting if needed
win_workman_tasks:
  - wu-run

# Install updates even when updates are kept paused
win_workman_tasks:
  - wu-run
win_workman_wu_unpause: true

# Pause updates for 14 days
win_workman_tasks:
  - wu-pause-14

# Pause updates for 3 weeks (inline duration)
win_workman_tasks:
  - wu-pause-3-w

# Resume paused updates
win_workman_tasks:
  - wu-resume

# Read the current FlightSettingsMaxPauseDays cap
win_workman_tasks:
  - wu-max_pause_days

# Raise the cap to 90 days
win_workman_tasks:
  - wu-max_pause_days-90

# Check whether updates are currently paused
win_workman_tasks:
  - wu-is_paused
```
