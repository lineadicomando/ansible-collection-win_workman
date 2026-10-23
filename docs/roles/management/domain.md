# Role: domain

Active Directory domain membership of a Windows host: joins it to a domain,
moves it back to a workgroup, or reports which of the two it is in. Join and
leave use `microsoft.ad.membership`; status reads `Win32_ComputerSystem` and
never changes state.

Works with any AD domain; written for the Samba AD DC that
[cockpit-samba-dc](https://github.com/lineadicomando/cockpit-samba-dc)
manages.

---

## Actions

| Action | Description |
|---|---|
| `status` *(default)* | Report membership; publish it as the `win_workman_domain_status` fact |
| `join` | Point DNS at the domain controllers, then join `win_workman_domain_name` |
| `leave` | Leave the domain for `win_workman_domain_workgroup`; the computer account stays in the directory, disabled, and a later `join` reuses it |
| `on` / `off` | Aliases for `join` / `leave` |

`join` and `leave` reboot the host when the change requires it
(`win_workman_domain_reboot`). A new domain logon is needed before domain
policies (drive maps, home drive) apply.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_domain_name` | `""` | DNS name of the domain, e.g. `example.com` (required by `join`, `leave`) |
| `win_workman_domain_admin_user` | `Administrator` | Domain account that joins the computer or disables its account on leave, used as `user@win_workman_domain_name` |
| `win_workman_domain_admin_password` | `""` | Its password; no default, supply it vault-encrypted (required by `join`, `leave`) |
| `win_workman_domain_dns_servers` | `[]` | DNS servers set on every adapter before `join`: the domain is found through SRV records only the DCs serve. Empty leaves the adapters alone |
| `win_workman_domain_workgroup` | `WORKGROUP` | Workgroup the host moves to on `leave` |
| `win_workman_domain_reboot` | `true` | Reboot when `join` or `leave` requires it |
| `win_workman_domain_set_fact` | `true` | `status` publishes `win_workman_domain_status` (`hostname`, `part_of_domain`, `domain`, `workgroup`) |

---

## Usage

```yaml
# Join the lab PCs to the domain served by dc01
win_workman_tasks:
  - domain-join
win_workman_domain_name: example.com
win_workman_domain_admin_user: admin
win_workman_domain_admin_password: "{{ vault_domain_admin_password }}"
win_workman_domain_dns_servers: ["192.0.2.10"]
```

```yaml
# Which PCs are in the domain?
win_workman_tasks:
  - domain
```

> The domain password is a different secret from the WinRM/SSH credential
> (`ansible_password`): keep it in a vault, never in extra vars.
