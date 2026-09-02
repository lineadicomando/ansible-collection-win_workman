# Role: sysinfo (System Information)

Collects system information and statistics from Windows workstations and reports them
per host plus as an aggregated summary. Read-only: it never changes state on the target.

Everything is gathered in a **single PowerShell round-trip** and the role does not rely
on gathered facts, so it works under the dispatcher's `gather_facts: false` plays.

---

## Actions

> **Default action: `on`** — bare `sysinfo` collects every configured section.

| Action | Description |
|---|---|
| `on` | Collect the configured sections; prints one line per host plus the OS version distribution |
| `os` | Collect only the `os` section — fast Windows version sweep across a lab |
| `full` | Collect and dump the whole information dictionary for each host |
| `save` | Collect and write an aggregated JSON report to `win_workman_sysinfo_dest` on the controller |

### Section selection

`on` accepts section names as inline arguments, overriding `win_workman_sysinfo_sections`:

```
sysinfo-on-os-disk     # only the os and disk sections
```

Unknown section names fail the task with the list of valid ones.

| Section | Contents |
|---|---|
| `os` | `caption`, `major`, `display_version` (e.g. `25H2`), `build`, `build_number`, `ubr`, `architecture`, `install_date`, `last_boot`, `uptime`, `uptime_days`, `uptime_hours`, `locale` |
| `identity` | `hostname`, `part_of_domain`, `domain`, `workgroup`, `logged_on_user` |
| `hw` | `manufacturer`, `model`, `serial`, `bios_version`, `cpu`, `cpu_cores`, `cpu_threads`, `ram_gb` |
| `disk` | One entry per fixed volume: `device`, `label`, `size_gb`, `free_gb`, `free_pct` |
| `net` | One entry per IP-enabled adapter: `description`, `mac`, `ip`, `gateway`, `dhcp` |

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_sysinfo_sections` | `[os, identity, hw, disk, net]` | Sections collected when the task string carries no explicit section list |
| `win_workman_sysinfo_dest` | `/tmp/win_workman_sysinfo.json` | Controller-side path for the `save` report. Must be **absolute**: `ansible-playbook` chdirs into the playbook directory, so a relative path lands inside the collection |

---

## Facts

The collected dictionary is exposed as the `win_workman_sysinfo` fact, so later tasks and
other roles can branch on it:

```yaml
- name: Only patch machines still on 24H2
  ansible.builtin.include_role:
    name: lineadicomando.win_workman.wu
  when: win_workman_sysinfo.os.display_version != '25H2'
```

---

## Usage

```yaml
# Full inventory of every host
win_workman_tasks:
  - sysinfo

# Windows version sweep across a lab (fastest form)
win_workman_tasks:
  - sysinfo-os

# Only disk usage and network configuration
win_workman_tasks:
  - sysinfo-on-disk-net

# Raw dictionary for a single host
win_workman_tasks:
  - sysinfo-full

# Aggregated JSON report on the controller
win_workman_tasks:
  - sysinfo-save
win_workman_sysinfo_dest: /home/user/lab-report.json
```

---

## Notes

- **Windows version detection.** `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProductName`
  still reports `Windows 10 Pro` on Windows 11 and must not be used. The role reads
  `Win32_OperatingSystem.Caption` for the product name and derives `major` from the build
  number (`>= 22000` means Windows 11). `DisplayVersion` (falling back to `ReleaseId` on
  older builds) carries the feature update — `24H2`, `25H2`, and so on.
- **Failure isolation.** Each section is wrapped in its own `try`/`catch`: a section that
  fails reports an `error` key instead of aborting the whole collection.
- **Aggregated output.** The `OS version distribution` task and the `save` action run
  `run_once` over `ansible_play_hosts`, so they summarise the whole play, not a single host.
