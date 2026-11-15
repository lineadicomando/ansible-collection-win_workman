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
