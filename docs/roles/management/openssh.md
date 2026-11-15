# Role: openssh

Manages OpenSSH Server on the hosts: reports how it is installed and hardens its
configuration. Every other role reaches the hosts through this server, so the role
never installs or removes it: a host it can talk to already has OpenSSH, and removing
it would cut off the connection the play runs on. The server gets on the hosts with
the Windows installation (`win_iso`, as the Win32-OpenSSH MSI or as the Windows
capability).

Replaces `secure_ssh`, which stays as a deprecated alias (see below).

---

## Actions

> **Default action: `info`** — bare `openssh` only reads.

| Action | Description |
|---|---|
| `info` | Report the installation: `source` (`msi`, `capability`, `unknown`, `none`), version, MSI ProductCode or capability name, state and start mode of the `sshd` service, path of `sshd.exe`. Changes nothing |
| `harden` | Apply the hardened configuration: public key of `ansible_ssh_pub_key_path` in `administrators_authorized_keys`, `PubkeyAuthentication yes`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `AllowUsers <ansible_user>` |
| `unharden` | Remove those settings and the key, back to the defaults of `sshd_config` |
| `on` | Alias for `harden`; it installs nothing |
| `off` | Alias for `unharden`; it never uninstalls OpenSSH |

`harden` and `unharden` edit `C:\ProgramData\ssh\sshd_config` and
`C:\ProgramData\ssh\administrators_authorized_keys` with `win_lineinfile`, keeping a
backup of each file they change. Then, only if something changed:

- **`sshd -t`** checks the new configuration. A directive the installed version does
  not know (`KbdInteractiveAuthentication` needs OpenSSH 8.7 or later) would keep
  `sshd` from starting again and leave the host out of reach, so the task fails
  instead and the service keeps running on the configuration it has loaded.
- **`sshd` restarts**: it reads `sshd_config` only when it starts, so without a
  restart the new settings have no effect. The session the play runs on survives
  the restart.

The directives are written above the first `Match` line. A global directive written
after it belongs to that `Match` block: `secure_ssh` appended `AllowUsers` at the end
of the file, inside `Match Group administrators`, where it restricted administrators
only. `harden` and `unharden` move such lines out of every `Match` block.

After `unharden` the key no longer opens a session: the next run needs
`ansible_password`.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_openssh_manage_authorized_keys` | `true` | Deploy the public key of `ansible_ssh_pub_key_path` |
| `win_workman_openssh_enable_pubkey_auth` | `true` | Set `PubkeyAuthentication yes` |
| `win_workman_openssh_disable_password_auth` | `true` | Set `PasswordAuthentication no` and `KbdInteractiveAuthentication no` |
| `win_workman_openssh_manage_allow_users` | `true` | Set `AllowUsers <ansible_user>` |

Each one falls back on the `win_workman_secure_ssh_*` variable of the same name, so
an inventory written for `secure_ssh` keeps its overrides.

---

## Usage

```bash
# How OpenSSH is installed, and which version
ansible-playbook lineadicomando.win_workman.win_workman -e '{"t": "openssh"}'

# Harden it, keeping password authentication on
ansible-playbook lineadicomando.win_workman.win_workman \
  -e '{"t": "openssh-harden", "win_workman_openssh_disable_password_auth": false}'
```

---

## secure_ssh (deprecated)

`secure_ssh` is the former name of this role and now prints a deprecation notice,
then runs the matching action of `openssh`:

| Old task | Runs |
|---|---|
| `secure_ssh`, `secure_ssh-on` | `openssh-harden` |
| `secure_ssh-off` | `openssh-unharden` |

It will be removed in a later release, together with the fallback on the
`win_workman_secure_ssh_*` variables.
