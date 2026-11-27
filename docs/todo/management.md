# Management roles (smaller entries)

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## `autoshutdown`: implement the `nouser` mode

**Priority:** P3 — the first release ships `always` only; nothing depends on `nouser` yet  
**Status:** proposed 2026-10-01 — the role shipped the same day with `always` only

`autoshutdown` registers a scheduled task that shuts the host down at the times
in `win_workman_autoshutdown_schedule`. `win_workman_autoshutdown_mode` is
foreseen with two values, `always` (the default) and `nouser`; the first release
implements `always` and its validation rejects `nouser` with an explicit
message (`win_workman_autoshutdown_modes_implemented` in `vars/main.yaml`,
checked in `tasks/schedule.yaml`).

`nouser` shuts down only when no user session is open, in any state, as
`shutdown-if-nouser` does from the controller. The check has to run on the host,
so the task action becomes a PowerShell command instead of a bare
`shutdown.exe`. Use the same session logic as `pkg_utils`
`tasks/user_sessions.yaml`, so a locked or disconnected session keeps the host
on in both roles.

To decide when implementing: whether a host found busy at the scheduled time
stays on until the next trigger, or the trigger repeats (say every 30 minutes
for a few hours) so the host goes down once the last user leaves. A repetition
needs its own variables and a stop time.

Test on the model of `tests/shutdown_if_nouser.yaml` in the project repo:
Active, Disconnected and no session, asserting the host stays on in the first
two and goes offline in the third.

## `wim-repair`: the folder form of the source, only partly exercised

**Priority:** P3 — the common case (`wim:`) is tested; the folder form has worked once  
**Status:** known gap of `996f5d4` (2026-10-06); folder form first used 2026-11-05

`win_workman_wim_repair_source` takes `wim:<path>:<index>`, `esd:<path>:<index>`
or a local folder holding the components (a mounted Windows directory or its
`WinSxS`). The commit tested invalid and missing sources and full and partial
repairs from `wim:`; `esd:` has still never run.

