# Role: lock

Enables or disables *maintenance mode* on a workstation: restricts interactive
logon to administrators only, displays a customisable banner on the logon
screen, and optionally force-logs off the user sessions.

---

## Actions

| Action | Description |
|---|---|
| `on` *(default)* | Enable maintenance mode: set banner, restrict logon rights, optionally force logoff |
| `off` | Disable maintenance mode: give back the banner, the last username setting and the logon rights the host had |
| `reset` | Unlock without the saved state: every setting to its Windows default |

---

## What `on` does

1. Sets a legal notice title and text on the Windows logon screen (registry).
2. Hides the last logged-in username from the logon screen.
3. Restricts `SeInteractiveLogonRight` to `win_workman_mode_interactive_logon_users`.
4. If `win_workman_mode_force_logoff` is `true`, logs off every user session,
   Active or Disconnected, and waits for them to end.

Before changing each of the three settings, `on` saves what the host had under
`HKLM:\SOFTWARE\Ansible\WinMaint`. A second `on` on a locked host updates the
banner and the allowed users and leaves the saved state alone, so it still
holds what the host had before the first one.

`off` reverses steps 1–3 from the saved state and then removes it: a value that
did not exist is removed, one that did gets its content back. It does not log
anybody back on.

`off` only acts on what `on` saved. On a host that is not locked it changes
nothing: a legal notice or a logon policy set by other means is not the role's
to remove.

## What can leave a host locked

A host stays locked when the run stops between `on` and `off`: a task in
between fails, or the host becomes unreachable. Put the work in a `block` with
`lock-off` in its `always` section, as `playbooks/maintenance.yaml` of the
project repository does. Running `lock-off` later unlocks the host just the
same, because the saved state stays on it.

The role refuses to proceed rather than risk a console nobody can log on to:

- `on` fails if `win_workman_mode_interactive_logon_users` is empty, or if the
  host does not report who holds `SeInteractiveLogonRight` now (`secedit`
  export failed or came back empty): the latter would be saved and restored.
- `off` never restores an empty saved `SeInteractiveLogonRight`. `on` does not
  save one any more, but a host locked by an older version of the role may
  hold it. `off` then sets the right to
  `win_workman_mode_interactive_logon_fallback_users`, prints a warning that
  names the host, and completes the unlock.

## `reset`: unlocking without the saved state

`off` goes by the saved state alone, so a host whose saved state was lost while
locked stays as it is: nothing tells it apart from one configured that way on
purpose. `lock-reset` is the explicit way out. It does not restore anything; it
sets each of the three settings to its Windows default and drops whatever
saved state is left:

| Setting | After `reset` |
|---|---|
| `LegalNoticeCaption`, `LegalNoticeText` | Empty strings: no notice |
| `DontDisplayLastUserName` | Removed: the last username is shown |
| `SeInteractiveLogonRight` | `win_workman_mode_interactive_logon_fallback_users` |

A legal notice or a logon policy the site had set by other means is lost with
it: on a host that still has its saved state, use `off`.

## What it does not cover

- **Remote Desktop.** Only `SeInteractiveLogonRight` is restricted. Where RDP
  is enabled, members of *Remote Desktop Users* can still log on during
  maintenance (`SeRemoteInteractiveLogonRight`).
- **SSH and services.** The Ansible connection and service accounts do not use
  an interactive logon and are not affected.
- **Autologon.** An account outside the allowed users cannot log on
  automatically while the host is locked, and the legal notice holds any
  autologon at the logon screen until someone confirms it.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_mode_title` | `"Maintenance in progress"` | Logon screen legal notice title |
| `win_workman_mode_text` | *(see below)* | Logon screen legal notice body |
| `win_workman_mode_force_logoff` | `true` | Log the user sessions off when enabling maintenance mode |
| `win_workman_mode_interactive_logon_users` | `[Administrators]` | Groups/users allowed to log on during maintenance (`SeInteractiveLogonRight`); names, `DOMAIN\name` or SIDs |
| `win_workman_mode_interactive_logon_fallback_users` | `[S-1-5-32-544, S-1-5-32-545, S-1-5-32-551]` | Who may log on when there is nothing to restore: `off` with an empty saved right, and `reset`. The default is Administrators, Users and Backup Operators |
| `win_workman_logoff_timeout_seconds` | `300` | Seconds to wait for the sessions to end (shared `pkg_utils` default) |

Default `win_workman_mode_text`:
```
The system is currently undergoing maintenance.
Contact IT for assistance.
```

All of them are plain role defaults: inventory, play and extra vars override
them. `Administrators` is the group's name on English and Italian Windows; on a
system where it is localised, use its SID, `S-1-5-32-544`.

---

## Usage

```yaml
# Lock down before a maintenance window
win_workman_tasks:
  - lock-on
win_workman_mode_title: "System update in progress"
win_workman_mode_text: "Back at 14:00. Contact helpdesk@school.it."
win_workman_mode_interactive_logon_users:
  - Administrators
  - Domain Admins

# Restore after maintenance
win_workman_tasks:
  - lock-off
```

---

## Files

| File | Covers |
|---|---|
| `tasks/act_on.yaml`, `tasks/act_off.yaml` | Call the three files below with `win_workman_mode_state` `present` / `absent` |
| `tasks/act_reset.yaml` | Sets the Windows defaults directly, without them |
| `tasks/maint_mode_banner.yaml` | `LegalNoticeCaption` and `LegalNoticeText` |
| `tasks/maint_mode_display_last_username.yaml` | `DontDisplayLastUserName` |
| `tasks/maint_mode_se_logon.yaml` | `SeInteractiveLogonRight`, read through `pkg_utils` `se_read` |

Saved state, all under `HKLM:\SOFTWARE\Ansible\WinMaint`:

| Value | Meaning |
|---|---|
| `LegalNoticeCaptionExists`, `LegalNoticeTextExists` | `1` if the value existed before the lock, `0` if not |
| `LegalNoticeCaption`, `LegalNoticeText` | Their content before the lock |
| `DontDisplayLastUserName` | Its value before the lock, `0` if it did not exist |
| `SeInteractiveLogonRight` | Accounts that held the right before the lock (multistring) |

Regression test: `tests/lock.yaml` in the project repository.
