---
name: win-workman
description: Managing Windows workstations with the collection lineadicomando.win_workman
  - installing, removing or configuring software, Windows Update, locks, shutdown,
  wallpaper and the other roles - through task strings such as chrome-off or
  wu-run-full. Read it before launching anything that takes task strings, or
  to find which role and action does what is asked.
---

# win_workman: task strings

The collection does everything through **task strings**, one per thing to do,
handed to its `dispatcher` role:

```
<role>[-<action>[-<arg>[-<arg>...]]]
```

| Task string | Does |
|---|---|
| `chrome` | install Google Chrome, or bring it to the version of the collection (the default action) |
| `chrome-off` | uninstall it |
| `chrome-info` | report what is installed, change nothing |
| `wu-run-full` | install every Windows update but feature updates |
| `wu-pause-2-w` | pause Windows Update for two weeks |
| `lock-on` | maintenance mode: a banner at the logon screen, and logons restricted |
| `autoshutdown-on-1830` | shut the host down at 18:30 every day, on its own |

- A role name never has a dash (`display_scale`): the dash separates the
  action and its arguments.
- Several task strings in one launch run in order on each host; a project
  usually takes them as a comma-separated list (`chrome,vscode-off,wu-run`).
- An action a role does not have fails the host (a package role says which
  ones it has): read the catalog instead of guessing.

## Which role and which action

The catalog of every role, its actions and the variables that shape them, is
in the files beside this one: read the one of the family you need.

- `roles-software.md`: packages (browsers, editors, office, programming,
  CAD, exam browsers, ...).
- `roles-management.md`: the roles that install no package (Windows
  Update, locks, autologon, wake-on-LAN, shutdown and restart, wallpaper,
  display scale, OpenSSH, domain join, maintenance such as chkdsk, sfc,
  optimize).

### Actions every package role has

| Action | Does |
|---|---|
| `on` | install, or upgrade to the version of the collection (usually the default) |
| `off` | uninstall |
| `info` | report the version installed and the state, change nothing |
| `download` | fetch the installer into the controller's storage only |
| `copy` | copy the installer to the host, install nothing |
| `shortcuts` | create the shortcuts again on an installed package |
| `is_present` | fail the host when the package is not installed |

A role with a per-user install (install scopes `usr`) takes
`<role>-usr-<verb>[-<target>[+<target>...]]`: the package installs at each
user's next logon; targets are accounts or groups joined by `+`.

## How to use them

- **Ask before you change.** `info`, `scan` (`wu-scan`) and the `info` of the
  management roles only read: use them to find out the state of the hosts.
  `off`, `rm` actions, `wu-run-*` with reboots and `lock-on` change what
  users see: say what you are about to do, on which hosts, and wait for the
  person when your profile asks you to.
- **Narrow the hosts.** Launch on the group or the hosts that need it (the
  limit of the launch), not on a whole inventory by default.
- **Hosts that are off** are unreachable, not failed: a project may wake them
  first (`wol` is a role and a task string too, and some projects put it
  first in the list).
- **Long tasks.** Windows Update, large installers and feature updates take
  tens of minutes and restart the hosts: launch, then follow the run rather
  than waiting in one call.
- **Variables** of the roles (paths, versions, policies) belong to the
  inventory of the lab; the task string chooses only the action and its
  arguments.
