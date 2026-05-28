# Role: autologon

> **Work in progress** — preliminary draft.

Configures or removes Windows automatic logon for a local account using the
`win_auto_logon` module.

---

## Actions

| Action | Description |
|---|---|
| `on` | Enable autologon for `win_workman_autologon_user` |
| `off` | Disable autologon |

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_autologon_user` | `{{ ansible_user \| default('') }}` | Username for automatic logon |
| `win_workman_autologon_password` | `{{ ansible_password \| default('') }}` | Password for the autologon account |

`on` asserts that `win_workman_autologon_user` is not empty before proceeding.

---

## Usage

```yaml
# Enable autologon for a dedicated local account
win_workman_tasks:
  - autologon-on
win_workman_autologon_user: labuser
win_workman_autologon_password: "{{ vault_labuser_password }}"
```

> The autologon password is stored in plain text in the registry
> (`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`).
> Use a dedicated low-privilege account and vault the password.
