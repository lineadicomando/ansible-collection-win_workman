# Role: wu (Windows Update)

Manages Windows Update behaviour: run pending updates, pause/resume the update schedule,
and inspect or adjust the maximum allowed pause duration.

---

## Actions

> **Default action: `run`** — bare `wu` (no action token) runs pending updates with the default profile (`security`).

| Action | Description |
|---|---|
| `run` | Install the updates selected by a profile or a category list (see below), rebooting and searching again until none is left, then report the outcome |
| `scan` | Read-only: list what Windows Update offers, both the updates `run` installs and the optional ones |
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
| `wu-run-full` | `security` plus updates, drivers, featurepacks, servicepacks, tools, BrowseOnly updates included (not the preview cumulatives, see below) |
| `wu-run-upgrades` | feature updates only (e.g. 25H2 -> 26H2), when Windows Update offers them as a regular install |
| `wu-run-cat-<a>[+<b>...]` | exactly the listed categories, BrowseOnly updates included |
| `wu-run-optional-<a>[+<b>...]` | the listed categories among the updates offered as optional: preview cumulatives, optional feature updates and drivers (see below) |

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
| `updates` | Updates (non-security fixes; the preview cumulatives carry it too, but only `wu-run-optional-updates` reaches them, see below) |
| `drivers` | Drivers |
| `featurepacks`, `servicepacks`, `tools` | Feature Packs, Service Packs, Tools |
| `upgrades` | Upgrades (feature updates) |
| `application`, `connectors`, `devkits`, `guidance` | the remaining WUA classifications |

Precedence: a `cat-` selector in the task string, then `win_workman_wu_categories`,
then the profile. Profiles are data in `win_workman_wu_profiles`, so an
inventory can add its own (`categories` as aliases, `skip_optional` as bool)
and call it as `wu-run-<name>`.

### Optional updates: `wu-run-optional-<category>`

Windows Update publishes some updates with `DeploymentAction` =
`OptionalInstallation`. Settings shows them as a banner that waits for the user:

```
2026-09 Aggiornamento della versione di anteprima (KB5124010) (26200.9550) è disponibile.   Scarica e installa
```

Three kinds have been seen in the labs:

- the monthly **non-security preview** cumulative (the "D week" release, fourth
  week of the month), in the `Updates` classification;
- **feature updates**: on 2026-10-02 "Windows 11, version 26H2" was offered to
  every 25H2 host of ario_info as optional, in `Upgrades`;
- optional **drivers**.

No profile and no `wu-run-cat-...` reaches them. win_updates searches with the
fixed query `IsInstalled = 0`, and a WUA query that does not name a
`DeploymentAction` implies `DeploymentAction='Installation'`: the optional
updates are not returned at all, so they show up neither among the found updates
nor under "Filtered out", and `wu-run-upgrades` reports `0 found`. No option of
win_updates changes the query. `skip_optional` is not involved either: it drops
`BrowseOnly` updates, and these are not `BrowseOnly`.

`wu-run-optional-<category>[+<category>...]` installs them. It searches with
`DeploymentAction='OptionalInstallation'`, keeps the updates in the listed
classifications (the same aliases as `cat-`), then downloads and installs
through the Windows Update Agent as SYSTEM, since the agent refuses both from a
network logon. Rounds, restarts and the report are those of every `run`; the
optional updates left out by the categories are listed under "Filtered out".

| Task | Installs |
|---|---|
| `wu-run-optional-upgrades` | the optional feature update |
| `wu-run-optional-updates` | the preview cumulative |
| `wu-run-optional-drivers` | optional drivers |
| `wu-run-optional-upgrades+updates` | feature update, then the preview cumulative of the new release in the following round |

A category is required: a bare `wu-run-optional` is rejected, because the
optional set mixes feature updates with drivers. `wu-run-optional-upgrades`
alone stops at the feature update, keeping the revision the host had
(26200.9457 became 26300.9457 on ario_info); chain `wu-run` after it for the
cumulative of the new release.

