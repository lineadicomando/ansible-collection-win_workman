# System tool roles

Small management roles with few or no variables: `oobe`, `widgets`, `wim`,
`ms_account`, `chkdsk`, `sfc`, `logoff`, `shutdown`, `ping`, `wol`. `restart` has its
own page ([restart](restart.md)).

## oobe

Toggles the OOBE privacy and first-logon screens through `HKLM` values: the
`DisablePrivacyExperience` policy (`Policies\Microsoft\Windows\OOBE`) and, under
`CurrentVersion\OOBE`, `DisablePrivacyExperience`, `PrivacyConsentStatus`,
`CompletedPrivacyConsent`, `DisableVoice`, `SkipPrivacySettings`, `SkipMachineOOBE`,
`SkipUserOOBE` (1) and `SystemSetupInProgress` (0).

| Action | Does |
|---|---|
| `on` *(default)* | remove those values: Windows shows the OOBE screens again |
| `off` | write them: the screens are skipped |

## widgets

Sets the `AllowNewsAndInterests` policy (`HKLM\SOFTWARE\Policies\Microsoft\Dsh`) after
logging off every user session (`pkg_utils` `logoff`), so the change applies at once.

| Action | Does |
|---|---|
| `on` *(default)* | log off, policy `1`: Widgets allowed |
| `off` | log off, policy `0`: Widgets disabled |

## wim

Component store health of the running Windows (`Repair-WindowsImage -Online`, the
DISM cmdlets).

| Action | Does |
|---|---|
| `check` *(default)* | `CheckHealth`: reads the flag left by the last scan or repair, so it can be stale either way |
| `scan` | `ScanHealth`, the real check; reports the state with the corruption counted in the summary written to `CBS.log` (total, payload files, components) |
| `repair` | `ScanHealth`, then `RestoreHealth` only on a `Repairable` store; fails unless it reaches `Healthy` |

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_wim_check_fail_on_repairable` | `true` | `check` fails on `Repairable`; `false` only reports |
| `win_workman_wim_scan_fail_on_repairable` | `true` | the same for `scan` |
| `win_workman_wim_repair_source` | `""` | local source of `repair`; empty: Windows Update |
| `win_workman_wim_repair_limit_access` | `true` | with a source, `/LimitAccess`: no fallback on Windows Update, so the outcome says whether the source works |

`NonRecoverable` and errors fail whatever the variables say. A source is a path on the
host (no UNC), checked to exist: `wim:C:\Temp\install.wim:1` (or `esd:`, with the
edition index) or a folder with the components (a Windows directory or its WinSxS).
DISM repairs a component only from a copy of the very same version: an image of the
base build lacks what later cumulatives installed.

## ms_account

Blocks or allows Microsoft accounts: `NoConnectedUser=3`
(`HKLM\…\CurrentVersion\Policies\System`: users cannot add or sign in with a Microsoft
account) and `DisableUserAuth=1` (`HKLM\SOFTWARE\Policies\Microsoft\MicrosoftAccount`).

| Action | Does |
|---|---|
| `on` *(default)* | write both values: Microsoft accounts blocked, local accounts only |
| `off` | remove them: Microsoft accounts allowed again |

## chkdsk

Online scan (`chkdsk <X>: /scan`) of `win_workman_chkdsk_volumes` (default `["C"]`), with
the volume in use: no restart, nothing scheduled for the next boot.

| Action | Does |
|---|---|
| `on` *(default)* | scan each volume; findings fixable online (unneeded index links, lost files under temporary folders) are repaired and reported `changed` |

The exit code is a `Volume.RepairStatus` value (the enum of `Repair-Volume`, in the
Storage module's `Volume.cdxml`), not only the classic 0–3. The role classifies it and
cross-checks the dirty bit and `HealthStatus`; `Repair-Volume -Scan`, a second full scan,
decides only an unknown code, a scan still needing a retry after the second attempt, or a
volume contradicting a good code (with no verdict, such a volume counts as needing an
offline fix).

| Exit | `RepairStatus` | Result |
|---|---|---|
| 0, 4 | `NoErrorsFound`, `ScanNoErrorsFound` | ok |
| 1, 2, 5, 16 | `ErrorsFixed`, `MinorErrorsFixedOrCleanup`, `ScanErrorsFoundAndFixedOnline`, `ScanFoundAndFixedLeaks` | changed |
| 3, 6, 7, 13 | `Failed`, `…NeedSpotFix`, `NeedOfflineScanAndFix` | failed |
| 8, 10, 11, 12 | `ScanNeedsRetry`, snapshot errors | scan repeated once, then `Repair-Volume -Scan` decides |

A failure means `chkdsk <X>: /spotfix` (or `/f`) at the next restart; its `msg` names the
volume, the status and the output lines naming a file (they carry its id as
`<0x1,0x24>` in every language). Over SSH, with no console, chkdsk writes in the ANSI
code page, not the OEM one.

## sfc

| Action | Does |
|---|---|
| `on` *(default)* | reboot first if one is pending (`pkg_utils` `pending_restart`, whoever is logged on; skipped with `win_workman_restart: false`), then `sfc /scannow` |

The outcome comes from the `[SR]` lines of this run in `CBS.log` (and in any
`CbsPersist_*.log` it rolled over into), copied to `C:\Windows\Logs\sfc_log_file.log`:
`changed` when files were repaired; failed on "Cannot repair" or "Repair failed", and
when no `[SR]` line was written, meaning sfc did not scan (e.g. a pending repair that
needs a restart). Repairs may need a restart to complete. For severe corruption run
`wim-repair` first.

## logoff

| Action | Does |
|---|---|
| `on` *(default)* | log off every session that carries a user, Active or Disconnected (switched away from, dropped from RDP), and wait for them to end |

`win_workman_logoff_timeout_seconds` (default `300`): the task fails if a session is
left. Session 0 (services, the Ansible SSH connection) and system accounts are left out.

## shutdown

| Action | Does |
|---|---|
| `on` *(default)* | `shutdown /s /f /t <win_workman_shutdown_timeout>`, then wait for the host to go offline; skipped when the connection port does not answer within 5 s |
| `wait` / `no_wait` | as `on`, waiting regardless of `win_workman_shutdown_wait` / never waiting |
| `if-nouser` | as `on` only when no user session is open; otherwise report who is logged on |
| `abort`, `a` | `shutdown /a` (never fails) |

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_shutdown_timeout` | `30` | seconds of notice; the logged-on user can cancel with `shutdown /a` |
| `win_workman_shutdown_wait` | `true` | after `on`/`if-nouser`, wait for the host to go offline and fail if it does not |
| `win_workman_shutdown_wait_timeout` | `900` | seconds the wait allows after the delay |

