# `sfc` repair reporting

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## `sfc`: repairs are reported as "no integrity violation"

**Priority:** P1 — a correctness bug: the role hides exactly what it is run to find  
**Status:** found 2026-10-31 on a production host; cause read in the role and in CBS.log, fix not written

On 2026-10-31 `sfc` on a lab host (25H2 26200.9457, with
`win_workman_restart: false`) printed `sfc found no integrity violation.`,
`changed: false`. In the same minutes sfc had written **2538** repair lines to
CBS.log and had left the repairs staged for a restart: `wim-scan` right after
failed with `ERROR_FAIL_REBOOT_REQUIRED` (0x80070bc9, "a pending repair
transaction already exists"), and `RebootPending` plus `WinSxS\pending.xml`
were set. Context: the host had just come back from a boot loop with thousands
of system files replaced by hand (incident report kept with the site notes,
outside this repository).

### What the role reads and what sfc wrote

`roles/sfc/tasks/act_on.yaml` collects the `[SR]` lines stamped from the start
of the run (CBS.log plus the `CbsPersist_*.log` written since: that part works,
CBS.log rolled over twice during this run) and counts:

| Counter | Pattern in the role | Lines on the host |
| --- | --- | --- |
| `$repaired` | `Repaired file\|Repairing corrupted file` | **0** |
| `$cannotRepair` | `Cannot repair` | 0 |
| `$repairFailed` | `Repair failed` | 0 |

The `[SR]` lines actually written by this build (3173 in total, numbers
replaced by `N`; read from `CbsPersist_20261031095119.log` with
`run_powershell`):

| Count | Text after `[SR]` |
| --- | --- |
| 2538 | `Repairing file \??\C:\WINDOWS\bcastdvr\\KnownGameList.bin from store` |
| 211 | `Beginning Verify and Repair transaction` |
| 209 | `Verifying N components` |
| 209 | `Verify complete` |
| 2 | `Repairing N components` |
| 2 | `Repair complete` |
| 1 | `Committing transaction` |
| 1 | `Cannot commit interactively, there are boot critical components being repaired` |

So:

1. the repair pattern is from older builds: on 26100/26200 the line is
   `Repairing file <path> from store`, and nothing matches;
2. nothing looks at `Cannot commit interactively …`: the repairs are only
   staged, and they are lost for any servicing operation until a restart
   (DISM refuses to start, as `wim-scan` did). The role neither says so nor
   restarts. Its `win_workman_restart` only restarts **before** the scan.

The console output (`$stdOut`) is localised and the role drops every line
holding a digit, so it cannot help; the exit code was 0.

### What to change

- Count repairs with every known form: `Repairing file .* from store`,
  `Repaired file`, `Repairing corrupted file`. Count the files, not the lines:
  one file can be repaired in more than one transaction, so take the unique
  paths.
- Count failures the same way, checking the 26100 wording of the failure lines
  first (it is not in this log; see "How to reproduce" for how to produce one).
  Keep `ScanRan` as it is.
- Detect a staged commit: the `Cannot commit interactively` line, and to be
  safe also `RebootPending` / `WinSxS\pending.xml` set **after** the scan when
  they were not set before it. Then:
  - `changed: true`, message `sfc repaired N files; the repair completes at the next restart (boot critical components)`;
  - a new result field (`RestartRequired: true`) and a fact for the tasks after it;
  - restart through `pkg_utils` `tasks/restart.yaml` when a variable allows it.
    Reusing `win_workman_restart` (default `true`) keeps one switch for "this
    role may restart the host"; mention in the docs that it now acts before and
    after the scan.
- Put the counts in the message (`N files repaired, M not repairable`) and list
  the first ~20 paths in the result, so the run log says what changed without
  opening `sfc_log_file.log` on the host.
- Update `docs/roles/management/system-tools.md` (section `sfc`) and the role's
  `meta/mcp.yaml` notes.

### How to reproduce in a test VM

On the `teacher` or `student01` VM of the project repo (25H2, see skill
`win-edulab-test-vms`; revert to `baseline` afterwards — reverting needs the
user's confirmation, see `CLAUDE.local.md`). Test with
`run_powershell` / `run_tasks` against inventory `school`.

1. **Plain repair** (the miscount). WinSxS and System32 share the file through a
   hard link, so overwriting the file in place corrupts the store copy too
   and sfc reports "cannot repair". Delete it instead, which leaves the store copy
   intact:

   ```powershell
   $f = "$env:windir\System32\tzres.dll"      # any non boot-critical protected file
   takeown /f $f; icacls $f /grant '*S-1-5-32-544:F'
   Remove-Item $f -Force
   ```

   Run `sfc`: expected `Repairing file \??\C:\WINDOWS\System32\\tzres.dll from store`
   in CBS.log. Today the role reports "no integrity violation".
2. **Staged commit** (the restart). Do the same on a boot-critical file
   loaded at boot, e.g. `System32\cdd.dll` or `System32\drivers\beep.sys`: try
   rename + copy of a different file first, since a file that is loaded cannot
   be deleted. Expected `Cannot commit interactively, there are boot critical
   components being repaired`, then `RebootPending` and `pending.xml`, and
   `wim-scan` failing with 0x80070bc9 until a restart. Snapshot the VM before
   this step: a mistake here can leave it unbootable.
3. **Not repairable**, to read the 26100 failure wording: overwrite a protected
   file **in place** (`[IO.File]::WriteAllBytes` on the hard link), so the store
   copy is corrupted too. Run `sfc`, then read the new `[SR]` lines. Expected
   something like `Cannot repair member file …`; note the exact text in the role
   comment.

Case 2 also covers the branch `d68a392` added and never ran: with the repair
staged, a second `sfc` before the restart should refuse to scan, leave no `[SR]`
line and fail the task with the "did not scan" message.

Each case: run `sfc` before the fix (wrong message), after the fix (right counts,
`changed`, `RestartRequired`), and with `win_workman_restart: false` (no
restart, message still says one is needed). Then `wim-scan` to confirm the
store is usable again. A test playbook in the project's `tests/` (like
`tests/lock.yaml`) can chain the three cases from `baseline`.

### Evidence

Copied on 2026-10-31 to the site notes, outside this repository, since `logs/`
keeps only the newest 50 runs:

- the run of the role;
- `[SR]` counts after the run, reboot flags and the CBS tail with 0x80070bc9 /
  "a pending repair transaction already exists" (2538 repaired, 0 cannot);
- the refused `wim-scan` (it only says "Module failed: Unknown error."; the
  reason is in the CBS tail above);
- the restart, and the reading of the `[SR]` line shapes.