Leaving the preview out is harmless, and is what Microsoft intends for devices
without an update policy: the **Enable optional updates** policy
(`AllowOptionalContent` under
`HKLM\Software\Policies\Microsoft\Windows\WindowsUpdate`) is not configured by
default, and the preview content ships in the following month's security
cumulative, which a plain `run` installs.

Setting the `TargetReleaseVersion` policy does not bring a feature update in
reach of `wu-run-upgrades`: set to `26H2` on a 25H2 host, with or without
`ProductVersion`, it hid the update from both searches until the policy was
removed.

The install task runs with `ansible_remote_tmp` moved to `C:\Windows\Temp`.
Ansible creates the inventory's remote tmp (`C:\Windows\Temp\ansible`) with
access for the connecting user only, and the become wrapper, running as SYSTEM,
fails there with `CompileAssemblyFromSource ... path not found` before the
script starts.

### `scan`

`wu-scan` installs nothing and prints, per host, the two lists the Windows
Update Agent keeps apart, each update with its classification:

```
Build: 25H2 26200.9457
Pending (wu-run): 1
[Definition Updates] Aggiornamento dell'intelligence sulla sicurezza per Microsoft Defender Antivirus ...
Optional (wu-run-optional-<category>): 1
[Upgrades] Windows 11, version 26H2
```

The same data is left in the `win_workman_wu_scan` fact (`build`, `pending`,
`optional`). An optional driver can show in both lists.

### `run` reboots

`run` first finishes any servicing already pending on the host (updates Windows
staged on its own) with the `pkg_utils` restart. Then it installs in rounds:
win_updates installs with `reboot: false`, the `pkg_utils` restart follows when
Windows asks for one, and a new round searches again, so updates that only show
up once another is in place (servicing stack, then cumulative) go in the same
run. A round that needs no restart ends the run (WUA offers some updates, such
as the Windows Security platform, again at every search), and
`win_workman_wu_max_rounds` caps the rounds.

The restart is not left to win_updates on purpose. Its reboot is over as soon as
the logon screen is up, but after a cumulative update Windows may reboot again on
its own right after (TrustedInstaller, twice in 13 minutes on a test VM), while
win_updates is already searching: the host drops as unreachable and the report
is lost. The `pkg_utils` restart waits until component servicing is idle and
rides out a reboot that happens meanwhile, for up to
`win_workman_wu_reboot_timeout` in `run`, longer than the default
`win_workman_restart_timeout`. With `win_workman_restart: false` nothing
reboots, a single round runs and the report says whether a reboot is still
required.

### `run` report

win_updates reports `ok` both when nothing was found and when a reboot finished
installing updates Windows had staged on its own, so the recap alone cannot say
what happened. At the end of `run` each host prints:

```
Selection: profile security (Security Updates, Critical Updates, Update Rollups, Definition Updates), optional updates skipped
Build: 25H2 26200.9309 -> 26200.9457
Updates: 2 found, 1 installed, 1 failed
[installed] 2026-09 Cumulative Update (KB5129195)
[failed 0x80240020] ... - WU_E_NO_INTERACTIVE_USER
Pause had expired before the run: Windows may have installed updates on its own
```

The same data is left in the `win_workman_wu_report` fact (`build_before`,
`build_after`, `found`, `installed`, `failed`, `reboot_required`, `reboots`, `rounds`,
`rounds_exhausted`, `updates`,
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
| `win_workman_wu_reboot_timeout` | `1800` | Seconds `run` waits after each restart for the host to be back with servicing idle |
| `win_workman_wu_max_rounds` | `5` | Install rounds in one `run`, each followed by a restart when needed |
| `win_workman_wu_optional_timeout` | `7200` | Seconds `wu-run-optional-...` may take to download and install in one round |
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

# Upgrade when the feature update is offered as optional, then its cumulative
win_workman_tasks:
  - wu-run-optional-upgrades
  - wu-run

# Install the monthly preview cumulative
win_workman_tasks:
  - wu-run-optional-updates

# List what Windows Update offers, installing nothing
win_workman_tasks:
  - wu-scan

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
