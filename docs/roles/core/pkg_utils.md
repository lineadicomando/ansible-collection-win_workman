# Role: pkg_utils

> **Work in progress** — preliminary draft.

Low-level package operations shared by all software roles. Not called directly
by playbooks — schema roles delegate to it via `include_role tasks_from: pkg_workflow`.

---

## Package schema format

Each software role exposes a `win_workman_<schema>_schema` variable in
`vars/main.yaml` with the following structure:

```yaml
win_workman_<schema>_schema:
  name: "Human-readable name"
  default_action: !!str on      # action used when task string has no action token

  package:
    setup_file: installer.exe       # filename expected in storage/remote_tmp
    searchName: "Registry display name"
    version: "1.2.3"
    provider: registry              # registry | portable
    install_args:
      - /VERYSILENT
    uninstall_args:
      - /VERYSILENT
    uninstall_before_upgrade: false # uninstall old version before installing new

  files:                            # list of downloadable assets
    - filename: installer.exe
      url: https://…
      checksum: sha256:…
      extract: 7z                   # optional: extract after download
      dest_dir: SubDir              # optional: destination under portable_path

  shortcuts:                        # optional: shortcuts to create/remove
    - description: "App Name"
      dest: "%PUBLIC%\\Desktop\\App.lnk"
      target: "C:\\Program Files\\App\\app.exe"
```

