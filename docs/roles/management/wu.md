# Role: wu (Windows Update)

Manages Windows Update behaviour: run pending updates, pause/resume the update schedule,
and inspect or adjust the maximum allowed pause duration.

---

## Actions

> **Default action: `run`** — bare `wu` (no action token) runs pending updates with the default profile (`security`).

| Action | Description |
|---|---|
| `run` | Search, download, and install the updates selected by a profile or a category list (see below); reboots if required, then reports the outcome |
| `on` | Resume Windows Update (alias for `resume`) |
| `off` | Pause Windows Update at maximum duration (alias for `pause` at max days) |
| `pause` | Pause quality and feature updates for `win_workman_wu_pause_days` days |
| `resume` | Remove the update pause (resume immediately) |
| `max_pause_days` | Read or set `FlightSettingsMaxPauseDays`; without args reports the current value, with a duration sets the cap |
| `is_paused` | Report whether updates are paused and, if so, the expiry timestamp |
| `policy_standard` | Restore standard Windows Update Group Policy (reverts Ansible-managed policy) |
| `policy_ansible_managed` | *(removed)* Raises an error; use `pause` or `off` instead |

### `run` selection

| Task | Installs |
|---|---|
| `wu-run`, `wu` | the `win_workman_wu_default_profile` profile (`security`) |
| `wu-run-security` | security, critical, rollups, definitions; optional (BrowseOnly) updates skipped |
| `wu-run-full` | `security` plus updates, drivers, featurepacks, servicepacks, tools, optional updates included |
| `wu-run-upgrades` | feature updates only (e.g. 25H2 -> 26H2) |
| `wu-run-cat-<a>[+<b>...]` | exactly the listed categories, optional updates included |

Feature updates are left out of `full` on purpose: an upgrade takes an hour and
several reboots, and fails outright on hosts that do not meet the requirements
(legacy BIOS/MBR, no TPM). They run only when asked for by name.

Category aliases, since task strings cannot carry spaces:

| Alias | Windows Update classification |
|---|---|
| `security` | Security Updates (the monthly cumulative on Windows 11) |
| `critical` | Critical Updates |
| `rollups` | Update Rollups |
| `definitions` | Definition Updates (Microsoft Defender) |
| `updates` | Updates (non-security fixes, preview cumulatives) |
| `drivers` | Drivers |
| `featurepacks`, `servicepacks`, `tools` | Feature Packs, Service Packs, Tools |
| `upgrades` | Upgrades (feature updates) |
| `application`, `connectors`, `devkits`, `guidance` | the remaining WUA classifications |

Precedence: a `cat-` selector in the task string, then `win_workman_wu_categories`,
then the profile. Profiles are data in `win_workman_wu_profiles`, so an
inventory can add its own (`categories` as aliases, `skip_optional` as bool)
and call it as `wu-run-<name>`.

### `run` report

win_updates reports `ok` both when nothing was found and when a reboot finished
installing updates Windows had staged on its own, so the recap alone cannot say
what happened. At the end of `run` each host prints:

```
Selection: profile security (Security Updates, Critical Updates, Update Rollups, Definition Updates), optional updates skipped
Build: 25H2 26200.9457 -> 26200.9550
Updates: 2 found, 1 installed, 1 failed
[installed] 2026-09 Cumulative Update (KB5124010)
[failed 0x80240020] ... - WU_E_NO_INTERACTIVE_USER
Pause had expired before the run: Windows may have installed updates on its own
```

The same data is left in the `win_workman_wu_report` fact (`build_before`,
`build_after`, `found`, `installed`, `failed`, `reboot_required`, `updates`,
`filtered`). The report is printed even when the install task fails, and the host
is marked failed when single updates fail although win_updates itself succeeded.

### `max_pause_days` duration syntax

An optional unit suffix controls how the numeric argument is interpreted:

| Suffix | Meaning |
|---|---|
| *(omitted)* or `d` / `day` / `days` | days |
| `w` / `week` / `weeks` | weeks (× 7) |
| `m` / `month` / `months` | months (× 28) |

Passing `0` resets the cap to the role default (`win_workman_wu_default_max_pause_days`).

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_wu_pause_days` | `7` | Days to pause updates when using `pause` |
| `win_workman_wu_default_max_pause_days` | `35` | Maximum pause cap; used by `off` and as reset target for `max_pause_days 0` |
| `win_workman_wu_default_profile` | `security` | Profile used by a bare `wu-run` |
| `win_workman_wu_profiles` | `security`, `full`, `upgrades` | Profiles for `wu-run-<name>`: `categories` (aliases) and `skip_optional` |
| `win_workman_wu_categories` | `[]` | When set, replaces the categories of the chosen profile |
| `win_workman_restart` | `true` | Allow reboot when `run` requires it |
| `win_workman_wu_unpause` | `false` | Resume updates before running `run` (useful when updates are kept paused between runs) |

---

## Usage

```yaml
# Install security updates, rebooting if needed
win_workman_tasks:
  - wu-run

# Install everything except feature updates
win_workman_tasks:
  - wu-run-full

# Upgrade to the next Windows release
win_workman_tasks:
  - wu-run-upgrades

# Only drivers and Defender definitions
win_workman_tasks:
  - wu-run-cat-drivers+definitions

# Install updates even when updates are kept paused
win_workman_tasks:
  - wu-run
win_workman_wu_unpause: true

# Pause updates for 14 days
win_workman_tasks:
  - wu-pause-14

# Pause updates for 3 weeks (inline duration)
win_workman_tasks:
  - wu-pause-3-w

# Resume paused updates
win_workman_tasks:
  - wu-resume

# Read the current FlightSettingsMaxPauseDays cap
win_workman_tasks:
  - wu-max_pause_days

# Raise the cap to 90 days
win_workman_tasks:
  - wu-max_pause_days-90

# Check whether updates are currently paused
win_workman_tasks:
  - wu-is_paused
```
