# Role: restart

Performs a controlled system restart, optionally only when a pending reboot is detected.

---

## Actions

| Action | Description |
|---|---|
| `on` | Restart the system unconditionally |
| `if-pending` | Restart only if a pending reboot is detected (CBS, WUA, PendingFileRenameOperations, WinSxS) |

Before restarting, `if-pending` prints which flags were set and, for
PendingFileRenameOperations, up to 20 of the queued file operations:

```
Reboot pending: PendingFileRenameOperations
rename C:\Windows\Temp\app\new.dll -> C:\Windows\Temp\app\app.dll
delete C:\Windows\Temp\app\old.dll
```

The reboot consumes those operations, so the run log is the only place left to
tell what asked for it. Every role that checks for a pending reboot through
`pkg_utils` (wu-run, sfc, some package roles) prints the same lines.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_restart_timeout` | `600` | Seconds to wait for the host to come back after reboot |

---

## Usage

```yaml
# Unconditional restart
win_workman_tasks:
  - restart

# Restart only if needed
win_workman_tasks:
  - restart-if-pending
```
