# wu — Windows Update

Installs updates through `win_updates` (or the Windows Update Agent for optional
updates), pauses and resumes the update schedule, refreshes the Settings page and
resets a stuck Windows Update state.

## Actions

| Action | Does |
|---|---|
| `run` *(default)* | install the updates of a profile or category list in rounds, rebooting between them, then report: [below](#run) |
| `scan` | install nothing; list what Windows Update offers, regular and optional, with classifications (fact `win_workman_wu_scan`: `build`, `pending`, `optional`; an optional driver can show in both) |
| `sync_ui` | refresh the Windows Update page of Settings: [below](#sync_ui) |
| `reset` | by hand only: reset a stuck Windows Update state: [below](#reset) |
| `pause[-<n>[-d\|w\|m]]` | pause quality and feature updates; bare: `win_workman_wu_pause_months` + `win_workman_wu_pause_days` |
| `off` | `pause` for `win_workman_wu_default_max_pause_days` days |
| `resume`, `on` | remove the pause (UX timestamps, policy pause status and dates) |
| `max_pause_days[-<n>[-d\|w\|m]]` | without args report `FlightSettingsMaxPauseDays`; with a duration set it (the cap of `pause`/`off`); `0` restores `win_workman_wu_default_max_pause_days` |
| `is_paused` | report whether `PausedQualityStatus` is 1 and the expiry (facts `win_workman_wu_is_paused`, `win_workman_wu_pause_expiry`) |
| `policy_standard` | restore the default policy the removed `ansible_managed` profile changed: WaaSMedicSvc manual with default recovery actions, AU `NoAutoUpdate=0`, `NoAUShutdownOption=0`, `AutoInstallMinorUpdates=1`, `UseWUServer=0`; removes `AUOptions`, `NoAutoRebootWithLoggedOnUsers` and every `ExcludeWUDriversInQualityUpdate` |
| `policy_ansible_managed` | removed: fails, pointing to `pause`/`off` and `policy_standard` |

### run

| Task | Installs |
|---|---|
| `wu-run`, `wu` | profile `win_workman_wu_default_profile` (`security`) |
| `wu-run-security` | security, critical, rollups, definitions; BrowseOnly updates skipped |
| `wu-run-full` | `security` plus updates, drivers, featurepacks, servicepacks, tools, BrowseOnly included |
| `wu-run-upgrades` | feature updates, when offered as a regular install |
| `wu-run-<profile>` | any profile of `win_workman_wu_profiles` (`categories` as aliases, `skip_optional`) |
| `wu-run-cat-<a>[+<b>…]` | exactly these categories, BrowseOnly included |
| `wu-run-optional-<a>[+<b>…]` | these categories among the updates offered as optional: [below](#optional-updates) |

Precedence: a `cat-` selector, then `win_workman_wu_categories`, then the profile.
Feature updates are out of `full` on purpose: an hour and several reboots, and they fail
outright on hosts that do not meet the requirements (legacy BIOS/MBR, no TPM).

Category aliases (task strings cannot carry spaces): `security` (Security Updates, the
monthly cumulative), `critical`, `rollups` (Update Rollups), `definitions` (Defender),
`updates` (non-security fixes; the preview cumulatives carry it too but only
`wu-run-optional-updates` reaches them), `drivers`, `featurepacks`, `servicepacks`,
`tools`, `upgrades` (feature updates), `application`, `connectors`, `devkits`,
`guidance`.

**Rounds and reboots.** `run` first reboots if a reboot is already pending
(`pkg_utils` `pending_restart`: servicing Windows staged on its own). Each round installs
with `reboot: false`, then the `pkg_utils` restart follows when Windows asks for one and
a new round searches again, so updates that appear once another is in place (servicing
stack, then cumulative) go in the same run. A round that needs no restart ends the run
(WUA offers some updates, such as the Windows Security platform, at every search);
`win_workman_wu_max_rounds` caps them. The restart is not left to `win_updates`: its
reboot is over at the logon screen, but after a cumulative Windows may reboot again on
its own (TrustedInstaller, twice in 13 minutes on a test VM) while `win_updates` is
already searching, and the host drops as unreachable with the report lost. The
`pkg_utils` restart waits for servicing to be idle and rides out that reboot, for up to
`win_workman_wu_reboot_timeout`. With `win_workman_restart: false` nothing reboots, one
round runs, and the report says whether a reboot is still required.

**Report.** `win_updates` reports `ok` both when nothing was found and when a reboot
finished installing updates Windows had staged, so each host prints:

```
Selection: profile security (Security Updates, Critical Updates, Update Rollups, Definition Updates), optional updates skipped
Build: 25H2 26200.9309 -> 26200.9457
Updates: 2 found, 1 installed, 1 failed
[installed] 2026-09 Cumulative Update (KB5129195)
[failed 0x80240020] ... - WU_E_NO_INTERACTIVE_USER
Pause had expired before the run: Windows may have installed updates on its own
```

Fact `win_workman_wu_report`: `build_before`, `build_after`, `found`, `installed`,
`failed`, `reboot_required`, `reboots`, `rounds`, `rounds_exhausted`, `updates`,
`filtered`. It is printed even when the install fails, and the host fails when single
updates fail although `win_updates` succeeded. After a `run` that installed something,
`sync_ui` runs (unless `win_workman_wu_sync_ui: false`); a failed refresh there is only
reported.

### Optional updates

Windows Update publishes some updates with `DeploymentAction=OptionalInstallation`;
Settings shows them as a banner waiting for the user (`2026-09 Aggiornamento della
versione di anteprima (KB5124010) (26200.9550) è disponibile. Scarica e installa`). Seen
in the labs: the monthly non-security **preview** cumulative ("D week", `Updates`);
**feature updates** (on 2026-10-02 26H2 was offered as optional to every 25H2 host of a
lab, `Upgrades`); optional **drivers**.

No profile or `cat-` reaches them: `win_updates` searches with the fixed query
`IsInstalled = 0`, which implies `DeploymentAction='Installation'`, so they show neither
as found nor as filtered out, and `wu-run-upgrades` reports `0 found`. No option of
`win_updates` changes the query; `skip_optional` is about `BrowseOnly`, which these are
not.

`wu-run-optional-<category>` searches with `DeploymentAction='OptionalInstallation'`,
keeps the listed classifications, and downloads and installs through the Windows Update
Agent as SYSTEM (become, async up to `win_workman_wu_optional_timeout`): the agent
refuses both from a network logon. Rounds, restarts and report as above; the optional
updates left out are listed under "Filtered out". A category is required (the set mixes
feature updates and drivers). `wu-run-optional-upgrades` stops at the feature update,
keeping the revision (26200.9457 became 26300.9457 on a lab): chain `wu-run` for the
cumulative of the new release, or use `wu-run-optional-upgrades+updates` (feature update,
then the new release's preview in the next round).

SYSTEM runs the become wrapper in `ansible_remote_tmp`: with the ACL Ansible creates it
with, the wrapper failed with `CompileAssemblyFromSource ... path not found`; the
dispatcher now fixes the ACL ([pkg_utils](../core/pkg_utils.md#remote-temporary-directory)).

Leaving the preview out is harmless and what Microsoft intends without an update
policy: *Enable optional updates* (`AllowOptionalContent`) is not configured by default,
and the preview content ships in the next month's security cumulative. Setting
`TargetReleaseVersion` to `26H2` on a 25H2 host (with or without `ProductVersion`) does
not bring the feature update to `wu-run-upgrades`: it hid it from both searches until the
policy was removed.

### sync_ui

Settings reads the Update Orchestrator store (`C:\ProgramData\USOPrivate\UpdateStore`),
not the Windows Update Agent `run` installs through, and that store changes only with an
orchestrator scan. After a `run` the page keeps Windows' last own scan: an installed
update still offered (*Scarica e installa*), or failed (*Aggiornamenti non riusciti*, "no
updates published for this edition") once the orchestrator tries it. Seen on 27 PCs on
2026-11-02 after `wu-run-optional-updates`.

`wu-sync_ui` runs `UsoClient StartInteractiveScan` in the logged-on user's session
through a temporary scheduled task and waits up to `win_workman_wu_sync_ui_timeout` for
a newer `LastSearchSuccessDate`. Only that works: `UsoClient StartScan` from SSH, the
same as SYSTEM, and the *UpdateOrchestrator\Schedule Scan* task end without error and
record no scan (22 hosts). With nobody logged on the host is skipped (the next automatic
scan fixes the store). Fact `win_workman_wu_sync_ui`: `user`, `before`, `after`,
`synced`, `skipped`, `message`; the stand-alone action fails when no new scan shows up.

### reset

For a state wrong in itself, not a lagging page. Seen on two hosts on 2026-10-21 after a
cumulative installed by hand with DISM: history entries left in progress with
`0x80242014`, `RebootRequired` set, a reboot asked at every logon that changes nothing, a
"versione di ripristino" of an older release offered.

It refuses while `TiWorker` runs (`Microsoft.Update.Installer.IsBusy` cannot be read
from a network logon: `E_ACCESSDENIED`). Otherwise it closes Settings (it holds the
store open), stops `wuauserv`, `bits`, `cryptsvc`, `usosvc` (again before each rename:
`wuauserv` and `usosvc` are trigger-started), renames `SoftwareDistribution`,
`System32\catroot2` and `USOPrivate\UpdateStore` with `.wu-reset-<stamp>` (kept as a way
back; copies of an earlier reset deleted), deletes `RebootRequired` (read first:
`wuauserv` drops it when it stops), starts the services whatever happened, then runs
`sync_ui` (not fatal) and `scan`. Fact `win_workman_wu_reset`: `stamp`, `renamed`,
`removed_backups`, `reboot_required_cleared`, `services`. It loses the download cache
and the history in Settings, so `run` never calls it.

### Pause durations and the 35-day limit

| Suffix | `pause` | `max_pause_days` |
|---|---|---|
| none, `d`, `day`, `days` | days | days |
| `w`, `week`, `weeks` | weeks | weeks × 7 |
| `m`, `month`, `months` | calendar months | months × 31 days |

`pause` computes the end on the host in local time, from now to the same time of day:
`wu-pause-1-m` on 10 November ends on 10 December, on 31 January at the end of February,
as the Settings date picker would. A pause longer than `FlightSettingsMaxPauseDays`
(absent: `win_workman_wu_default_max_pause_days`) is shortened to it, with a message. A
month counts 31 days in the cap, so `max_pause_days-6-m` never shortens a later
`pause-6-m`. Up to v0.5.2 a month counted 28 days for both (`wu-pause-3-m` now pauses 89
to 92 days, not 84).

On 25H2 (26200) and 26H2 (26300) Settings has a date picker ("Sospendi aggiornamenti →
Seleziona data") that ignores `FlightSettingsMaxPauseDays` and stops at 35 days, even
with `max_pause_days-6-m`, Settings reopened and `UsoSvc` restarted. The picker follows
the `SetMaxPauseDays` policy (`HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate`,
CSP `Update/SetMaxPauseDays`), which accepts 1–35 and can only shorten it (14 cuts it to
14; 168 is discarded for 35). A pause written to the registry is still accepted beyond
35 days, so `max_pause_days` now only caps this role's `pause`/`off`:

```yaml
win_workman_tasks:
  - wu-max_pause_days-6-m   # cap: 186 days
  - wu-pause-6-m            # until the same day, six months from today
```

Settings then shows "Gli aggiornamenti sono stati sospesi fino al …" with that date and
"Riprendi aggiornamenti" works; the picker still offers only 35 days, so only the role
can extend it. Microsoft does not document such pauses, and nobody has checked one holds
for its full length.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_wu_pause_days` / `_pause_months` | `7` / `0` | duration of a bare `pause` |
| `win_workman_wu_default_max_pause_days` | `35` | duration of `off`; cap when `FlightSettingsMaxPauseDays` is absent; target of `max_pause_days-0` |
| `win_workman_wu_default_profile` | `security` | profile of a bare `run` |
| `win_workman_wu_profiles` | `security`, `full`, `upgrades` | profiles: `categories` (aliases), `skip_optional` |
| `win_workman_wu_categories` | `[]` | replaces the profile's categories |
| `win_workman_restart` | `true` | `run` may reboot |
| `win_workman_wu_reboot_timeout` | `1800` | seconds `run` waits after each restart |
| `win_workman_wu_max_rounds` | `5` | install rounds per `run` |
| `win_workman_wu_optional_timeout` | `7200` | seconds one round of `run-optional-…` may take |
| `win_workman_wu_sync_ui` | `true` | `sync_ui` after a `run` that installed something |
| `win_workman_wu_sync_ui_timeout` | `300` | seconds `sync_ui` waits for the new scan |
| `win_workman_wu_unpause` | `false` | `resume` before `run`; the host stays unpaused afterwards |

## Notes

- The report lines "Paused before the run" / "Pause had expired before the run" read
  the pause state as of after the run (`build_info` runs again at the end and overwrites
  it): after `win_workman_wu_unpause` they do not show.
