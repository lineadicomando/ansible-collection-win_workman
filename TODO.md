# TODO

Planned improvements for the `lineadicomando.win_workman` collection.

Reviewed 2026-09-28: every entry below was checked against the current tree, and
the notes say what has changed since each was written. Re-checked 2026-10-01
against the tree at `b599405`.

Priorities, assigned 2026-09-28:

- **P1** — affects the labs in production or is a correctness bug; do next.
- **P2** — merged or written code that has never been exercised; do before
  relying on it.
- **P3** — improvements, refactoring and work that waits on something else.

| Priority | Entry |
| --- | --- |
| P1 | Kill declared processes before install |
| P1 | `pkg_act_on` reads from `ansible_remote_tmp` |
| P1 | `wu`: a feature update that does not apply is reported as installed |
| P1 | `lock-off` leaves the logon screen without the user list until a restart |
| P1 / P3 | AutoCAD: end-to-end validation on a real host (P1 only before a rollout) |
| P2 | Verify the upgrade path of the `uninstall_before_upgrade` roles |
| P2 | `pkg_act_off` does not stop declared services |
| P2 | `usr`: test a version upgrade |
| P2 | Audit the catalog drafts |
| P3 | Wait mode for the helper uninstall in `pkg_act_off` |
| P3 | veyon `config`: a crashing `veyon-cli` export reads as a missing key |
| P3 | `usr`: fewer round trips in `usr-on` |
| P3 | `usr`: test several policies at once |
| P3 | `usr`: a role with both scopes |
| P3 | `usr`: `usr-purge` with copies still installed |
| P3 | `usr`: agent log rotation |
| P3 | `usr`: adopt more per-user packages |
| P3 | AutoCAD: promote `odis_uninstall` and `find_products` to `pkg_utils` |
| P3 | `autoshutdown`: implement the `nouser` mode |
| P3 | Roles with no documentation at all |
| P3 | `run_powershell`: `timeout` is ignored with `background=true` |

---

## Package workflow

### Kill declared processes before install

**Priority:** P1 — the root cause of the Veyon outage: stopping services alone did not prevent it  
**Status:** proposed — still unimplemented, verified 2026-09-28

`pkg_utils` stops the services listed under `services:` before installing, but
user-facing processes still lock their own files. On the teacher station of the
`ario_info` lab the Veyon Master GUI was running during the upgrade, which is
how the stale DLLs got there.

A `kill_processes:` schema field handled by `pkg_utils` would cover this,
reusing `tasks/kill.yaml`. Roles already call it from their own task files:
chrome, firefox, edge, libreoffice, autocadlt2026, and `autocadlt2023` through
its own `win_workman_autocadlt2023_kill_processes` variable — which a schema
field would make redundant. `kill.yaml` only handles lists of more than one name
since `0f0ae61`. `sketchup2026` (`b599405`) closes SketchUp in its own
`tasks/ensure_closed.yaml` with a direct `Stop-Process`, bypassing `kill.yaml`;
it guards the licence actions rather than an install, but is one more
role-local kill to fold in.

Since 2026-09-28 `veyon` lists `%ProgramFiles%\Veyon` under `cleanup_paths`, so
a file still locked after the uninstall now fails the run at *Cleanup paths*
instead of leaving a mixed install — tested on `teacher` with a DLL held open by
another process. That turns the outage into a loud failure, with Veyon
uninstalled until the lock is released; only killing the processes first
prevents it. Veyon's own uninstaller removes the whole directory, unknown and
read-only files included, whenever nothing is locked.

### Verify the upgrade path of the `uninstall_before_upgrade` roles

**Priority:** P2 — merged code on a production path, but no failure observed; veyon is covered by the P1 entries  
**Status:** follow-up to a change already merged — rewritten 2026-09-28

The preliminary uninstall of an upgrade goes through `pkg_act_off` instead of
calling `win_package` directly, so `uninstall_via_helper`, the
`before_uninstall` / `after_uninstall` hooks, the Windows Installer wait
(`65b0e03`), `cleanup_registry_key`, `cleanup_paths` and the leftovers pass all
apply to upgrades.

The earlier version of this entry asked to verify the thirteen roles that
declare `cleanup_paths` or `cleanup_registry_key`. That was wrong:
`uninstall_before_upgrade` defaults to `false` and none of those thirteen sets
it, so their upgrade never calls `pkg_act_off`. Their uninstall path has
meanwhile been exercised with `off` in `c0f7c5c` and `2e3dddf` (python313,
embarcadero_devcpp, winrar, foxit_pdf_reader, p7zip).