For the difference between `registry` and `portable` providers see
[architecture.md](../architecture.md#package-providers).

---

## Actions (`pkg_workflow`)

`pkg_workflow` validates the action against `win_workman_pkg_actions` and fails
immediately with a clear error if an unknown action is passed.

| Action | Task file | Description |
|---|---|---|
| `on` | `pkg_act_on` | Install or upgrade |
| `off` | `pkg_act_off` | Uninstall |
| `download` | `pkg_act_download` → `download` | Download to `win_workman_storage_path` |
| `copy` | `pkg_act_copy` | Copy from storage to remote temp |
| `info` | `pkg_act_info` | Report installation state |
| `is_present` | `pkg_act_is_present` | Assert package is installed |
| `usr` | `pkg_act_usr` → `pkg_usr_<verb>` | Per-user deferred install, see [below](#per-user-deferred-install-usr) |

---

## Key variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_storage_path` | `~/win_workman_storage` | Controller-side installer storage |
| `win_workman_remote_tmp` | `C:\Windows\Temp\ansible` | Temp dir on target |
| `win_workman_portable_path` | `C:\PortableApps` | Root for portable apps |
| `win_workman_restart` | `true` | Allow reboot after install if needed |
| `win_workman_restart_timeout` | `180` | Seconds to wait after reboot |
| `win_workman_default_lang` | `en_US` | Locale hint for multi-locale roles |
| `win_workman_cleanup_uninstaller_dir` | `true` | Remove an install directory left holding only uninstaller files |

### Uninstall cleanup

`off` removes more than the package itself, in this order: the registry key (only
when the schema sets `cleanup_registry_key`), the schema's `cleanup_paths`, then
the install directory if nothing but uninstaller files is left in it.

That last step is global, not per-role: Inno Setup cannot delete the
`unins000.exe` it is running from, so every Inno-based package (`vscode`, `git`,
`gimp`, `netbeans`, `winmerge`, `peazip`, `laragon`) leaves its install directory
behind holding that one file. The step removes the directory only when *every*
remaining entry matches `unins*` and is not a subdirectory — a directory still
holding user data, extensions or a second product is reported and left alone.
Drive roots and shared system directories are refused outright.

Set `win_workman_cleanup_uninstaller_dir: false` to keep the leftovers. A role
that needs a non-empty install directory removed wholesale should use
`cleanup_paths` instead, which makes that intent explicit per package.

---

## Per-user deferred install (`usr`)

Some software ships only a per-user installer: it installs into the profile of
whoever runs it (`%LOCALAPPDATA%\Programs`, `HKCU` uninstall key), even when run
elevated. Run by Ansible it would land in the Ansible user's profile. The `usr`
action installs it for other users instead, by deferring the install to their
logon.

### Install scopes

A schema declares what it supports through its blocks:

| Block | Scope | Actions |
|---|---|---|
| `package` | `sys` — machine-wide, now | `on`, `off`, `info`, `copy`, `shortcuts`, `is_present` |
| `usr` | `usr` — per user, at logon | `usr-<verb>` |

A schema may carry both. `download` works for either. `pkg_workflow` refuses
`usr-*` on a schema without a `usr` block, and the machine-wide actions on a
schema that has only a `usr` block, pointing to the right syntax. The MCP
`get_role_info` tool reports the result as `install_scopes`.

### Task syntax

```
<schema>-usr-<verb>[-<target>[+<target>…]]
```

| Verb | Effect |
|---|---|
| `on` *(default)* | Download, stage the installer on the host, mark the targets `present` |
| `off` | Mark the targets `absent`; without targets, every target of the policy |
| `info` | Policy, and per profile (or per given target) installed version and last agent outcome |
| `apply` | Run the agent now for the logged-on users and wait for it |
| `purge` | Remove the policy and staged installer; takes no targets |

Targets are account or group names, `DOMAIN\name`, or SIDs, joined by `+`.
Everything after the verb is rejoined on `-` before splitting on `+`, so names
containing dashes work: `zed-usr-on-student-alice+student-bob`. `+` cannot occur in a
Windows or AD account name; `,` cannot be used because it separates tasks in the
`t` extra var. Without targets, `on` uses `win_workman_usr_targets`.

`on` and `off` merge into the policy rather than replace it, so they compose:

```
zed-usr-on                 # every member of BUILTIN\Users
zed-usr-off-student-bob    # …except student-bob, who uninstalls at next logon
```

### How it works

```
C:\ProgramData\win_workman\usr\
├── agent.ps1                     # one agent for every policy
├── policies\<schema>.json        # version, args, sha256, targets by SID and state
└── payload\<schema>\<version>\   # staged installer
```

- **Logon task** `\win_workman\usr-agent`: principal `BUILTIN\Users`, trigger at
  logon of any user, runs the agent through `conhost.exe --headless` in that
  user's session, without elevation. No password is stored.
  `usr-apply` starts the same task on demand: it runs in every interactive
  session.
- **The agent**, for each policy that applies to the user, reads the `HKCU`
  uninstall key named by `uninstall_key` and then installs (missing or older),
  does nothing (same or newer: it never downgrades, because packages such as
  Zed update themselves), or uninstalls (`absent`, waiting for the key to go,
  since Inno Setup and NSIS uninstallers return before they finish).
  It verifies the installer's sha256 before running it and records the outcome
  under `HKCU\Software\win_workman\usr\<schema>` (`State`, `Result`, `Changed`,
  `Version`, `Message`, `Timestamp`), plus a log in
  `%LOCALAPPDATA%\win_workman\usr-agent.log`.
- **Rule resolution**: targets are stored by SID, resolved on the host when the
  policy is written, and matched against the user's token. An entry naming the
  user wins over group entries; among group entries that disagree, `absent`
  wins. A user matched by no entry is left alone. Each entry also records its
  `kind` (`user`, `group`, `computer`, `unknown`, from `LookupAccountSid`): check it, because a
  mistyped name can resolve to a group — on an Italian Windows `nessuno` is the
  local group *None*. An unresolvable name fails the task.
- **Access control**: the tree grants Users read and execute only. Every user
  who logs on runs the agent and the payload, so write access for one user would
  mean running code as all the others.

### Why a logon task

Measured on Windows 11 25H2 before choosing it:

- A task with an `S4U` principal (no password) for another user cannot be
  registered: *Access denied* from the Ansible session, from SYSTEM, with the
  batch logon right granted, and with the target in Administrators.
- A `Password` principal works, creates the profile of a user who never logged
  on, and runs at once, but needs every user's password and the
  *Log on as a batch job* right, which standard users lack.
- A group principal at logon needs neither, covers users created later and
  domain users who never logged on, and can still be started on demand for the
  users already logged on.

The cost is that `usr-on` does not install anything by itself: `usr-info` tells
who has what.

### Schema block

```yaml
win_workman_zed_schema:
  name: Zed
  role: lineadicomando.win_workman.zed      # its last segment names the policy
  default_action: usr
  usr:
    setup_file: Zed-x86_64-1.19.2.exe       # must match a files entry with a sha256
    version: "1.19.2"
    uninstall_key: "{2DB0DA96-CA55-49BB-AF4F-64AF36A86712}_is1"   # under HKCU\…\Uninstall
    install_args: [/VERYSILENT, /SUPPRESSMSGBOXES, /NORESTART]
    uninstall_args: [/VERYSILENT, /SUPPRESSMSGBOXES, /NORESTART]
    success_exit_codes: [0]                 # optional
    timeout: 900                            # optional, seconds
  files:
    - filename: Zed-x86_64-1.19.2.exe
      url: https://github.com/zed-industries/zed/releases/download/v1.19.2/Zed-x86_64.exe
      checksum: sha256:dd8fd2b2…
```

Bumping `version` and running `usr-on` again stages the new installer, removes
the previous one, and upgrades each user at their next logon.

### Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_usr_targets` | `[BUILTIN\Users]` | Targets of a bare `usr-on` |
| `win_workman_usr_path` | `C:\ProgramData\win_workman\usr` | Root of policies, payloads and agent |
| `win_workman_usr_timeout` | `900` | Seconds the agent allows an installer or uninstaller |
| `win_workman_usr_apply_timeout` | `900` | Seconds `usr-apply` waits for the agent in every session |

---

### Available actions list

`pkg_utils` also exposes `win_workman_pkg_actions` (defined in `vars/main.yaml`)
as the canonical list of valid action strings. Schema roles can use it for
validation or branching.

---

## Calling pkg_utils from a schema role

```yaml
# roles/myrole/tasks/main.yaml
- name: Run package workflow
  ansible.builtin.include_role:
    name: lineadicomando.win_workman.pkg_utils
    tasks_from: pkg_workflow
  vars:
    win_workman_schema: "{{ win_workman_myrole_schema }}"
```