The folder form ran once, on a production host, on 2026-11-05. A repair from
a `wim:` image of the base build had fixed all but three payloads, which
belonged to component versions installed by later cumulatives and so absent
from the image. The source was a folder `<dir>\Windows\WinSxS\` holding
only the three component directories, copied from a healthy host with the
same versions, plus their three `.manifest` files under `WinSxS\Manifests\`;
`win_workman_wim_repair_source: '<dir>\Windows'`. `RestoreHealth` succeeded
and the following `scan` was `Healthy`, 0 corruptions. Not tested: whether
the manifests are needed, and pointing the source at `WinSxS` instead of
`Windows`. Document the form in the role notes as the way to repair payloads
of cumulative versions, after a run on a test VM.

---

## `scoobe`: confirm that `off` keeps the page away after a cumulative

**Priority:** P3 — a nuisance on the lab PCs after updates, no data at risk  
**Status:** role written 2026-11-04; first test inconclusive

The role exists (`docs/roles/management/scoobe.md`) and writes its three
per-user values correctly: `info`, `off` twice (the second a no-op) and
`off`/`on`/`on` back to the initial state on two lab hosts, then `off` on a
whole lab of 28 hosts, 141 profiles, none unavailable. What is not proven is
that the values stop the page.

Test of 2026-11-04 on two identical lab hosts, one with `off` and one without,
after the preview cumulative KB5127936 (26300.9818, the update after which the
page had been seen on another lab): the page showed on neither at the first
logon of the same domain user. Both ran `UserOOBEBroker.exe`, and the shell
logon task `RemoveTempOOBEUser` (Microsoft-Windows-Shell-Core/Operational,
events 62170/62171) ran with flags `132116` on the host without the values and
`1044` on the one with them. The only difference is bit `0x20000`, so it may
be the "offer SCOOBE" decision that the values switch off. That is an
inference, not documented by Microsoft.

- Watch the host without the values over the following days: if the page
  appears there and never on hosts with `off`, the role is confirmed.
- If it appears on a host with `off`, find which value Windows 26H2 actually
  reads (whether Pro honours the CloudContent user policy is still open).

## `w32time`: a role for the Windows time service

**Priority:** P3 — the labs that needed it were configured by hand with ad hoc PowerShell  
**Status:** proposed 2026-11-11

No role manages the clock. On workgroup hosts Windows polls
`time.windows.com` every 32768 s by default (`SpecialPollInterval`), and
W32Time is trigger-started, so it is
often stopped after boot and the source reads "Local CMOS Clock". Clocks drift
by minutes, and by days on hosts with a failing RTC. W32Time also refuses
corrections larger than `MaxPosPhaseCorrection`/`MaxNegPhaseCorrection`
(15 h on a workgroup host), which then need `Set-Date`. The fix applied so far
by hand: `SpecialPollInterval` 3600, `w32tm /config
/manualpeerlist:<server>,0x9 /syncfromflags:manual /update`, a restart of the
service and `w32tm /resync /force`.

Proposed actions:

- `on`: set the NTP server list, `SpecialPollInterval`, the service to
  automatic start, then restart the service and resync. Idempotent: compares
  the registry values before writing.
- `info`: read only. Reports the source, the stratum, the last successful
  sync, the poll interval, the service state and start mode, and the offset
  measured with `w32tm /stripchart` against the configured server. Also lists
  large clock jumps in the System log since the last boot (Kernel-General
  event 1), which reveal hosts whose RTC stops while they are off.
- `resync`: `w32tm /resync /force`; when the offset exceeds the phase
  correction limit, sets the time from the server first.
- `off`: back to the Windows defaults (`time.windows.com`, poll 32768 as found on
  untouched Windows 11 hosts, trigger start).

Variables: `win_workman_w32time_servers` (default
`["time.windows.com"]`), `win_workman_w32time_poll_interval` (default 3600),
and for `info` an offset threshold above which the host is reported as out of
sync. Domain members take their time from the domain hierarchy (`NT5DS`):
`on` should refuse them unless asked explicitly, so as not to override the
domain controller.

To check when implementing: hosts booted an hour earlier that still showed
"Local CMOS Clock" while the NtpClient logged samples received (event 37) but
no sync (event 35). Find out whether this is normal before the first poll or
a configuration that never syncs, and make `info` say which.

## `veyon`: manage the predefined applications and websites

**Priority:** P3 — the lists are filled by hand today, one teacher profile at a time  
**Status:** proposed 2026-11-21

The *Start application* and *Open website* menus of Veyon Master read two lists:

- the global configuration, `HKLM\SOFTWARE\Veyon Solutions\Veyon\DesktopServices`,
  values `PredefinedApplications` and `PredefinedWebsites`. This is the only list
  the Veyon Configurator shows, and it applies to every user of the master;
- the per-user file `%APPDATA%\Veyon\Config\VeyonMaster.json`, section
  `DesktopServices`, where the entries a teacher adds from the master end up.
  The master rewrites this file when it closes.

An entry visible in the master but missing from the Configurator is therefore a
per-user one, and other accounts on the same teacher PC do not see it. Moving
such an entry to the global list was done by hand: write the value, then remove
the entry from the profile with the master closed.

The registry value is a string `@@JsonValue(<base64>)`, where the base64 encodes
UTF-8 JSON `{"a":[...]}`, the same form as `BuiltinDirectory/NetworkObjects`. Each
item is `{"Name", "Path", "Type", "Uid"}`: `Type` 1 is an application (`Path` is
the command line run on the clients), 2 a website (`Path` is the URL); `Uid` is
a braced GUID. `veyon-cli config get DesktopServices/PredefinedApplications`
reads it back as a plain JSON array.

Proposed:

- variables `win_workman_veyon_predefined_applications` and
  `win_workman_veyon_predefined_websites`, lists of `{name, path}` (default
  undefined: leave the lists alone, so that existing hand-made entries survive);
- written by `veyon-config` on master hosts, with a `Uid` derived from the
  name (a name-based UUID) so that reruns are idempotent and do not reorder
  entries in the menu;
- optionally, `veyon-config` reports the per-user entries it finds under
  `C:\Users\*\AppData\Roaming\Veyon\Config\VeyonMaster.json`, without
  removing them: the master shows both lists, so a per-user copy of a global
  entry appears twice.

To check when implementing: whether the master deduplicates a global and a
per-user entry with the same `Uid`, and whether writing the value with
`veyon-cli config set` accepts a JSON array or needs the import of a whole
configuration file.

## `optimize`: an analysis alone, without defragmenting HDDs

**Priority:** P3 — an improvement; what the role does now is what its docs say  
**Status:** proposed 2026-11-27

`optimize-on` calls `Optimize-Volume` without an operation, so Windows picks
it by media type: retrim on SSDs, analysis *and* defragmentation on HDDs.
`win_workman_optimize_defrag` only adds `-Defrag`, forcing it on SSDs too.
There is no way to learn how fragmented an HDD is without defragmenting it,
which keeps a lab PC busy for long: on a Windows 11 VM whose disk reads as an
HDD (cockpit-fleet's lab, 27 November) a run "without defrag" made eight
passes and took about 9 minutes, fragmentation from 7% to 1%. An assistant
of cockpit-fleet, reading `defrag` as the question of the playbook, had even
offered "analysis only" to the user (the skill of ansible-win_edulab now says
there is none).

What to change: a variable `win_workman_optimize_analyze` (bool, false) that
calls `Optimize-Volume -Analyze` instead, reporting the fragmentation and
changing nothing (`$Ansible.Changed = $false`); or an action `analyze`
beside `on`, which fits the task strings better (`optimize-analyze`). With
it, `meta/mcp.yaml`, `docs/roles/management/optimize.md`, the catalog of
the skill (`tools/fleet_skills.py`) and, in ansible-win_edulab, the row of
`maint_optimize` in its skill and in `docs/playbooks.md`.

Test: on an HDD (or a VM disk read as one), `optimize-analyze` leaves the
fragmentation as it was and reports it; on an SSD it reports the retrim not
needed; `optimize-on` as before.