The roles whose upgrade really goes through `pkg_act_off` are postman, winscp,
inkscape, putty, mysql_server and veyon. Run an upgrade of each on a test VM
(install the previous release, then `<role>-on`) and check that the state save
and restore around the uninstall leaves the install step running.

### `pkg_act_off` does not stop declared services

**Priority:** P2 — every uninstall relies on the vendor uninstaller stopping its own service  
**Status:** found 2026-09-28 while testing the Veyon cleanup on `teacher`

`pkg_act_on` stops the services under `services:` before the preliminary
uninstall of an upgrade, but an explicit `<role>-off` goes straight to
`pkg_act_off`, which never does. Veyon gets away with it because its uninstaller
stops the service through `veyon-cli`; when `veyon-cli` could not start (a test
held `veyon-core.dll` open exclusively), `VeyonService` kept running, the
uninstaller removed the registry entry and left 48 files behind. Move the
`services_stop` include into `pkg_act_off`, before *Uninstall package*; the
upgrade path then gets it for free and the call in `pkg_act_on` can go.

### Wait mode for the helper uninstall in `pkg_act_off`

**Priority:** P3 — do it when a hang is actually observed; the current default is the right one  
**Status:** proposed — role list updated 2026-09-28

`Start-Process -Wait` does not simply `WaitForExit()` on the process it
launched: it waits for the whole job object, every descendant included. That is
what makes bootstrapper-style installers work, where the parent hands off to a
child and exits at once, and it is also what hangs forever when a program leaves
a stray helper running.

`tasks/start_process.yaml` exposes the choice: `win_workman_exec_wait_tree`
defaults to `true` (the job-object wait) and can be set to `false` to wait on
the launched process alone, with an optional `win_workman_exec_timeout`. The
helper uninstall inside `pkg_act_off` still hardcodes `-Wait`
(`pkg_act_off.yaml:296` and `:298`).

Twelve roles declare `uninstall_via_helper: true`: dbeaver, driver_reviver,
embarcadero_devcpp, filezilla, firefox, orwell_devcpp, puredata, redpanda_cpp,
veyon, vivaldi, vlc, winrar. A thirteenth caller sits outside the schema:
`audacity/tasks/remove_superseded.yaml` sets it to run the old release's Inno
uninstaller. For most of them the job-object wait is
load-bearing: NSIS uninstallers copy themselves to `%TEMP%` and the launched
process exits immediately — `5a0e983` is exactly that failure on the Dev-C++
roles. A process-only wait would report a barely started uninstall as finished.

So: add the option with `true` as the default, then enable it per role only
where a hang is actually observed. Do not flip the default.

### `pkg_act_on` reads from `ansible_remote_tmp`

**Priority:** P1 — one-line correctness fix, breaks any consumer that does not set the variable  
**Status:** proposed — one line, `tasks/pkg_act_on.yaml:418`

`win_copy` puts the installer in `win_workman_remote_tmp` (the collection's own
default, `C:\Windows\Temp\ansible`), but the *Install package* task reads it
back from `ansible_remote_tmp`, an Ansible connection variable. The two coincide
only because every `win_edulab` inventory sets
`ansible_remote_tmp: C:\Windows\Temp\ansible` in `group_vars/win_managed/vars.yaml`
(re-checked 2026-10-01 on all seven inventories).

It is the last reference to `ansible_remote_tmp` in the roles. A consumer who
does not set the variable gets either the wrong path or an undefined-variable
error. The same coupling was removed from `autocadlt2026` in `fac39f0`.

### veyon `config`: a crashing `veyon-cli` export reads as a missing key

**Priority:** P3 — 4.10.x only; matters while a lab still runs it  
**Status:** found 2026-09-28; not reproduced on 4.11.2 and 4.11.3

`tasks/import_keys.yaml` decides whether a key is installed from the exit code
of `veyon-cli authkeys export`. On 4.10.0 the export succeeds and then crashes
on exit (`0xC0000005`), so the key reads as missing, the import runs again and
fails with "one or more key files already exist". Base the check on the
exported file (`Test-Path` plus the fingerprint) rather than on `$LASTEXITCODE`.
On `teacher` (2026-09-28) `config` imported the key on a fresh 4.11.2 and found it
unchanged after the upgrade to 4.11.3, so the export exits cleanly there. Fix it
only if a 4.10.x lab needs `config` before being upgraded.

