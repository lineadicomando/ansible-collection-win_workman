# `lock-off` and the logon screen user list

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## `lock-off` leaves the logon screen without the user list until a restart

**Priority:** P1 — hit on a whole lab after every maintenance; the workaround is restarting every idle host  
**Status:** found 2026-10-17 on a production lab; cause verified on the hosts, fix not written

After `lock` → `wu-scan` → `wu-run` → `lock-off` on the 30 hosts of
a production lab, every host with nobody logged on showed the "user name and
password" prompt instead of the list of users. A restart brought the list
back, host by host. The registry was already right: `lock-off` had done its
job, the logon screen just had not read it again.

### What was read on the hosts

`run_powershell` on three of the hosts at 09:58 (the run log was later deleted
by the log rotation of the MCP server, which keeps the newest 50 runs: the
table below is the only record left):

| Host | `DontDisplayLastUserName` | `HKLM:\SOFTWARE\Ansible\WinMaint` | `LogonUI.exe` started | Last boot |
| --- | --- | --- | --- | --- |
| A | absent | empty | 09:41:01 (session 2) | 09:34:55 |
| B | absent | empty | 09:41:06 (session 2) | 09:34:55 |
| C | absent | empty | 09:56:04 (session 2) | 09:55:10 (restarted by hand) |

No `explorer.exe` on any of them, so no user logged on. A and B showed
the prompt, C the user list.

### Cause

- `lock-on` sets `DontDisplayLastUserName = 1` under
  `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System`
  (`roles/lock/tasks/maint_mode_display_last_username.yaml`) and then logs
  every user off (`pkg_utils` `tasks/logoff.yaml`). The logoff starts a new
  `LogonUI.exe` on the console session, and that LogonUI reads the policy
  while it is `1`: no user list.
- `lock-off` removes the value (or restores the saved one) and stops there
  (`roles/lock/tasks/act_off.yaml`). LogonUI reads the policy only when it
  starts, so the screen keeps the locked layout until the next logon/logoff or
  restart.
- The same happens when a host restarts while locked: on 2026-10-17 the teacher
  station restarted inside `wu-run-optional-drivers` (run log rotated away),
  so its LogonUI too came up with the lock on.
- `lock-reset` (`act_reset.yaml`) removes the value in the same way and has the
  same gap.
- Not verified: whether the stale LogonUI also keeps showing the maintenance
  banner (`LegalNoticeCaption`/`LegalNoticeText`). Nobody reported it; check it
  while testing the fix. `SeInteractiveLogonRight` is checked at each logon
  attempt, so restoring it has no such delay.

Workaround used on 2026-10-17: `restart` on every host after `lock-off`
(runs `20261017-100102-…` and `20261017-100350-…`, rotated away).

### What to change

Add a step at the end of `act_off.yaml` (and of `act_reset.yaml`), after the
registry is restored, that makes the logon screen start again on the sessions
that have no user, and only when `DontDisplayLastUserName` actually changed.
No task under `roles/lock/tasks/` registers its result: the before/after values
exist only as set_facts in `maint_mode_display_last_username.yaml` (*Set restore
flags*, *Set current value*), so derive the condition from those or add a
`register`. Leave sessions with a user alone:
their next logoff starts a fresh LogonUI anyway, and the lock screen of a
logged-on user must not be touched.

Candidates, to be compared on a test VM before choosing:

1. `Stop-Process` on the `LogonUI.exe` of each session without a user
   (session id from `Get-Process LogonUI`, user from `WTSQuerySessionInformation`
   as in `pkg_utils` `tasks/user_sessions.yaml` and `tasks/logoff.yaml`).
   Winlogon is expected to start it again; on some Windows builds killing
   LogonUI has been reported to leave a black screen until Ctrl+Alt+Del.
   Verify that a new LogonUI appears within a few seconds and shows the list.
2. `WTSLogoffSession` on the console session that has no user: Winlogon then
   builds a new session with a new LogonUI. Check that the API accepts a
   session without a user and how long the screen stays black.
3. Fallback if neither is reliable: an opt-in variable (say
   `win_workman_mode_restart_idle: false`) that restarts the hosts with no user
   at the end of `lock-off`, through `pkg_utils` `tasks/restart.yaml`.

Whatever is chosen should be idempotent: on a host where nothing was restored,
or where LogonUI already started after the restore, do nothing and report
`changed: false`.

### How to test

`tests/lock.yaml` in the project repo (VM `teacher` by default, from the
baseline snapshot; see skill `win-workman-pkg-test`) already locks a host with
a Disconnected session and asserts the registry after each step. Add, after the
`lock-off` of step 4:

- read `LogonUI.exe` start times per session and assert that the console
  session (no user) has a LogonUI started after the `lock-off` task began;
- assert that a LogonUI exists at all a few seconds later (the black-screen
  case);
- a screenshot is the only direct proof of the user list
  (`virsh screenshot teacher`); take one before and after the fix once by hand.

The VM must have more than one local user for the list to mean anything: check
which users the baseline has before relying on it, and create one if needed.
