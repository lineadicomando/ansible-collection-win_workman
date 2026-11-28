# lock — Maintenance mode

Puts a workstation in maintenance mode: a legal notice on the logon screen, the last
username hidden, interactive logon restricted to the allowed users, user sessions
logged off. Saves what the host had and gives it back on `off`.

## Actions

| Action | Does |
|---|---|
| `on` (default) | Save the current state, set the banner, `DontDisplayLastUserName=1`, `SeInteractiveLogonRight` = allowed users; then log off every session (Active or Disconnected) and wait, if `win_workman_mode_force_logoff` |
| `off` | Restore the three settings from the saved state and drop it; changes nothing on a host that is not locked; logs nobody back on |
| `reset` | Unlock without the saved state: each setting to its Windows default, saved state dropped (below) |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_mode_title` | `Maintenance in progress` | Legal notice title |
| `win_workman_mode_text` | `The system is currently undergoing maintenance.\nContact IT for assistance.\n` | Legal notice body |
| `win_workman_mode_force_logoff` | `true` | Log the sessions off on `on` |
| `win_workman_mode_interactive_logon_users` | `[Administrators]` | Who may log on while locked: names, `DOMAIN\name` or SIDs |
| `win_workman_mode_interactive_logon_fallback_users` | `[S-1-5-32-544, S-1-5-32-545, S-1-5-32-551]` | Who may log on when there is nothing to restore (`off` with an empty saved right, `reset`): Administrators, Users, Backup Operators, as SIDs so the list does not depend on the language |
| `win_workman_logoff_timeout_seconds` | `300` | Wait for the sessions to end (`pkg_utils` default) |

`Administrators` is the group's name on English and Italian Windows; where it is
localised use `S-1-5-32-544`.

## Saved state

Under `HKLM:\SOFTWARE\Ansible\WinMaint`, written only when absent, so a second `on`
updates banner and allowed users but keeps what the host had before the first:

| Value | Meaning |
|---|---|
| `LegalNoticeCaptionExists`, `LegalNoticeTextExists` | `1` if the value existed before the lock, else `0`; written last, so a run cut in between saves again next time |
| `LegalNoticeCaption`, `LegalNoticeText` | Their content before the lock |
| `DontDisplayLastUserName` | Its value before, `0` if absent (`off` then removes it) |
| `SeInteractiveLogonRight` | Holders of the right before the lock (multistring, read with `pkg_utils` `se_read`) |

`off` acts only on what was saved: a notice or a logon policy set by other means is
not the role's to remove.

## Notes

- A run that stops between `on` and `off` (a failed task, an unreachable host) leaves
  the host locked: put the work in a `block` with `lock-off` in `always`, as the
  project's `playbooks/maintenance.yaml` does. `lock-off` later works the same, the
  saved state stays on the host.
- Guards against a console nobody can log on to: `on` fails if the allowed users are
  empty or the host does not report who holds `SeInteractiveLogonRight` (a failed or
  empty `secedit` export would be saved and restored). `off` never restores an empty
  saved right (a host locked by an older version, or a state edited by hand): it sets
  the fallback users, warns naming the host, and completes.
- `reset` is for a host left locked with its saved state lost, which `off` cannot tell
  from one configured so on purpose. It sets `LegalNoticeCaption`/`LegalNoticeText`
  to empty strings, removes `DontDisplayLastUserName`, sets `SeInteractiveLogonRight`
  to the fallback users. A notice or logon policy the site had set is lost: with the
  saved state still there, use `off`.
- Not covered: Remote Desktop (`SeRemoteInteractiveLogonRight` is untouched, so
  *Remote Desktop Users* can still log on); SSH and service accounts (no interactive
  logon). Autologon: an account outside the allowed users cannot log on while
  locked, and the legal notice holds any autologon at the logon screen until
  confirmed.
- Known bug (P1): after `off` or `reset`, idle hosts show the user name/password prompt
  instead of the user list until a restart: the LogonUI started by the logoff read
  `DontDisplayLastUserName=1` and reads it only at start. Workaround: `restart`. See
  [lock-off](../../todo/lock-off.md).
- Regression test: `tests/lock.yaml` in the project repository.