---

## Per-user deferred install (`usr`)

State on 2026-09-16: implemented and validated with local and Samba AD domain
users; `zed` is the only `usr` role. Before opening any file, load what already
maps it:

- **Skills** (project repo, `.claude/skills/`): `win-workman-pkg-utils` (section
  *Per-user deferred install — file map*: every file, fact, var, host path),
  `win-workman-schema` (*The `usr` block*), `win-workman-task-syntax`,
  `win-workman-pkg-test` (*Testing a per-user role*).
- **Design and rationale**: `docs/roles/core/pkg_utils.md`, section
  *Per-user deferred install*.
- **Regression test**: `tests/usr_zed.yaml` in the project repo (builds the
  domain via `tests/samba_dc.yaml`, asserts every step). Run it in the
  background, output under `logs/`; it takes a long time (DC build + first
  domain logon).
- Facts already measured, do not re-investigate: S4U task principals for
  another user are always denied; a `Password` principal needs the password
  and SeBatchLogonRight; the `BUILTIN\Users` + AtLogOn principal runs in the
  user's session and `Start-ScheduledTask` on it hits every interactive
  session; domain users and groups share the `S-1-5-21-` prefix
  (`LookupAccountSid` tells them apart).

### Fewer round trips in `usr-on`

**Priority:** P3 — performance only; ~90 s per host is tolerable with one `usr` role  
**Status:** proposed — measured 2026-09-16

On the domain-joined lab VMs every `win_powershell` task costs 10-20 s
(`win_ping` about 6 s). `usr-on` runs seven remote tasks (~90 s), `usr-off`
four. Today, in order: `pkg_usr_stage.yaml` (tree+ACL script, agent
`win_copy`, task registration script), `pkg_usr_on.yaml` (payload `win_file`,
payload `win_copy`, `pkg_usr_policy.yaml` script, prune script).

**Plan:** (1) one script for tree+ACL+task registration, passing the agent
content as a parameter (`lookup('file', 'usr_agent.ps1')`, ~9 KB) and writing
it only when its hash differs — drops the agent `win_copy`; (2) payload
`win_copy` creates parent directories itself, so drop the `win_file`;
(3) fold the prune into the policy script (`pkg_usr_policy.yaml` gets an
optional `KeepVersion`). Keep the order payload → policy: the agent must never
see a policy whose installer is missing. Result: 3 round trips for `on`, 1 for
`off`. Each script must keep reporting `changed` only on real changes — the
idempotency check is running `zed-usr-on` twice and expecting `changed=0`.

### Test a version upgrade

**Priority:** P2 — the first zed release bump runs this path in production untested  
**Status:** proposed — upgrade path written, never exercised on a host

