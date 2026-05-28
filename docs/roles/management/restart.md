# Role: restart

Performs a controlled system restart, optionally only when a pending reboot is detected.

---

## Actions

| Action | Description |
|---|---|
| `on` | Restart the system unconditionally |
| `if-pending` | Restart only if a pending reboot is detected (CBS, WUA, PendingFileRenameOperations, WinSxS) |

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
