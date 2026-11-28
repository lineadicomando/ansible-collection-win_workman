# Architecture

A playbook calls one role, `dispatcher`, with a list of task strings. Each string
names a role and an action; package roles hand the work to `pkg_utils`, management
roles implement their actions themselves.

```
win_workman_tasks: ["chrome", "wu-pause-14"]
        │  lineadicomando.win_workman.parse_tasks (plugins/filter/parse_tasks.py)
        ▼
  dispatcher ── include_role lineadicomando.win_workman.<argv[0]>
        ▼
  <role>/tasks/main.yaml ── dispatches on argv[1] (or the schema's default_action)
        ├─ package role:    pkg_utils tasks_from: pkg_workflow → pkg_act_<action>
        └─ management role: tasks/act_<action>.yaml
```

## Entry points

| Entry point | Use |
|---|---|
| role `lineadicomando.win_workman.dispatcher` | playbooks: `roles:` with `win_workman_tasks` |
| playbook `lineadicomando.win_workman.win_workman` | CLI and the [MCP server](mcp.md): `-e '{"todo": "chrome,vlc-off"}'` (`todo`: comma-separated string or list; `t` is its old name) |

Before the first task that connects to the host (a leading `wol` runs on the
controller), the dispatcher gives `win_workman_remote_tmp` an ACL that SYSTEM can use ([pkg_utils](roles/core/pkg_utils.md)).

## Task strings

```
<role>[-<action>[-<arg1>[-<arg2>…]]]
```

`argv[0]` is the role, `argv[1]` the action (omitted: the role's
`win_workman_<role>_schema.default_action`), the rest are role arguments. A role name
therefore never contains a dash (`display_scale`, not `display-scale`).

| Task string | Role | Action | Args |
|---|---|---|---|
| `chrome` | `chrome` | default (`on`) | — |
| `chrome-on-32bit` | `chrome` | `on` | `32bit` |
| `veyon-on-master` | `veyon` | `on` | `master` |
| `wu-pause-14` | `wu` | `pause` | `14` |
| `display_scale-set-150` | `display_scale` | `set` | `150` |
| `zed-usr-on-student-alice+student-bob` | `zed` | `usr` | `on`, `student-alice+student-bob` |

The filter yields, per string, `{task, schema, act, argc, argv}` (`act` is `""` when
omitted); inside the role these are `win_workman_task`, `win_workman_action`,
`win_workman_task_argc`, `win_workman_task_argv`.

## Actions

Every role's schema has a `default_action`, so a bare role name does something
sensible; `on`/`off` mean enable/disable across the collection, wired as aliases where
a role's own verbs differ (`set`/`reset`, `join`/`leave`). An unknown action fails the
host.

Standard package actions, implemented once in `pkg_utils`
(`roles/pkg_utils/vars/main.yaml`, `win_workman_pkg_actions`):

