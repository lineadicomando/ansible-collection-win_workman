# System tool roles

> **Work in progress** — preliminary draft.

Reference for roles that perform targeted system configuration with no or
minimal variables: `oobe`, `widgets`, `secure_ssh`, `wim`, `ms_account`,
`chkdsk`, `sfc`, `logoff`, `restart`, `shutdown`, `ping`, `wol`.

---

## oobe

Suppresses or restores the Windows Out-of-Box Experience (OOBE) prompts
(privacy settings wizard, language setup, Microsoft account prompts) that
appear after first login or after a system reset.

| Action | Description |
|---|---|
| `on` | Suppress OOBE prompts via registry |
| `off` | Restore OOBE prompts |

No variables beyond the global collection defaults.

---

## widgets

Enables or disables the Windows 11 Widgets panel (news and interests on the
taskbar). Applies a system-wide Group Policy registry key and logs off active
sessions so the change takes effect immediately.

| Action | Description |
|---|---|
| `on` | Enable the Windows 11 Widgets panel |
| `off` | Disable the Windows 11 Widgets panel |

No variables. Logoff is automatic — active user sessions are terminated before
the registry key is written.

---

## secure_ssh

Hardens the OpenSSH server (`sshd`) installed on Windows. Intended for
workstations managed exclusively via SSH (no WinRM).

| Action | Description |
|---|---|
| `on` | Apply hardened SSH configuration: enable public-key auth, disable password auth, manage `authorized_keys`, restrict `AllowUsers` |
| `off` | Revert to default SSH configuration |

Internally, `on` calls `secure_ssh_handler` with these flags set:

| Flag | Value |
|---|---|
| `win_workman_secure_ssh_manage_authorized_keys` | `true` |
| `win_workman_secure_ssh_enable_pubkey_auth` | `true` |
| `win_workman_secure_ssh_disable_password_auth` | `true` |
| `win_workman_secure_ssh_manage_allow_users` | `true` |

No user-facing defaults file — all configuration is derived from
`ansible_ssh_pub_key_path` and inventory user variables (see collection README).

---

## wim

Runs DISM (`Deployment Image Servicing and Management`) component store
health operations.

| Action | Description |
|---|---|
| `on` / `check` | Run `DISM /CheckHealth` |
| `scan` | Run `DISM /ScanHealth` |
| `repair` | Run `DISM /RestoreHealth` |

No variables. Operations run against the live Windows image (`/Online`).

> `repair` downloads missing files from Windows Update; the host must have
> internet access or a local WSUS/WIM source.

---

## ms_account

Enables or disables the requirement to sign in with a Microsoft account.
Targets the OOBE and Settings account linking prompts.

| Action | Description |
|---|---|
| `on` | Allow Microsoft account sign-in |
| `off` | Block Microsoft account sign-in (force local accounts only) |

No variables.

---

## chkdsk

Runs Check Disk (`chkdsk`) to detect and repair file system errors.

| Action | Description |
|---|---|
| `on` | Run Check Disk on next boot |

No variables. Operation is queued for the next system restart.

---

## sfc

Runs the Windows System File Checker (`sfc /scannow`) to verify and repair
system file integrity.

| Action | Description |
|---|---|
| `on` | Scan and repair system files |

No variables. Operation may require a restart to complete repairs.

---

## logoff

Forces the logoff of all interactive user sessions on the target.

| Action | Description |
|---|---|
| `on` | Force logoff all interactive sessions |

No variables. This action disconnects all logged-in users immediately.

---

## restart

Initiates a controlled system restart.

| Action | Description |
|---|---|
| `on` | Restart the system |

Uses the global `win_workman_restart_timeout` (default: 180 seconds) to wait
for the host to come back online.

---

## shutdown

Initiates a controlled system shutdown.

| Action | Description |
|---|---|
| `on` | Shut down the system |

No automatic restart delay — shutdown is immediate.

---

## ping

Tests connectivity to the target host via `win_ping`.

| Action | Description |
|---|---|
| `on` | Ping the target (connectivity test) |

No variables. Returns success if the target responds.

---

## wol

Sends a Wake-on-LAN (WoL) magic packet to power on a host.

| Action | Description |
|---|---|
| `on` | Send WoL packet and wait for SSH connectivity |

Requires:
- `ansible_mac` — MAC address of the target NIC
- `ansible_broadcast` (optional) — broadcast address for WoL packet
- `ansible_host` — hostname or IP for SSH connectivity check (timeout: 300s)

Delegated to `localhost` — the controller sends the WoL packet and monitors
for SSH port 22 availability on the target.
