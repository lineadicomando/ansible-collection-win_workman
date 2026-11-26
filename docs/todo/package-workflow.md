# Package workflow

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## Kill declared processes before install

**Priority:** P1 — the root cause of the Veyon outage: stopping services alone did not prevent it  
**Status:** proposed — still unimplemented, verified 2026-10-31

`pkg_utils` stops the services listed under `services:` before installing, but
user-facing processes still lock their own files. On the teacher station of a
production lab the Veyon Master GUI was running during the upgrade, which is
how the stale DLLs got there.

A `kill_processes:` schema field handled by `pkg_utils` would cover this,
reusing `tasks/kill.yaml`. Roles already call it from their own task files:
chrome, firefox, edge, libreoffice, autocadlt2026, and `autocadlt2023` through
its own `win_workman_autocadlt2023_kill_processes` variable — which a schema
field would make redundant. `kill.yaml` only handles lists of more than one name
since `243663b`. `sketchup2026` (`0771b71`) closes SketchUp in its own
`tasks/ensure_closed.yaml` with a direct `Stop-Process`, bypassing `kill.yaml`;
it guards the licence actions rather than an install, but is one more
role-local kill to fold in.

Other roles kill from the schema hooks with an inline `Stop-Process`, the
nearest thing to the proposed field today: `edge` (`before_install_ps_script`),
`seb` (`before_install_ps_script` and `before_uninstall_ps_script`), `chrome`,
`opera` and `vivaldi` (`before_uninstall_ps_script`; chrome's install hook is
commented out), `foxit_pdf_reader` (inside its uninstall script), and
`autocadlt2026`, which stops `db-bootstrap` in `tasks/act_on.yaml`. `firefox`
defines `win_workman_firefox_before_act_ps_script`, which nothing uses. The
field should replace these too.

Since 2026-09-28 `veyon` lists `%ProgramFiles%\Veyon` under `cleanup_paths`, so
a file still locked after the uninstall now fails the run at *Cleanup paths*
instead of leaving a mixed install — tested on `teacher` with a DLL held open by
another process. That turns the outage into a loud failure, with Veyon
uninstalled until the lock is released; only killing the processes first
prevents it. Veyon's own uninstaller removes the whole directory, unknown and
read-only files included, whenever nothing is locked.

## Verify the upgrade path of the `uninstall_before_upgrade` roles

**Priority:** P2 — merged code on a production path, but no failure observed; veyon is covered by the P1 entries  
**Status:** follow-up to a change already merged — rewritten 2026-09-28

The preliminary uninstall of an upgrade goes through `pkg_act_off` instead of
calling `win_package` directly, so `uninstall_via_helper`, the
`before_uninstall` / `after_uninstall` hooks, the Windows Installer wait
(`f9d7742`), `cleanup_registry_key`, `cleanup_paths` and the leftovers pass all
apply to upgrades.

The earlier version of this entry asked to verify the roles that declare
`cleanup_paths` or `cleanup_registry_key` (sixteen on 2026-11-15, `goldendict`
and `nodejs26` included). That was wrong: `uninstall_before_upgrade` defaults to `false` and,
apart from `veyon`, none of them sets it, so their upgrade never calls
`pkg_act_off`. Their uninstall path has
meanwhile been exercised with `off` in `56aac0e` and `68b27cc` (python313,
embarcadero_devcpp, winrar, foxit_pdf_reader, p7zip).

The roles whose upgrade really goes through `pkg_act_off` are postman, winscp,
inkscape, putty, mysql_server and veyon. Run an upgrade of each on a test VM
(install the previous release, then `<role>-on`) and check that the state save
and restore around the uninstall leaves the install step running.

`veyon` has run this path once in production: the upgrade 4.11.3 → 4.11.4
(`1bd8558`, 2026-10-17) on the teacher station of a production lab went through
cleanly. The other five have never run it.

## `pkg_act_off` does not stop declared services

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

## Wait mode for the helper uninstall in `pkg_act_off`

**Priority:** P3 — do it when a hang is actually observed; the current default is the right one  
**Status:** proposed — role list updated 2026-10-31

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

Thirteen roles declare `uninstall_via_helper: true`: dbeaver, driver_reviver,
embarcadero_devcpp, filezilla, firefox, goldendict, orwell_devcpp, puredata,
redpanda_cpp, veyon, vivaldi, vlc, winrar. A fourteenth caller sits outside
the schema: `audacity/tasks/remove_superseded.yaml` sets it to run the old
release's Inno uninstaller. For most of them the job-object wait is
load-bearing: NSIS uninstallers copy themselves to `%TEMP%` and the launched
process exits immediately — `b1ce531` is exactly that failure on the Dev-C++
roles. A process-only wait would report a barely started uninstall as finished.

So: add the option with `true` as the default, then enable it per role only
where a hang is actually observed. Do not flip the default.

## veyon `config`: a crashing `veyon-cli` export reads as a missing key

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

## `version_file`: a program found only that way cannot be removed

**Priority:** P3 — chrome and edge only; the skip message already tells the operator  
**Status:** known limitation of `d5aa649` (2026-10-20), no fix designed

`package.version_file` lets `pkg_act_on` skip an MSI when the executable on disk
is already at the MSI version or newer: Google Updater can move Chrome past the
enterprise MSI and leave it with no uninstall entry. Detection still reads the
uninstall entries only, so such a program is "not installed" for `off`, which
cannot remove it; the skip message says so. Chrome sets `version_file` to
`chrome.exe`; Edge opted in with `5912f96`.

To decide when it matters: either have `off` fall back on the vendor's own
uninstaller next to `version_file` (Chrome's `setup.exe --uninstall
--system-level`), or report the program as present-but-unmanaged in `info` so
the gap is visible before anyone relies on `off`.

## Remote tmp ACL: exercise the paths not run yet

**Priority:** P2 — merged in `22ec497`, two consumers not run since  
**Status:** proposed 2026-11-15

`pkg_utils/tasks/remote_tmp.yaml`, run by the dispatcher, gives
`win_workman_remote_tmp` (and `ansible_remote_tmp`) SYSTEM and Administrators full
control, no inheritance; Ansible creates the directory readable by the connecting user
alone. Tested on VMs: become to SYSTEM fails with the old ACL and works after, a SYSTEM
scheduled task runs a staged script, `openssh-update` reads its MSI from there.

Not run since: the `wu` optional updates (`run_optional.yaml`), whose
`ansible_remote_tmp: C:\Windows\Temp` override was removed in the same commit, and a
`win_iso` build, whose `setup.ps1.j2` now creates the directory with that ACL during
Setup (template rendering checked only). Run one of each.