| Action | Does |
|---|---|
| `on` | install, or upgrade to the version of the schema (the usual default) |
| `off` | uninstall |
| `info` | report installed version and state, change nothing |
| `download` | fetch the files into `win_workman_storage_path` on the controller |
| `copy` | copy the installer to the host, install nothing |
| `shortcuts` | create the shortcuts again on an installed package |
| `is_present` | fail when the package is not installed |
| `usr-<verb>` | per-user deferred install: `on`, `off`, `info`, `apply`, `purge` ([pkg_utils](roles/core/pkg_utils.md#per-user-deferred-install-usr)) |

Role-specific actions are on each role's page ([catalog](index.md)) and in its
`meta/mcp.yaml`, which `get_role_info` returns.

## Package schema

A package role defines `win_workman_<role>_schema` in `vars/main.yaml`; the full field
reference is in [pkg_utils](roles/core/pkg_utils.md).

```yaml
win_workman_vscode_schema:
  name: Visual Studio Code
  default_action: !!str on
  package:
    setup_file: VSCodeSetup-x64-<version>.exe
    searchName: "Microsoft Visual Studio Code"   # matched in the Uninstall registry keys
    version: "<version>"
    provider: registry                           # msi | registry | portable; absent: auto
    install_args: [/VERYSILENT]
    uninstall_args: [/VERYSILENT]
  files:
    - filename: VSCodeSetup-x64-<version>.exe
      url: https://…
      checksum: sha256:…
```

### Providers

- **`msi`, `registry`** (absent: `auto`): passed to `win_package` as its `provider`;
  a normal installer (MSI, NSIS, Inno, Burn, …), detected through the Uninstall keys
  by `searchName`.
- **`portable`**: files extracted or copied under `win_workman_portable_path`
  (`package.portable_dir`; a file entry may carry `extract: 7z` and `dest_dir`).
  With no version to read, `on` writes `.win_workman_source`
  (`win_workman_portable_marker_name`) in each install directory: one line per
  `files` entry, filename and checksum (URL when there is none). At the next `on` a
  missing or different marker means remove and extract again from scratch, so a bump
  reaches the hosts and leaves no old files behind (anything added by hand inside is
  lost); a matching marker makes `on` a no-op. A schema with
  `uninstall_before_upgrade: true` and a file without `checksum` (a "latest" URL, as
  `postman` has) reinstalls at every `on`: there is nothing to compare.

### Install scopes

Orthogonal to the provider: a `package` block installs machine-wide now (`sys`); a
`usr` block installs into each user's profile at their next logon (`usr-<verb>`). A
per-user-only package (`zed`) has no `package` block, and `zed-on` fails instead of
installing into the Ansible user's profile.

## Global variables

Defaults in `roles/pkg_utils/defaults/main.yaml`; role variables are
`win_workman_<role>_*`, documented on the role's page.

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_tasks` | `[]` | task strings for the dispatcher |
| `win_workman_storage_path` | `$HOME/win_workman_storage` | controller-side installer storage |
| `win_workman_remote_tmp` | `C:\Windows\Temp\ansible` | staging directory on the host |
| `win_workman_portable_path` | `C:\PortableApps` | root of portable packages |
| `win_workman_default_lang` | `en_US` | locale hint of multi-locale roles (some detect it) |
| `win_workman_restart` | `true` | roles may reboot when needed |
| `win_workman_restart_timeout` | `600` | seconds to wait for a reboot |
| `win_workman_logoff_timeout_seconds` | `300` | wait for sessions to log off |
| `win_workman_installer_wait_timeout` | `120` | wait for Windows Installer to be idle (`Global\_MSIExecute`) before an install |
| `win_workman_installer_retry_codes` / `_retries` / `_retry_delay` | `[1601, 1618]` / `5` / `60` | retry an installer busy with another install |
| `win_workman_cleanup_uninstaller_dir` | `true` | after `off`, remove an install directory left with only the uninstaller's files (Inno's `unins000.exe`) |
| `win_workman_usr_path`, `win_workman_usr_targets`, `win_workman_usr_timeout`, `win_workman_usr_apply_timeout` | see [pkg_utils](roles/core/pkg_utils.md#per-user-deferred-install-usr) | per-user install |

## Repository layout

| Path | Holds |
|---|---|
| `roles/<role>/` | `vars/main.yaml` (schema), `defaults/`, `tasks/main.yaml` + `act_*.yaml`, `meta/main.yaml`, `meta/mcp.yaml` |
| `roles/pkg_utils/tasks/` | package workflow (`pkg_*`) and the shared `tasks_from` toolbox |
| `plugins/` | `filter/parse_tasks.py`, `lookup/file_copy_manifest.py`, `modules/seb_config.py` |
| `playbooks/win_workman.yaml` | the collection playbook |
| `mcp/` | MCP server ([mcp.md](mcp.md)) |
| `tools/` | `release.sh`, `fleet_skills.py` |
| `.fleet/skills/win-workman/` | skill for the assistant of cockpit-fleet; `roles-*.md` generated from the manifests |
| `docs/` | this documentation; `docs/todo/` the full backlog entries indexed by `TODO.md` |
