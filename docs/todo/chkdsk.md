# `chkdsk` exit codes

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## `chkdsk`: a volume repaired online fails the host

**Priority:** P1: a harmless finding drops the host from the play, so every task after
`chkdsk` is skipped on it  
**Status:** found 2026-11-17 on two production hosts; cause read in the role, fix not written

On 2026-11-17 `chkdsk`, `wim-scan`, `sfc`, `optimize` ran on a whole lab (34 hosts,
26H2 26300.9974). On two hosts `chkdsk` failed with
`Task failed: Module failed: Unknown error.` and `ExitCode: 5`. Ansible then dropped
both hosts, and they got no `wim-scan`, no `sfc` and no `optimize`. From the run, the
failure looked like a hang: the other hosts carried on and these two printed nothing
more.

What chkdsk had found, from `StdOut` (Italian host):

- host A: five `Rilevato collegamento non necessario ($FILE_NAME: …)` entries in the
  `$I30` index of `\Program Files (x86)\Microsoft\Temp\EU4D4B.tmp`, which is Edge
  updater scratch;
- host B: two unneeded links and one lost file (`Rilevato file perso … Richiesta di
  riconnessione`) under
  `\Windows\SystemTemp\CbsTemp._ForDelete\…\Windows11.0-KB5127690-x64-NDP481.cab\$dpx$.tmp`,
  which is leftover CBS cleanup.

Every finding is followed by `... riparati online.` ("repaired online"), and the
summary reports `0 KB in settori danneggiati` (no bad sectors). Nothing was left for
an offline repair: run again 40 minutes later, `chkdsk` returned exit 0 on both hosts,
and `wim-scan` (Healthy) and `sfc` (no violation) passed.

### Why it fails

`roles/chkdsk/tasks/act_on.yaml` maps only exit codes 0–3:

| Exit | Role result | Effect |
|---|---|---|
| 0 | `OK` | ok |
| 1 | `FIXED` | changed |
| 2, 3 | `UNRESOLVED` | failed |
| anything else | `UNKNOWN` | **failed** |

So 5 falls into `UNKNOWN`. `$Ansible.Failed` is set without `$Ansible.Result.msg`,
which is where the unhelpful "Unknown error" comes from. The codes chkdsk returns with
`/scan` on current builds are not documented beyond 0–3. Here 5 came with "all repaired
online", which is a success.

### What to change

1. **Decide health from the volume, not from the exit code.** The exit code says what
   chkdsk did, not what state the volume is left in. Read the state after the scan, and
   fail only when an offline repair is still needed:
   - cheap, always: the dirty bit (`fsutil dirty query <X>:`) and `HealthStatus` /
     `OperationalStatus` of `Get-Volume`;
   - `Repair-Volume -DriveLetter <X> -Scan` is language-independent and returns
     `NoErrorsFound`, `SpotFixNeeded` or `FullRepairNeeded`, but it is a second full
     online scan, as long as `chkdsk /scan`. Run it only when the exit code is not 0 or
     1, so a clean volume is not scanned twice.
2. **Revisit the whole exit-code map, not only 5.** Documented meanings: 2 is "disk
   cleanup performed, or not performed because `/f` was not given"; 3 is "could not
   check the disk, or errors not fixed", the real offline-repair case. With the verdict
   taken from the volume, 2 (like 1 and 5) should give `changed` and keep the host in the
   play when the volume ends up healthy.
3. **Always set a `msg` on failure**: exit code, the volume verdict, and the finding
   lines. That includes the `catch` branch, which today returns only `Output`.
4. **The role notes are wrong, not just incomplete.** `meta/mcp.yaml` and the catalog
   page (`docs/roles/management/system-tools.md#chkdsk`) say "the scan only detects".
   The run above shows `/scan` repairs online. Rewrite both: what is repaired online,
   what exit 5 means in practice, and that a failure means "an offline repair is
   needed".

### How to test

Use a small secondary VHDX on a test VM, with its letter in
`win_workman_chkdsk_volumes`, so the corruption never touches `C:`.

- `chkdsk-on` on a clean volume: exit 0, ok.
- Corrupt the VHDX (e.g. mark it dirty with `fsutil dirty set`, or damage an index
  with the volume dismounted), run `chkdsk, optimize` in one call: when the scan
  repairs online the task reports `changed` and `optimize` still runs.
- Leave the VHDX needing an offline repair: the task must fail, with a readable `msg`.