Expected: bumping `usr.version` and running `usr-on` stages
`payload\<schema>\<new>`, deletes the old version directory ("Remove staged
installers of other versions"), and the agent upgrades each user at logon
because `Compare-PkgVersion installed policy < 0` (`files/usr_agent.ps1`).

**Steps:** temporarily point `roles/zed/vars/main.yaml` at an older release,
`usr-on` + logon (or `usr-apply`), restore 1.19.2, `usr-on` + `usr-apply`;
assert the receipt `Message` is `installed (exit 0)` with the new `Version`
and only one directory under `payload\zed\`. Older asset digest without
downloading:
`gh api repos/zed-industries/zed/releases/tags/v<old> --jq '.assets[]|select(.name=="Zed-x86_64.exe")|.digest'`.
Zed updates itself only when launched, which the test never does. Add the
steps to `tests/usr_zed.yaml` once they pass.

### Test several policies at once

**Priority:** P3 — blocked until a second `usr` role exists  
**Status:** proposed — blocked on a second `usr` role (see *Adopt*)

The agent applies `policies\*.json` sequentially, sorted by name, in one run
per session (mutex `Local\win_workman_usr_agent`); `usr-apply` reports only
its own schema's receipt. To verify: two roles with `usr-on`, one logon, both
receipts `ok`; then `usr-purge` of one leaves the task and the other policy
(`remaining_policies` in the purge result), purge of the second removes the
whole tree.

### A role with both scopes

**Priority:** P3 — no demand yet; do it when a dual-scope package is actually needed  
**Status:** proposed

No schema carries `package` and `usr` together, so the dual case is untested:
the scope guard in `pkg_workflow.yaml` (*Validate install scope*) and
`install_scopes` in `mcp/roles.py` should already accept it. Natural
candidate: `vscode`, which ships `VSCodeUserSetup-x64-<ver>.exe`. The update
API `https://update.code.visualstudio.com/api/update/win32-x64-user/stable/latest`
returns `url`, `productVersion` and `sha256hash` in one call (as the system
one does, see skill `win-workman-pkg-update`). To verify by a manual install
before writing the schema: the HKCU uninstall key name (Inno `_is1` suffix,
AppId differs from the system setup) and how the user setup behaves silently
when the system install is present — it may warn or abort, in which case the
two scopes must be documented as mutually exclusive per host.

### `usr-purge` with copies still installed

**Priority:** P3 — only bites on an explicit purge, and the manual sequence works  
**Status:** proposed

`usr-purge` removes policy and payload but leaves copies in profiles, which
nothing tracks afterwards. Removing them needs `usr-off`, then a logon (or
`usr-apply`) per user, then `usr-purge`. Option: make purge refuse while any
profile has the package, listing who, reusing the per-profile read of
`pkg_usr_info.yaml` (HKU or `reg load`, `uninstall_key`). Override through a
variable (`win_workman_usr_purge_force: true`), not a task token: purge
rejects inline arguments because they would be parsed as targets
(`pkg_act_usr.yaml`, *Reject targets for usr-purge*).

### Agent log rotation

**Priority:** P3 — at 4-6 lines per logon the log takes years to reach 1 MB  
**Status:** proposed — small

`%LOCALAPPDATA%\win_workman\usr-agent.log` grows forever (4-6 lines per
logon). In `files/usr_agent.ps1`, right after `$logFile` is set: if it exceeds
~1 MB, move it to `usr-agent.log.1` (overwrite). Hosts pick up agent changes
at the next `usr-on`/`usr-off` (`Deploy usr agent` is a `win_copy`).

### Adopt more per-user packages

**Priority:** P3 — on demand; also unblocks *Test several policies at once*  
**Status:** proposed

Candidates to verify, none checked yet: Obsidian, GitHub Desktop, Discord,
Spotify, Cursor, Microsoft Teams (new). Qualifying test: run the installer
silently as `maint` over SSH and check it lands in `maint`'s
`%LOCALAPPDATA%` with an HKCU uninstall key — that key name is
`usr.uninstall_key`. Squirrel-based installers (GitHub Desktop, Discord)
register the key under the app name and uninstall with `Update.exe
--uninstall`; check that `UninstallString` is directly runnable, since the
agent runs it with `usr.uninstall_args` and waits for the key to disappear.
Procedure: skill `win-workman-new-role`, section *Per-user role*; test with a
copy of `tests/usr_zed.yaml`.

---

## AutoCAD roles

### Promote `odis_uninstall` and `find_products` to `pkg_utils`

**Priority:** P3 — refactoring; waits for the end-to-end validation below  
**Status:** proposed

`roles/autocadlt2023/tasks/` and `roles/autocadlt2026/tasks/` carry byte-identical
copies of `odis_uninstall.yaml` (run an ODIS uninstall waiting on the launched
process alone) and `find_products.yaml` (resolve uninstall-hive entries by
display-name pattern, because Autodesk component GUIDs change with every
release). They were duplicated on purpose, to keep the fix out of the shared
code path while it was unproven.

`find_products.yaml` in particular is not Autodesk-specific and would serve any
role that needs to uninstall something whose GUID is not stable. Once both have
run against real hosts a few times, move them into `pkg_utils` and have the two
roles include them from there.

### End-to-end validation on a real host

**Priority:** P1 if AutoCAD LT 2026 is to be rolled out to a lab, P3 otherwise  
**Status:** blocking before lab-wide use — no run found in the project logs as
of 2026-09-28

- `autocadlt2026-on` has never been run end to end since `fac39f0` rewrote its
  presence detection. The install path — 2.7 GB per host, the `db-bootstrap`
  polling, the licence registration through `AdskLicensingInstHelper` — is
  unverified.
- `autocadlt2023-off` was validated on PC05 of `ario_info` (2026-09-11); the
  `off-full` variant was not. PC05 is the natural candidate: it still carries
  exactly the leftovers that `off-full` targets (the two Material Library 2023
  packages, the emptied install directory, the ACDLT2023 licensing logs).
- `autocadlt2026-off-full` has never been run since the GUIDs became
  runtime-resolved in `93a26d7`.

---

## Management roles

### `autoshutdown`: implement the `nouser` mode

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

### `lock-off` leaves the logon screen without the user list until a restart

**Priority:** P1 — hit on a whole lab after every maintenance; the workaround is restarting every idle host  
**Status:** found 2026-10-17 on `ario_info`; cause verified on the hosts, fix not written

After `lock` → `wu-scan` → `wu-run` → `lock-off` on the 30 hosts of
`ario_info`, every host with nobody logged on showed the "user name and
password" prompt instead of the list of users. A restart brought the list
back, host by host. The registry was already right: `lock-off` had done its
job, the logon screen just had not read it again.

#### What was read on the hosts

`run_powershell` on PC01, PC05 and PC06 at 09:58 (log
`logs/20261017-095813-ps-PC01_PC05_PC06.log` in the project repo):

| Host | `DontDisplayLastUserName` | `HKLM:\SOFTWARE\Ansible\WinMaint` | `LogonUI.exe` started | Last boot |
| --- | --- | --- | --- | --- |
| PC05 | absent | empty | 09:41:01 (session 2) | 09:34:55 |
| PC06 | absent | empty | 09:41:06 (session 2) | 09:34:55 |
| PC01 | absent | empty | 09:56:04 (session 2) | 09:55:10 (restarted by hand) |

No `explorer.exe` on any of them, so no user logged on. PC05 and PC06 showed
the prompt, PC01 the user list.

#### Cause

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
- The same happens when a host restarts while locked: on 2026-10-17 `DOC`
  restarted inside `wu-run-optional-drivers` (run
  `logs/20261017-094805-win_wm-lock_wu-run-optional-drivers_lock-off-DOC_PC02_PC03_P.log`),
  so its LogonUI too came up with the lock on.
- `lock-reset` (`act_reset.yaml`) removes the value in the same way and has the
  same gap.
- Not verified: whether the stale LogonUI also keeps showing the maintenance
  banner (`LegalNoticeCaption`/`LegalNoticeText`). Nobody reported it; check it
  while testing the fix. `SeInteractiveLogonRight` is checked at each logon
  attempt, so restoring it has no such delay.

Workaround used on 2026-10-17: `restart` on every host after `lock-off`
(runs `20261017-100102-…` and `20261017-100350-…` in the project's `logs/`).

#### What to change

Add a step at the end of `act_off.yaml` (and of `act_reset.yaml`), after the
registry is restored, that makes the logon screen start again on the sessions
that have no user, and only when `DontDisplayLastUserName` actually changed
(the restore and remove tasks already know). Leave sessions with a user alone:
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

#### How to test

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

### `wu`: a feature update that does not apply is reported as installed

**Priority:** P1 — a correctness bug in the report, and five needless restarts of a lab host  
**Status:** found 2026-10-10 on `PC16` of `ario_ling`; cause read in the code and in the host's logs, fix not written

`wu-run-upgrades` reported a feature update as installed while Windows Setup
had refused it, and restarted the host five times before giving up with a
message that suggests running it again. The run ended `failed=0`, exit code 0.

The entry is written to be worked without the host: `PC16` is being repaired
and will not be in this state again. Everything quoted below was read on
2026-10-10; the evidence is saved in the project repo (see **Evidence**).

#### What the role printed

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

#### What happened on the host

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

#### Why Setup refused it (context, not the bug)

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
state described in `local/docs/spalla_info2-wim.md` of the project repo. On such
a host a plain `wu-run` reports `0 found` and lists `Windows 11, version 2xH2`
under "Filtered out", on 24H2 and on 25H2 alike: that pair is a recognisable
signature (see point 4 below).

#### Where it goes wrong in the role

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

#### What to change

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

#### How to reproduce without `PC16`

The block is not specific to that host: Setup refuses any target older than
the host. On a test VM (see the `win-workman-pkg-test` skill), from a 24H2
baseline: install the 25H2 enablement package
(`local/wu_25h2_enablement.yaml` in the project repo), then `wu-run-upgrades`.
If Windows Update does not offer the feature update to a healthy VM — it is
offered to hosts it considers in need of repair — the detection of point 1 can
still be unit-tested by feeding `run_round.yaml` two rounds with the same
update id, `installed: true`, `reboot_required: true` and an unchanged build;
`local/test_wu_report.yaml` and `local/test_wu_selection*.yaml` in the project
repo are the existing harnesses for the report and the selection.

#### Evidence

In the project repo (`ansible-win_edulab`, not tracked by git: `local/` and
`logs/` are ignored):

- `local/reports/ario_ling/2026-10-10-pc16-wu-upgrade/` — `setupact.log`,
  `setuperr.log` and `ReportingEvents.log` fetched from the host at 11:21, plus
  copies of the run logs: `20261010-102911-win_wm-wu-run-PC16.log` (`wu-run` on
  24H2, 0 found), `20261010-ekb25h2-PC16.log` (enablement package),
  `20261010-103437-win_wm-wu-run-PC16.log` (`wu-run` on 25H2, 0 found),
  `20261010-103608-win_wm-wu-run-upgrades-PC16.log` (the run of this entry),
  `20261010-111708-win_wm-wu-scan-PC16.log` (scan after it).
- `logs/20261010-111634-ps-PC16.log`, `…-111653-ps-PC16.log`,
  `…-111739-ps-PC16.log` — the readings of boots, WUA events, Setup errors,
  `CompatData`, DISM state and packages quoted above.
- `local/docs/ario_ling-25H2.md`, section "Aggiornamento del 10 ottobre 2026" —
  the history of the host and of the day.

The `CompatData_*.xml` file itself was not fetched; its hard block is quoted
above from the reading in `…-111653-ps-PC16.log`.

---

## MCP server

The server lives in the project repo (`ansible-win_edulab`, `mcp/`), not in the
collection.

### `run_powershell`: `timeout` is ignored with `background=true`

**Priority:** P3 — no harm observed, but a hung background run is never killed  
**Status:** found 2026-10-08 on `PC19` of `ario_info`; cause read in the code, fix not written

A `DISM /StartComponentCleanup` started with `background=true` and
`timeout=3600` ran for 65 minutes and ended on its own (log
`20261008-082009-ps-PC19.log`). The tool schema describes `timeout` as "Seconds
before the run is killed", with no exception for background runs.

The background branch of `run_powershell` (`mcp/server.py:400`) calls
`start_run(cmd, label, env=ADHOC_ENV, redact=redact)` and drops `timeout`, while
`start_logged` in `mcp/runlog.py` accepts one and hands it to the supervisor.
The synchronous branch passes it to `run_raw`.

To decide before passing it through: the default is 300 seconds, which suits a
synchronous query but would kill most background runs, started in the
background precisely because they are long. Either apply the timeout to a
background run only when the caller sets it explicitly, or say in the schema
that it does not apply there. `run_tasks` and `run_playbook` take no `timeout`
at all, so their background runs are unbounded by design.

Killing `ansible` on the controller does not stop what is already running on
the host: check what happens to a `dism.exe` or an installer left behind before
relying on the timeout to clean up.

---

## Documentation

### Audit the catalog drafts

**Priority:** P2 — a wrong page reads as documentation; start from the roles in use in the labs  
**Status:** proposed

43 of the 57 files in `docs/roles/catalog/` still open with
`> **Work in progress** — preliminary draft.` The banner says nothing about
whether the content is right, and both cases exist:

- `sketchup2026.md` is accurate and current, `license` and `unlicense` included
   — the banner is simply stale.
- `autocadlt2026_en.md` and `autocadlt2026_it.md` documented two roles that had
  never existed under those names, with the wrong provider and the wrong
  installer filename. Deleted and replaced in `fac39f0`.

A wrong draft is worse than no page, because it reads as documentation. Go
through them against the roles, fix what is wrong, and drop the banner from the
ones that earn it.

### Roles with no documentation at all

**Priority:** P3 — four pages, no wrong information in the meantime  
**Status:** proposed

Four roles have no page in `docs/roles/`: `googledrive`, `tinycad`, `winmerge`,
`winrar` (re-checked 2026-09-28; `winmerge` is only named in passing in
`docs/roles/core/pkg_utils.md`). `chkdsk`, `logoff`, `ms_account`, `oobe`,
`ping`, `secure_ssh`, `sfc`, `shutdown`, `widgets`, `wim` and `wol` are covered
collectively by `docs/roles/management/system-tools.md`, which is correct and
needs nothing.
