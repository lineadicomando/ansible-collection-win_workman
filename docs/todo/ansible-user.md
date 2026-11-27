# `ansible_user` read as a variable

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## Roles that read `ansible_user` without a default

**Priority:** P2 — cosmetic in `ping`; in `openssh` and `win_iso` it may break a run
under cockpit-fleet, not exercised yet  
**Status:** found 2026-11-27 in a cockpit-fleet run of `win_edulab` (`win_wm.yaml`,
`todo: [ping]`); only `ping` observed, the others read in the tree at `2177542`

cockpit-fleet runs a template on its managed inventory and passes the
template's SSH user as `--user`. Ansible connects as that user, but `--user`
sets the connection option, not the variable: `ansible_user` stays undefined
unless the inventory defines it (the `win_edulab` inventories do, in
`group_vars/all`; a Fleet inventory need not). The same happens with
`ansible-playbook -u` or `remote_user` in `ansible.cfg`.

Since ansible-core 2.19 an undefined variable in a task name is a warning and
the name is printed as the error:

```
[WARNING]: Encountered 1 template error.
error 1 - 'ansible_user' is undefined
Origin: .../win_workman/roles/ping/tasks/act_on.yaml:2:9
TASK [lineadicomando.win_workman.ping : Ping << error 1 - 'ansible_user' is undefined >>]
```

The ping itself succeeds.

### Where it is read

| File | Use | Without `ansible_user` |
| --- | --- | --- |
| `roles/ping/tasks/act_on.yaml:2` | task name `Ping {{ ansible_user }}` | warning, observed |
| `roles/openssh/vars/main/config.yaml:23` | `AllowUsers` value, enabled by default (`win_workman_openssh_manage_allow_users: true`) | to check: an undefined-variable failure, or worse an `AllowUsers` that locks the connection user out |
| `roles/win_iso/defaults/main.yaml:57` | `win_workman_win_iso_user`, the local administrator of the ISO | undefined-variable failure unless the variable is set |
| `roles/autologon/defaults/main.yaml:2` | `win_workman_autologon_user` | has `default('')`, and `act_on` asserts it: fine |
| `roles/autologon/meta/mcp.yaml:11` | MCP default shown to the caller | display only |

### What to change

- `ping`: a name that templates without it, e.g.
  `Ping {{ ansible_user | default(inventory_hostname) }}` or a plain `Ping`.
- `openssh`: the user Ansible is connected as, whatever set it. Either
  `ansible_user | default(...)` with an explicit fallback variable, or read it
  on the host (`whoami` / `$env:USERNAME` in the session that writes
  `sshd_config`) so that `AllowUsers` always names the account in use. Fail
  with a clear message rather than write `AllowUsers` with an empty or wrong
  name.
- `win_iso`: keep the default, but assert `win_workman_win_iso_user` is set
  with a message that names the variable, as `autologon` does.

### How to test

- `ansible-playbook -u <user>` against an inventory without `ansible_user`:
  `ping` has no warning; `openssh` (with `manage_allow_users`) writes the
  connected user or fails with the message, never an empty `AllowUsers`.
- The same template in cockpit-fleet on its managed inventory.
