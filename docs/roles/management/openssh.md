# openssh — OpenSSH Server

Reports how OpenSSH Server is installed, upgrades the Win32-OpenSSH MSI and hardens
`sshd_config`. Every role reaches the hosts through this server, so the role never
installs or removes it: OpenSSH gets on the hosts with the Windows installation
(`win_iso`, MSI or capability). Replaces `secure_ssh`, kept as a deprecated alias.

## Actions

| Action | Does |
|---|---|
| `info` *(default)* | report `source` (`msi`, `capability`, `unknown`, `none`), version, MSI ProductCode or capability name, `sshd` state and start mode, path of `sshd.exe`; changes nothing |
| `update` | upgrade an MSI installation to the release of `vars/main/msi.yaml`; nothing when already there or later; refuses a capability: [below](#update) |
| `harden` | key of `ansible_ssh_pub_key_path` in `administrators_authorized_keys`, `PubkeyAuthentication yes`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `AllowUsers <ansible_user>` |
| `unharden` | remove those directives and the key, back to the defaults of `sshd_config` |
| `on`, `off` | aliases of `harden`, `unharden`: they never install or uninstall |

`harden`/`unharden` edit `C:\ProgramData\ssh\sshd_config` and
`administrators_authorized_keys` with `win_lineinfile`, keeping a backup of each file
changed. Only when something changed:

- **`sshd -t`** checks the configuration: a directive the installed version does not
  know (`KbdInteractiveAuthentication` needs OpenSSH 8.7+) would keep `sshd` from
  starting and leave the host out of reach, so the task fails and the service keeps the
  configuration it has loaded;
- **`sshd` restarts**, since it reads `sshd_config` only at start; the play's session
  survives.

The directives are written above the first `Match` line: a global directive after it
belongs to that block. `secure_ssh` appended `AllowUsers` at the end, inside `Match Group
administrators`, where it restricted administrators only; `harden`/`unharden` first
remove the managed directives from every `Match` block. After `unharden` the key no longer
opens a session: the next run needs `ansible_password`.

## update

`msiexec` stops `sshd` and replaces the binaries the play's session runs on, so the
upgrade cannot run inside that session:

1. `info`; stop unless `source` is `msi` (the capability is updated by Windows Update,
   and replacing it with the MSI over SSH would remove the server the play runs on);
2. if older than the target: download the MSI (sha256 checked) and copy it with
   `files/update.ps1` to `win_workman_remote_tmp\openssh-update`;
3. **check before changing anything**: extract the new MSI (`msiexec /a`) and run its
   `sshd.exe -t` on the current `sshd_config`; a directive the new release rejects fails
   the task here, session up and nothing changed;
4. start `update.ps1` from a SYSTEM scheduled task and return once it runs: it saves
   `HKLM\SOFTWARE\OpenSSH` (`DefaultShell`) and the files of `C:\ProgramData\ssh`, stops
   `sshd`, runs `msiexec /i`, restores whatever value or file went missing, starts `sshd`,
   writes `result.json`;
5. wait for `result.json` (the upgrade takes seconds, too few to see port 22 close; the
   session survives, or the play reconnects once `sshd` is back), read it, remove the task
   and the MSI copies; fail unless no errors, `sshd` running, target version installed.

The MSIs share their UpgradeCode, so a failed `msiexec` rolls back by itself and the
script still starts `sshd`. Logs (`msiexec.log`, `result.json`) stay in the update
directory. No outcome within `win_workman_openssh_update_up_timeout`: the host needs its
console (read the logs, `Start-Service sshd`). Roll out on one host first. The release
(tag, MSI name, sha256, bumped together) is in `vars/main/msi.yaml`, which `win_iso` loads
too, so ISO and `update` install the same version.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_openssh_manage_authorized_keys` | `true` | deploy the key of `ansible_ssh_pub_key_path` |
| `win_workman_openssh_enable_pubkey_auth` | `true` | `PubkeyAuthentication yes` |
| `win_workman_openssh_disable_password_auth` | `true` | `PasswordAuthentication no`, `KbdInteractiveAuthentication no` |
| `win_workman_openssh_manage_allow_users` | `true` | `AllowUsers <ansible_user>`: every other account is refused |
| `win_workman_openssh_update_up_timeout` | `600` | `update`: seconds to wait for `sshd` and the outcome |

The four flags fall back on the `win_workman_secure_ssh_*` variable of the same name.

## Notes

- `secure_ssh` (deprecated): prints a notice, then `secure_ssh`/`secure_ssh-on` run
  `openssh-harden` and `secure_ssh-off` runs `openssh-unharden`. It goes in a later
  release, together with the `win_workman_secure_ssh_*` fallbacks.
- Harden keeping passwords: `-e '{"todo": "openssh-harden",
  "win_workman_openssh_disable_password_auth": false}'`.
