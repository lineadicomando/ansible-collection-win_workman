# Per-user deferred install (`usr`)

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

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

## Fewer round trips in `usr-on`

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

## Test a version upgrade

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

## Test several policies at once

**Priority:** P3 — blocked until a second `usr` role exists  
**Status:** proposed — blocked on a second `usr` role (see *Adopt*)

The agent applies `policies\*.json` sequentially, sorted by name, in one run
per session (mutex `Local\win_workman_usr_agent`); `usr-apply` reports only
its own schema's receipt. To verify: two roles with `usr-on`, one logon, both
receipts `ok`; then `usr-purge` of one leaves the task and the other policy
(`remaining_policies` in the purge result), purge of the second removes the
whole tree.

## A role with both scopes

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

## `usr-purge` with copies still installed

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

## Agent log rotation

**Priority:** P3 — at 4-6 lines per logon the log takes years to reach 1 MB  
**Status:** proposed — small

`%LOCALAPPDATA%\win_workman\usr-agent.log` grows forever (4-6 lines per
logon). In `files/usr_agent.ps1`, right after `$logFile` is set: if it exceeds
~1 MB, move it to `usr-agent.log.1` (overwrite). Hosts pick up agent changes
at the next `usr-on`/`usr-off` (`Deploy usr agent` is a `win_copy`).

## Adopt more per-user packages

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
