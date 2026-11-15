# `wu` feature update reporting

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## `wu`: a feature update that does not apply is reported as installed

**Priority:** P1 — a correctness bug in the report, and five needless restarts of a lab host  
**Status:** found 2026-10-10 on a production host; cause read in the code and in the host's logs, fix not written

`wu-run-upgrades` reported a feature update as installed while Windows Setup
had refused it, and restarted the host five times before giving up with a
message that suggests running it again. The run ended `failed=0`, exit code 0.

The entry is written to be worked without the host: it is being repaired
and will not be in this state again. Everything quoted below was read on
2026-10-10; the evidence is saved in the project repo (see **Evidence**).

### What the role printed

```
Selection: profile upgrades (Upgrades)
Build: 25H2 26200.6899
Updates: 1 found, 1 installed, 0 failed
[installed] Windows 11, version 25H2
Restarted 5 time(s) to complete the install, 5 install round(s)
Stopped after 5 rounds (win_workman_wu_max_rounds): more updates may be waiting, run wu-run again
```

The `Build:` line shows a single value because the build did not change, which
is the only hint in the report that nothing was applied.

### What happened on the host

The run was `wu-run-upgrades` with `win_workman_wu_reboot_timeout: 3600`,
started at 10:36 (controller clock; the host clock ran about 3 min 45 s behind,
and the times below are the host's).

| Host time | Event |
| --- | --- |
| 10:32 | Download starts (WUA event 44) |
| 10:41:08–10:41:25 | First `SetupHost` session, `SetupResult` 0x0 (preparation) |
| 10:45:25 | Round 1: `AGENT_INSTALLING_STARTED`, caller `ansible.windows.win_updates` |
| 10:59:46 | Second `SetupHost` session |
| 11:00:30 | `MigChoice: Selected install choice is not available.` → `0xC1900204` |
| 11:00:45 | `CSetupHost::Execute(564): Result = 0xC1900204` |
| 11:01:31 | Boot (restart of round 1) |
| 11:03:13 | Round 2: `AGENT_INSTALLING_STARTED` |
| 11:03:48 | Boot |
| 11:05:31 | Round 3: `AGENT_INSTALLING_STARTED` |
| 11:06:07 | Boot |
| 11:07:52 | Round 4: `AGENT_INSTALLING_STARTED` |
| 11:08:27 | Boot |
| 11:10:11 | Round 5: `AGENT_INSTALLING_STARTED` |
| 11:10:48 | Boot |

Facts that matter for the fix:

- **Setup failed before the first restart**, in the downlevel (online) phase,
  while `win_updates` was still inside its install call. The restart of round 1
  completed nothing.
- **`win_updates` returned the update as installed with `reboot_required` in
  every round**, never with a `failure_hresult_code`: the merged result counts
  1 installed and 0 failed, and the role restarted after each round. The
  per-round results are not in the run log (no `-v`), so the exact fields
  `win_updates` returned are inferred from the role's behaviour — reproduce
  with `-vvv` or a `debug` on `win_workman_wu_round` before fixing.
- **Rounds 2 to 5 did not run Setup at all.** `setupact.log` holds two
  `SetupHost` sessions only, both before 11:01; each later round lasted about
  35 seconds between "installing started" and the boot. WUA answered
  "succeeded, reboot required" for an update whose install had already failed.
- **No WUA failure event.** The System log has event 43 (installation started)
  five times for `Windows 11, version 25H2` and neither a 19 (success) nor a 20
  (failure). `ReportingEvents.log` likewise has five `AGENT_INSTALLING_STARTED`
  lines and nothing after them. The failure is visible only in Setup's own logs.
- **After the run the update was gone from the search.** `wu-scan` at 11:17
  (controller) reported `Pending: 0`, `Optional: 0`; at 10:34, before the run,
  `wu-run` listed `Windows 11, version 25H2` among the filtered updates. So "run
  wu-run again", as the report suggests, would have found nothing.
- The host was left healthy: same build, no `C:\Windows.old`, no pending
  reboot, `C:\$WINDOWS.~BT` present.

### Why Setup refused it (context, not the bug)

`CompatData_2026_10_10_11_00_30_*.xml` carries a hard block
`HardwareType="Setup_HostIsNewer"`, and `setupact.log` says why:

```
Host OS version: 10.0.26200.0
Target OS version: 10.0.26100.9457
MigChoice: After Migration Filter -> [CleanInstall]
MigChoice: Selected install choice is not available.
```

The image Windows Update downloads as "Windows 11, version 25H2" is a 26100
image (25H2 is 24H2 plus an enablement package). The host had been moved to
25H2 half an hour earlier with the KB5054156 enablement package, from
`26100.6899` to `26200.6899`, so Setup saw a host newer than its target, kept
only the clean-install choice and stopped. Had the feature update been
installed while the host was still on `26100.6899`, the target would have been
newer.

Why Windows Update offered a full setup instead of a cumulative: the component
store of the host was corrupted (`DISM /CheckHealth`: "The component store is
repairable"; last cumulative installed on 2025-07-11, `26100.6899`; a
`Package_for_RollupFix~26100.1742.1.10` left `Staged` since 2024). It is the
same corrupted-store state met on other lab hosts. On such
a host a plain `wu-run` reports `0 found` and lists `Windows 11, version 2xH2`
under "Filtered out", on 24H2 and on 25H2 alike: that pair is a recognisable
signature (see point 4 below).

### Where it goes wrong in the role

- `roles/wu/tasks/run_round.yaml` — "Decide whether another round is needed"
  sets `win_workman_wu_done` from `reboot_required` alone. A round that
  installs the very same update as the round before, with the build unchanged
  across the restart, is not told apart from servicing stack → cumulative.
- `roles/wu/tasks/act_run.yaml` — "Merge the install rounds" combines the
  `updates` dicts of all rounds by update id and counts as installed whatever
  has `installed: true` and no `failure_hresult_code`. Five rounds on one
  update merge into "1 installed".
- `roles/wu/tasks/run_report.yaml` — prints `[installed]` from that field, and
  on `rounds_exhausted` says "more updates may be waiting, run wu-run again",
  which is wrong when every round installed the same update.
- "Fail if some updates failed to install" in `act_run.yaml` looks at
  `failed` only, so the run ends green.

### What to change

1. **Detect an install that did not apply.** After the restart of a round, read
   the build (`build_info.yaml` already does it). If the round reported updates
   installed with `reboot_required`, the build is unchanged and the next search
   finds the same update id again — or, for the `upgrades` selection, the build
   is simply unchanged — stop the rounds and mark that update as failed
   ("reported installed, not applied") instead of installing it again. One
   repeat is enough to decide; do not restart again for it.
2. **Fetch the real error.** For a feature update the reason is in
   `C:\$WINDOWS.~BT\Sources\Panther\setuperr.log` (last `Result = 0x…` line) and
   in the newest `CompatData_*.xml` there (`BlockingType="Hard"` items, here
   `Setup_HostIsNewer`). `HKLM\SYSTEM\Setup\MoSetup\Volatile` was read during
   the run (`SetupProgress` 20, then 100) but is not a result code. Put the
   HRESULT and the hard-block names in the report line of the update.
3. **Fail the run** when an update is marked this way, as for
   `failure_hresult_code`, and drop the "run wu-run again" line in that case.
4. **Optional, cheap:** when a `wu-run` with a profile that excludes `Upgrades`
   finds nothing and the filtered list holds a `Windows 11, version …` whose
   release is the one the host already runs, add a report line saying that
   Windows Update is offering a repair install and that `wim-scan` is worth
   running. That is how the corrupted store showed up here, twice, without
   being recognised.

Check before writing the fix whether `win_updates` exposes, per update, the
WUA `ResultCode` (2 succeeded, 3 succeeded with errors) or only `installed`:
if Setup's failure comes back as "succeeded with errors", point 1 may reduce to
reading that field.

### How to reproduce without the original host

The block is not specific to that host: Setup refuses any target older than
the host. On a test VM (see the `win-workman-pkg-test` skill), from a 24H2
baseline: install the 25H2 enablement package
(a site-specific playbook outside this repository), then `wu-run-upgrades`.
If Windows Update does not offer the feature update to a healthy VM — it is
offered to hosts it considers in need of repair — the detection of point 1 can
still be unit-tested by feeding `run_round.yaml` two rounds with the same
update id, `installed: true`, `reboot_required: true` and an unchanged build;
the site-specific harnesses for the report and the selection are outside this
repository.

### Evidence

Kept with the site notes, outside this repository: the Windows Setup logs
(`setupact.log`, `setuperr.log`, `ReportingEvents.log`) fetched from the host,
copies of the run logs (`wu-run` on 24H2 and 25H2 with 0 found, the enablement
package, the `wu-run-upgrades` of this entry, the scan after it) and the history
of the host. The readings of boots, WUA events, Setup errors, `CompatData`, DISM
state and packages quoted above were deleted by the log rotation of the MCP
server (newest 50 runs kept) and no copy exists: the WUA event counts and the
`CompatData` hard block survive only in this entry. The `CompatData_*.xml` file
itself was not fetched.
