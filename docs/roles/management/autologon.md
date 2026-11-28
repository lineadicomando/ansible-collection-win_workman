# autologon — Windows automatic logon

Enables or removes automatic logon with `ansible.windows.win_auto_logon`.

## Actions

| Action | Does |
|---|---|
| `on` (default) | Enable autologon for `win_workman_autologon_user`; fails if the user is empty |
| `off` | Disable autologon and remove the stored credentials |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_autologon_user` | `{{ ansible_user \| default('') }}` | Account to log on |
| `win_workman_autologon_password` | `{{ ansible_password \| default('') }}` | Its password (vault it) |
| `win_workman_autologon_restart` | `false` | Restart (`pkg_utils` `restart`) after `on`/`off`, only when something changed |

## Notes

- The password is kept as the LSA secret `DefaultPassword`: encrypted, but any
  administrator of the host can decrypt it. Use a dedicated low-privilege account.
