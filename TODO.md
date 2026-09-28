# TODO

Planned improvements for the `lineadicomando.win_workman` collection.

Reviewed 2026-09-28: every entry below was checked against the current tree, and
the notes say what has changed since each was written.

Priorities, assigned 2026-09-28:

- **P1** — affects the labs in production or is a correctness bug; do next.
- **P2** — merged or written code that has never been exercised; do before
  relying on it.
- **P3** — improvements, refactoring and work that waits on something else.

| Priority | Entry |
| --- | --- |
| P1 | Kill declared processes before install |
| P1 | `pkg_act_on` reads from `ansible_remote_tmp` |
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
| P3 | Roles with no documentation at all |

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
since `0f0ae61`.

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
veyon, vivaldi, vlc, winrar. For most of them the job-object wait is
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
`ansible_remote_tmp: C:\Windows\Temp\ansible` in `group_vars/windows11/vars.yaml`.

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
