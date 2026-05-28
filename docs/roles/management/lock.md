# Role: lock

> **Work in progress** — preliminary draft.

Enables or disables *maintenance mode* on a workstation: restricts interactive
login to administrators only, displays a customisable banner on the login
screen, and optionally force-logs off active sessions.

---

## Actions

| Action | Description |
|---|---|
| `on` | Enable maintenance mode: set banner, restrict logon rights, optionally force logoff |
| `off` | Disable maintenance mode: remove banner, restore default logon rights |

---

## What `on` does

1. Sets a legal notice title and text on the Windows login screen (registry).
2. Hides the last logged-in username from the login screen.
3. Restricts the `SeInteractiveLogonRight` to `win_workman_mode_interactive_logon_users`.
4. If `win_workman_mode_force_logoff` is `true`, terminates all active interactive sessions.

`off` reverses steps 1–3. It does not restore previously logged-off sessions.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_mode_title` | `"Maintenance in progress"` | Login screen legal notice title |
| `win_workman_mode_text` | *(see below)* | Login screen legal notice body |
| `win_workman_mode_force_logoff` | `true` | Force active sessions to log off when enabling maintenance mode |
| `win_workman_mode_interactive_logon_users` | `[Administrators]` | Groups/users allowed to log in during maintenance (`SeInteractiveLogonRight`) |

Default `win_workman_mode_text`:
```
The system is currently undergoing maintenance.
Contact IT for assistance.
```

> These same variables are also defaults in `pkg_utils` and apply during
> software installs that trigger a maintenance window.

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
