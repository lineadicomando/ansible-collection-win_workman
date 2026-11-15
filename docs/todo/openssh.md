# OpenSSH Server (`openssh`)

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md). The role and
the reasoning behind `update` are in `docs/roles/management/openssh.md`.

## `openssh-update`: first run on a production host

**Priority:** P2 — written and tested on a VM only; it touches the one service every run depends on  
**Status:** tested 2026-11-15 (`22ec497`) on a Windows 11 VM, MSI 10.0.0.0 → 10.4.0.0

What was tested: upgrade through the dispatcher with the old remote tmp ACL to start
with; a second run is a no-op; `sshd_config`, `administrators_authorized_keys` and
`HKLM\SOFTWARE\OpenSSH\DefaultShell` survive; a capability host is refused. The whole
upgrade, sshd down included, took about 3 s, and the session of the play survived it.

Not tested: an `msiexec` failure (rollback by Windows Installer, then the script starts
sshd again), a host whose sshd does not come back (the run fails after
`win_workman_openssh_update_up_timeout` and the console is needed), an upgrade across
more than one release.

When the next Win32-OpenSSH release is out: bump `roles/openssh/vars/main/msi.yaml`
(release tag, MSI file name, sha256; the two MSIs must share their UpgradeCode, so that
the new one is a major upgrade), run it on a VM with the previous MSI (the project repo
builds one with `test_vm_openssh_msi`), then one lab PC, then the lab.

## Remove the `secure_ssh` alias

**Priority:** P3 — at the next release of the collection, not before  
**Status:** alias in place since `70adfb1` (2026-11-15)

`roles/secure_ssh/` prints a deprecation notice and runs `openssh-harden` or
`openssh-unharden`; `roles/openssh/defaults/main.yaml` falls back on the
`win_workman_secure_ssh_*` variables. Remove both together, and the *secure_ssh
(deprecated)* section of `docs/roles/management/openssh.md`, the `secure_ssh` row in
`docs/architecture.md` and the mention in `README.md` and `docs/index.md`.

Hosts hardened by `secure_ssh` before `70adfb1` need one `openssh-harden`: the old role
never restarted sshd (so `PasswordAuthentication no` waited for the next reboot) and
appended `AllowUsers` inside `Match Group administrators` (non-admins not restricted).
Say so in the release notes.
