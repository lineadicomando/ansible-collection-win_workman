# Role: openssh

Manages OpenSSH Server on the hosts: reports how it is installed, upgrades the
Win32-OpenSSH MSI and hardens the configuration. Every other role reaches the hosts through this server, so the role
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
| `update` | Upgrade an MSI installation to the release set in `roles/openssh/vars/main/msi.yaml` (see below). Does nothing when the installed version is already there or later; refuses a capability installation |
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

## update

The play reaches the host through the very server it upgrades: `msiexec` stops
`sshd` and replaces the binaries the SSH session runs on, so the upgrade cannot run
inside that session. `update` goes like this:

1. `info`; stop unless `source` is `msi`. The Windows capability is updated by
   Windows Update (`wu`), and replacing it with the MSI over SSH would remove the
   server the play runs on.
2. If the installed version is older than the target: download the MSI into
   `win_workman_storage_path` (sha256 checked) and copy it, with
   `files/update.ps1`, to `C:\Windows\Temp\ansible\openssh-update`.
3. **Check before changing anything**: extract the new MSI (`msiexec /a`) and run
   the new `sshd.exe -t` on the current `sshd_config`. A directive the new release no
   longer accepts would keep `sshd` from starting after the upgrade: the task fails
   here, while the session is still up and nothing has changed.
4. Start `update.ps1` from a SYSTEM scheduled task and return once it runs. The
   script saves `HKLM\SOFTWARE\OpenSSH` (where `DefaultShell` lives) and the files
   of `C:\ProgramData\ssh`, stops `sshd`, runs `msiexec /i`, puts back whatever
   value or file went missing, starts `sshd` and writes `result.json`.
5. Wait for `result.json`. The upgrade takes a few seconds, `sshd` down included,
   too few to watch port 22 close. The session of the play survives `sshd`
   stopping; if the upgrade cuts it, the play waits for `sshd` and reconnects. Then
   read `result.json`, remove the task and the MSI copies. The run fails unless the result has no errors, `sshd` running and
   the target version installed.

The two MSIs share their UpgradeCode, so the new one is a major upgrade: if
`msiexec` fails, Windows Installer rolls back to the installed version by itself,
and the script still starts `sshd` again. The logs stay in
`C:\Windows\Temp\ansible\openssh-update` (`msiexec.log`, `result.json`).

If no outcome arrives within `win_workman_openssh_update_up_timeout` the run
fails and the host needs its console: read `result.json` and `msiexec.log`, then
`Start-Service sshd`. Roll out on one host first, then on the lab.

The release is set in `roles/openssh/vars/main/msi.yaml`: tag, MSI file name and
sha256, bumped together. `win_iso` loads the same file, so the ISO and `update`
always install the same version.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_openssh_manage_authorized_keys` | `true` | Deploy the public key of `ansible_ssh_pub_key_path` |
| `win_workman_openssh_enable_pubkey_auth` | `true` | Set `PubkeyAuthentication yes` |
| `win_workman_openssh_disable_password_auth` | `true` | Set `PasswordAuthentication no` and `KbdInteractiveAuthentication no` |
| `win_workman_openssh_manage_allow_users` | `true` | Set `AllowUsers <ansible_user>` |
| `win_workman_openssh_update_up_timeout` | `600` | `update`: seconds to wait for `sshd` and for the outcome of the upgrade once it has started |

The four flags fall back on the `win_workman_secure_ssh_*` variable of the same name, so
an inventory written for `secure_ssh` keeps its overrides.

---

## Usage

```bash
# How OpenSSH is installed, and which version
ansible-playbook lineadicomando.win_workman.win_workman -e '{"t": "openssh"}'

# Upgrade the MSI installation, one PC first
ansible-playbook lineadicomando.win_workman.win_workman -l pc01 -e '{"t": "openssh-update"}'

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
