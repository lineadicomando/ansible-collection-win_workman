# domain — Active Directory membership

Joins a host to an AD domain, moves it back to a workgroup, or reports which it is
in. `join`/`leave` use `microsoft.ad.membership`; `status` reads
`Win32_ComputerSystem` and changes nothing. Works with any AD domain; written for the
Samba AD DC that [cockpit-samba-dc](https://github.com/lineadicomando/cockpit-samba-dc)
manages.

## Actions

| Action | Does |
|---|---|
| `status` (default) | Report domain or workgroup; publish `win_workman_domain_status` |
| `join` | Set `win_workman_domain_dns_servers` on every adapter (if any), then join `win_workman_domain_name` |
| `leave` | Move to `win_workman_domain_workgroup`; the computer account is disabled, not deleted, and a later `join` reuses it |
| `on` / `off` | Aliases of `join` / `leave` |

`join` and `leave` fail early without domain name, user and password (and workgroup
for `leave`), and reboot the host when the change needs it.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_domain_name` | `""` | DNS name of the domain, e.g. `example.com` |
| `win_workman_domain_admin_user` | `Administrator` | Domain account, a bare name: the role passes `<user>@<domain_name>` |
| `win_workman_domain_admin_password` | `""` | Its password, vault-encrypted |
| `win_workman_domain_dns_servers` | `[]` | DNS servers set before `join`: the domain is found through SRV records only the DCs serve. Empty leaves the adapters alone |
| `win_workman_domain_workgroup` | `WORKGROUP` | Workgroup for `leave` |
| `win_workman_domain_reboot` | `true` | Reboot when `join`/`leave` require it |
| `win_workman_domain_set_fact` | `true` | `status` publishes `win_workman_domain_status` (`hostname`, `part_of_domain`, `domain`, `workgroup`) |

## Notes

- The domain password is a different secret from the WinRM/SSH credential
  (`ansible_password`): keep it in a vault, never in extra vars. The membership tasks
  run with `no_log`.
- `leave` does not put back the DNS servers `join` set.
- Domain policies (drive maps, home drive) apply only after a new domain logon.
