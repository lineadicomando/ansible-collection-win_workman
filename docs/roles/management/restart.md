# restart — Controlled reboot

Reboots the host through `pkg_utils` `restart` and waits until it is really back.

## Actions

| Action | Does |
|---|---|
| `on` *(default)* | reboot unconditionally |
| `if-pending` | reboot only when a reboot is pending: CBS `RebootPending`, WU `RebootRequired`, `PendingFileRenameOperations` or `WinSxS\pending.xml`; a bare `if` or another condition fails |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_restart_timeout` | `600` | seconds to wait for the host after the reboot |

## Notes

- The host counts as back when `sshd` runs, it has been up for 60 s and component
  servicing (TrustedInstaller, TiWorker) has stayed idle for 20 s: after updates Windows
  finishes installing at boot and may reboot again on its own once the logon screen is
  up, and the next task would run into that reboot. A connection lost meanwhile only
  makes `win_reboot` test again, until the timeout.
- `win_workman_restart: false` does not stop this role; it only stops the roles that
  reboot on their own (`wu`, `sfc`).
- Before rebooting, `if-pending` prints the flags set and, for
  PendingFileRenameOperations, up to 20 of the queued operations; the reboot consumes
  them, so the run log is the only place left to read them. Every role using `pkg_utils`
  `pending_restart` (`wu-run`, `sfc`, the AutoCAD roles) prints the same:

  ```
  Reboot pending: PendingFileRenameOperations
  rename C:\Windows\Temp\app\new.dll -> C:\Windows\Temp\app\app.dll
  delete C:\Windows\Temp\app\old.dll
  ```
