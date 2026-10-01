# Role: autoshutdown

Leaves a scheduled task on the host that shuts it down at fixed times, every
day or on chosen days of the week. Once the task is there the host shuts down on
its own: no controller, no network and no Ansible run are involved at that time.

[`shutdown`](system-tools.md#shutdown) is the push counterpart: it shuts hosts
down now, from the controller.

---

## Actions

| Action | Description |
|---|---|
| `on` | Create or update the scheduled task *(default action)* |
| `off` | Remove the scheduled task |
| `info` | Report the scheduled times, the task state and its last outcome, without changing anything |

`on` takes an optional time as task argument, written `HHMM` because task
strings split on `-`: `autoshutdown-on-1830` schedules 18:30 on every day and
wins over `win_workman_autoshutdown_schedule`.

`on` is idempotent: it reports a change only when the task on the host differs
from the requested one, and it replaces the triggers as a whole, so entries
removed from the schedule disappear from the host.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_autoshutdown_schedule` | `"18:30"` | When to shut down, see below |
| `win_workman_autoshutdown_warning` | `60` | Seconds of warning before the shutdown (`shutdown /t`); `0` shuts down at once |
| `win_workman_autoshutdown_message` | `Spegnimento automatico programmato: salvare il lavoro.` | Text shown to the logged-on user during the warning (`shutdown /c`) |
| `win_workman_autoshutdown_mode` | `always` | `always` shuts down whoever is logged on. `nouser` is reserved, see [Modes](#modes) |
| `win_workman_autoshutdown_task_path` | `\win_workman` | Task Scheduler folder of the task; starts with a backslash |
| `win_workman_autoshutdown_task_name` | `AutoShutdown` | Name of the scheduled task |

---

## Schedule

One time for every day of the week:

```yaml
win_workman_autoshutdown_schedule: "18:30"
```

Different times on different days:

```yaml
win_workman_autoshutdown_schedule:
  - time: "18:30"
    days: [monday, tuesday, wednesday, thursday, friday]
  - time: "14:00"
    days: [saturday]
```

- An entry is a `"HH:MM"` time or a mapping with `time` and an optional `days`
  list. An entry without `days` applies to every day.
- A day named by no entry has no shutdown — Sunday, in the example above.
- Several entries may cover the same day: `"14:00"` and `"18:30"` are two
  shutdowns a day.
- Days are the English names, in any case and any order.
- Times are in the local time of the host; Windows follows daylight saving.

**Quote the times.** YAML reads a bare `18:30` as the sexagesimal number 1110.
The role refuses anything that is not a `"HH:MM"` string and says so, before
touching the host.

Each entry becomes one trigger of the same task: a daily trigger when it covers
all seven days, a weekly one otherwise.

Per-lab times belong in the inventory, typically in the `group_vars` of the lab
group, so that a plain `autoshutdown` applies the right ones to each lab.

---

## Modes

`always`, the default and the only mode implemented, shuts the host down at the
scheduled time whoever is logged on, after the warning.

`nouser` — shut down only when no user session is open — is foreseen and
reserved: the variable accepts the name, and `on` fails with *not implemented
yet*. Any other value fails as unknown.

---

## The scheduled task

| Setting | Value |
|---|---|
| Account | `SYSTEM`, highest privileges |
| Action | `%SystemRoot%\System32\shutdown.exe /s /f /t <warning> /c "<message>"` |
| Run as soon as possible after a missed start | off |
| Wake the computer to run | off |

*Run as soon as possible after a missed start* is off on purpose: a host that
was already off at the scheduled time would otherwise shut down as soon as it is
switched on the next morning.

`/f` closes applications without waiting for them, so unsaved work is lost when
the warning runs out. Double quotes in the message are turned into single ones,
since they would end the `/c` argument early.

---

## Usage

```yaml
# Every day at 18:30
win_workman_tasks:
  - autoshutdown-on-1830

# The schedule declared in the inventory
win_workman_tasks:
  - autoshutdown

# What is scheduled on each host
win_workman_tasks:
  - autoshutdown-info

# No automatic shutdown, e.g. for an evening course
win_workman_tasks:
  - autoshutdown-off
```

`info` prints, for a host with the two-entry schedule above:

```
schedule:
  - 18:30 monday,tuesday,wednesday,thursday,friday
  - 14:00 saturday
```

and leaves the raw task in the `win_workman_autoshutdown_info` fact
(`task_exists`, `triggers`, `actions`, `state`, `settings`).

---

## Notes

- `off` removes the task with the **current** name and path only. Run
  `autoshutdown-off` before changing `win_workman_autoshutdown_task_name` or
  `win_workman_autoshutdown_task_path`, or the old task stays and keeps shutting
  the host down. The Task Scheduler folder is removed with its last task; of a
  nested path such as `\school\evening` only the innermost folder goes, and
  `\school` stays behind, empty.
- During the warning a logged-on user can normally cancel the shutdown with
  `shutdown /a`: standard users hold the shutdown privilege on a workstation.
  `win_workman_autoshutdown_warning: 0` leaves no time for that, and none to
  save work either.
- The task fires only at its times, so a maintenance run at night on hosts woken
  with `wol` is not affected, unless it is still running at a scheduled time.
