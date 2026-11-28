# autoshutdown — Scheduled shutdown

Leaves a scheduled task on the host that shuts it down at fixed times, every day or
on chosen weekdays. Once there, the host shuts down on its own: no controller,
network or Ansible run is involved. [`shutdown`](system-tools.md#shutdown) is the push
counterpart (now, from the controller).

## Actions

| Action | Does |
|---|---|
| `on[-<HHMM>]` (default) | Create or update the task. A time argument (`HHMM`, since task strings split on `-`) means that time every day and wins over the variable: `autoshutdown-on-1830` |
| `off` | Remove the task with the current name and path |
| `info` | Report task, enabled, status, schedule (`18:30 monday,...` or `every day`), command, next/last run and last result; the raw task stays in the `win_workman_autoshutdown_info` fact |

`on` is idempotent and replaces the triggers as a whole, so entries removed from the
schedule disappear from the host. Settings are validated before the host is touched.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_autoshutdown_schedule` | `"18:30"` | A `"HH:MM"` time for every day, or a list of entries (below) |
| `win_workman_autoshutdown_warning` | `60` | Seconds of warning (`shutdown /t`); `0` shuts down at once |
| `win_workman_autoshutdown_message` | `Spegnimento automatico programmato: salvare il lavoro.` | Warning text (`shutdown /c`); double quotes become single, as they would end `/c` early |
| `win_workman_autoshutdown_mode` | `always` | `always` shuts down whoever is logged on; `nouser` is reserved and fails as not implemented, see [management](../../todo/management.md) |
| `win_workman_autoshutdown_task_path` | `\win_workman` | Task Scheduler folder, starting with a backslash |
| `win_workman_autoshutdown_task_name` | `AutoShutdown` | Task name |

```yaml
win_workman_autoshutdown_schedule:
  - time: "18:30"
    days: [monday, tuesday, wednesday, thursday, friday]
  - time: "14:00"
    days: [saturday]
```

An entry is a `"HH:MM"` time or `{time, days}`; without `days` it applies to every
day; a day in no entry has no shutdown (Sunday above); several entries may cover the
same day. Days are English names, any case and order. Each entry is one trigger: daily
when it covers all seven days, weekly otherwise. Host local time, daylight saving
followed (start boundary without a time zone suffix). Per-lab times belong in the
lab's `group_vars`.

## Notes

- Quote the times: YAML reads a bare `18:30` as the sexagesimal number 1110. The role
  refuses anything not a `"HH:MM"` string.
- The task: `SYSTEM`, highest privileges, `%SystemRoot%\System32\shutdown.exe /s /f /t
  <warning> /c "<message>"`, time limit 5 min, no wake to run. "Run as soon as
  possible after a missed start" is off on purpose: a host already off at the
  scheduled time would otherwise shut down as soon as it is switched on next morning.
- `/f` closes applications without waiting: unsaved work is lost when the warning runs
  out. A logged-on user can normally cancel with `shutdown /a` (standard users hold
  the shutdown privilege on a workstation); `warning: 0` leaves no time for that.
- `off` removes only the task with the current name and path: run `autoshutdown-off`
  before changing either, or the old task keeps shutting the host down. The folder
  goes with its last task, but of a nested path (`\lab_a\evening`) only the innermost
  one: `\lab_a` stays, empty.
- The task fires only at its times: a night maintenance run on hosts woken with `wol`
  is unaffected unless still running at a scheduled time.
