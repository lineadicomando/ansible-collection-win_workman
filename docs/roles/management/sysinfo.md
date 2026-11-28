# sysinfo — System information

Collects system information from Windows hosts and reports one line per host plus
lab-wide summaries. Read-only. Everything is gathered in a single PowerShell
round-trip without gathered facts, so it works under the dispatcher's
`gather_facts: false` plays.

## Actions

| Action | Does |
|---|---|
| `on[-<section>...]` (default) | Collect the sections (`win_workman_sysinfo_sections`, or those named in the task string); print a line per host, the OS version distribution and the upgrade hard block distribution |
| `os` | As `on`, `os` section only: fast Windows version sweep |
| `security` | As `on`, `security` section only |
| `wu` | As `on`, `wu` section only |
| `full[-<section>...]` | Collect and dump the whole dictionary per host |
| `save[-<section>...]` | Collect and write `{host: dict}` as JSON to `win_workman_sysinfo_dest` on the controller |

Section arguments (`sysinfo-on-os-disk`) replace `win_workman_sysinfo_sections`; an
unknown name fails with the list of valid ones. They win over the fixed section of
`os`/`security`/`wu` too: `sysinfo-os-disk` collects `disk` only.

| Section | Contents |
|---|---|
| `os` | `caption`, `major`, `display_version` (`25H2`), `build` (`<build>.<ubr>`), `build_number`, `ubr`, `architecture`, `install_date`, `last_boot`, `uptime` (`2d 3h` or `3h 12m`), `uptime_days`, `uptime_hours`, `locale` |
| `identity` | `hostname`, `part_of_domain`, `domain`, `workgroup`, `logged_on_user` |
| `hw` | `manufacturer`, `model`, `serial`, `bios_version`, `cpu`, `cpu_cores`, `cpu_threads`, `ram_gb` |
| `disk` | Per fixed volume: `device`, `label`, `size_gb`, `free_gb`, `free_pct` |
| `net` | Per IP-enabled adapter: `description`, `mac`, `ip` (first IPv4), `gateway`, `dhcp` |
| `security` | `tpm_present/ready/enabled/activated/owned`, `tpm_restart_pending`, `tpm_spec`, `tpm_manufacturer`, `tpm_firmware`, `tpm_device`, `tpm_first_install`, `secure_boot` (`enabled`/`disabled`/`unavailable`), `firmware` (`UEFI`/`Legacy BIOS`), `partition_style` of C: |
| `wu` | `target_release`, `target_release_set`, `no_auto_update`, `use_wu_server`, `wsus_server`, `defer_feature_days`, `branch_readiness`, `feature_paused_until`, `upgrade_blocks` (`{release: "UpgEx[: RedReason]"}`), `compat_report`, `compat_report_date`, `compat_hard_blocks`, `compat_hard_blocks_text` |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_sysinfo_sections` | `[os, identity, hw, disk, net, wu]` | Sections when the task string names none |
| `win_workman_sysinfo_dest` | `/tmp/win_workman_sysinfo.json` | Controller path for `save`. Must be absolute: `ansible-playbook` chdirs into the playbook directory, so a relative path lands inside the collection |

The result is the fact `win_workman_sysinfo` (`win_workman_sysinfo.os.display_version`
and so on), for later tasks to branch on.

## Notes

- `security` is opt-in: `Get-Tpm` and `Get-Disk` load their modules and cost about a
  second per host, doubling a plain `sysinfo` across a lab. It needs an elevated
  session; without it the section degrades to an `error` entry.
- `Get-Tpm` is the only source of `RestartPending` (a TPM just enabled in firmware
  needing a reboot). `tpm_first_install` (`DEVPKEY_Device_FirstInstallDate`) dates
  the BIOS change that enabled the TPM. Windows 11 needs a Secure Boot capable
  machine, not Secure Boot on: `Confirm-SecureBootUEFI` throwing is read as legacy BIOS.
- `wu`: the appraiser indicators (`UpgEx`/`RedReason` under
  `TargetVersionUpgradeExperienceIndicators`) are stored values, not recomputed on
  read: after a BIOS change they report the old reason until the Microsoft
  Compatibility Appraiser task runs again. The hard blocks come from the newest
  `C:\$WINDOWS.~BT\Sources\Panther\CompatData_*.xml`, written by Setup on each
  upgrade attempt. `sysinfo-on-os-security-wu` shows why a feature update is not
  offered.
- Windows version: `CurrentVersion\ProductName` still says `Windows 10 Pro` on
  Windows 11. The role uses `Win32_OperatingSystem.Caption` and derives `major` from
  the build (`>= 22000` is 11); `DisplayVersion`, falling back to `ReleaseId`.
- Each section has its own `try`/`catch`: a failing one reports `error`, the rest
  is collected.
- Traps in the collector, kept in comments: sections are inline `if`/`try` blocks,
  not functions (under `win_powershell` a function's `$script:` scope is not the one
  holding `$result`, yielding `{}`); `upgrade_blocks` is a flat string map because
  deeper hashtables serialise as `OrderedDictionary` strings; the section is `wu`,
  not `update`, because Jinja resolves `.update` to `dict.update`.