The wait runs on the controller and watches the port of the Ansible connection
(`ansible_port`, else 22 for SSH, 5986/5985 for WinRM by `ansible_winrm_scheme`) until it
closes: the connection service has stopped, the host is on its way down. ICMP is not
used, since many lab PCs do not answer it. A host going down returns as soon as the port
closes; the timeout is long because Windows installs pending updates in the preshutdown
phase, before sshd stops. A host that stays on fails with `PC05 still answers on port 22
900 s after the shutdown delay: shutdown cancelled (shutdown /a) or stuck`. A
`shutdown.exe` refusing the command fails the task; exit code 1190 (a shutdown already
scheduled) counts as success.

`if-nouser` counts every session with a user, in any state (a locked workstation is
Active, a switched-away or dropped RDP user Disconnected): both may hold unsaved work.
Sessions come from `pkg_utils` `user_sessions` (fact `win_workman_user_sessions`). A host
left on prints `Not shutting down, logged on: LAB_A\student-alice (Active)`. With
autologon a user is always logged on, so `if-nouser` never shuts down.

## ping

| Action | Does |
|---|---|
| `on` *(default)* | `win_ping`: succeeds when the host answers over the Ansible connection |

## wol

Runs on the controller (the dispatcher does not connect to the host for it, so
`wol,chrome` wakes the PC first).

| Action | Does |
|---|---|
| `on` *(default)* | send `win_workman_wol_packets` magic packets to `ansible_mac` (one second apart; a single UDP broadcast is easily lost), to `ansible_broadcast` when set, then wait for `ansible_host:ansible_port` (default 22) |

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_wol_packets` | `3` | magic packets sent |
| `win_workman_wol_timeout` | `300` | seconds to wait for the port |

A host without `ansible_mac` fails with a message that says so. The wait uses port 22
when `ansible_port` is unset, even on WinRM hosts.
