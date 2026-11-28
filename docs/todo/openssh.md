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

**Priority:** P3 — at the next `minor` release (a removal changes behaviour)  
**Status:** alias in place since `70adfb1` (2026-11-15, released in v0.7.0); still there at v0.9.2 (checked 2026-11-28)

`roles/secure_ssh/` prints a deprecation notice and runs `openssh-harden` or
`openssh-unharden`; `roles/openssh/defaults/main.yaml` falls back on the
`win_workman_secure_ssh_*` variables. Remove both together, with the *secure_ssh*
section of `docs/roles/management/openssh.md`, its mention in `docs/index.md`, and
`roles/secure_ssh/meta/mcp.yaml` (then `tools/fleet_skills.py`). The upgrade note for
hosts hardened by the old role is in `CHANGELOG.md`: repeat it in the release commit.
