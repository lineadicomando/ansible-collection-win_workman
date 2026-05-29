# Architecture

> **Work in progress** — preliminary draft.

---

## Overview

The collection is built on a **dispatcher + schema** pattern. A single role
(`dispatcher`) is the only entry point a playbook needs to call. It parses a
list of task strings, resolves each one to a *schema role*, and delegates
execution. All low-level package operations are centralised in `pkg_utils`.

```
win_workman_tasks (list of strings)
        │
        ▼  lineadicomando.win_workman.parse_tasks (Jinja2 filter)
        │
        ▼
  dispatcher role
        │  include_role: lineadicomando.win_workman.<schema>
        ▼
  schema role  (e.g. chrome, vscode, veyon …)
        │  include_role: pkg_utils  tasks_from: pkg_workflow
        ▼
  pkg_utils — download / install / uninstall / info / …
```

## Entry points

| Entry point | How to call | When to use |
|---|---|---|
| `lineadicomando.win_workman.dispatcher` role | `roles:` block in a playbook | Standard playbook usage |
| `lineadicomando.win_workman.win_workman` playbook (FQCN) | `ansible-playbook lineadicomando.win_workman.win_workman` | CLI / MCP server |

The collection playbook (`playbooks/win_workman.yaml`) accepts `t` as a
comma-separated extra-var string, normalises it into a list, and delegates to
`dispatcher`. It is the entry point used by the [MCP server](mcp.md).

---

## Task string syntax

```
<schema>[-<action>[-<arg1>[-<arg2>…]]]
```

| Token | Position | Description |
|---|---|---|
| `schema` | `argv[0]` | Name of the target schema role |
| `action` | `argv[1]` | Operation to perform; if omitted, the role uses its own `win_workman_{role}_schema.default_action` |
| `arg1…` | `argv[2+]` | Role-specific arguments (e.g. Veyon mode) |

### Examples

| Task string | Schema | Action | Args |
|---|---|---|---|
| `chrome` | `chrome` | *(default: `on`)* | — |
| `chrome-on` | `chrome` | `on` | — |
| `chrome-off` | `chrome` | `off` | — |
| `veyon-on-student` | `veyon` | `on` | `student` |
| `veyon-config-teacher` | `veyon` | `config` | `teacher` |
| `python312-download` | `python312` | `download` | — |
| `wallpaper-set` | `wallpaper` | `set` | — |

### Parsed object

The filter produces one dict per task:

```python
{
  "task":   "veyon-config-teacher",   # original string
  "schema": "veyon",                  # argv[0]
  "act":    "config",                 # argv[1], or "" if omitted — default applied at role level
  "argc":   3,                        # len(argv)
  "argv":   ["veyon", "config", "teacher"]
}
```

The dispatcher exposes these as `win_workman_action`, `win_workman_task_argv`,
`win_workman_task_argc`, and `win_workman_task` inside each included schema role.

---

## Actions

### Standard package actions (handled by `pkg_utils`)

| Action | Description |
|---|---|
| `on` | Install or upgrade the package |
| `off` | Uninstall the package |
| `download` | Download installer to `win_workman_storage_path` only |
| `copy` | Copy installer from storage to remote temp without installing |
| `info` | Report installation state without making changes |
| `is_present` | Assert that the package is installed (fails the play if not) |

### Role-specific actions

Some roles extend the standard set with their own actions or support a subset:

| Role | Actions |
|---|---|
| `chrome` | `on`, `off`, `privacy-on`, `privacy-off`, `rm-profile` |
| `firefox` | `on`, `off`, `privacy-on`, `privacy-off`, `rm-profile` |
| `edge` | `privacy-on`, `privacy-off`, `rm-profile` (uninstall not supported) |
| `wallpaper` | `set`, `reset`, `lock`, `unlock` |
| `wu` | `run` *(default)*, `on`, `off`, `pause`, `resume`, `max_pause_days`, `is_paused`, `policy_standard` |
| `veyon` | `on`, `off`, `config` |
| `lock` | `on`, `off` |
| `autologon` | `on`, `off` |
| `secure_ssh` | `on`, `off` |
| `ms_account` | `on`, `off` |
| `oobe` | `on`, `off` |
| `seb` | `on`, `off`, `deploy`, `undeploy`, `config_key` |
| `chkdsk` | `on` |
| `sfc` | `on` |
| `logoff` | `on` |
| `restart` | `on` |
| `shutdown` | `on`, `wait` |
| `ping` | `on` |
| `wol` | `on` |
| `wim` | `check` *(default)*, `scan`, `repair`, `on` *(alias for `check`)* |

---

## Package providers

Each schema role defines a `win_workman_<schema>_schema` variable in
`vars/main.yaml`. The `package.provider` key controls how `pkg_utils`
installs and detects the software.

### `registry` (default)

Standard installer (MSI, NSIS, Inno Setup, …). Detected via the Windows
Uninstall registry key using `package.searchName`.

```yaml
win_workman_vscode_schema:
  name: Visual Studio Code
  package:
    setup_file: VSCodeSetup-x64-1.108.2.exe
    searchName: "Microsoft Visual Studio Code"
    version: "1.108.2"
    provider: registry
    install_args:
      - /VERYSILENT
      - /TASKS=desktopicon,addtopath
    uninstall_args:
      - /VERYSILENT
  files:
    - filename: VSCodeSetup-x64-1.108.2.exe
      url: https://…/VSCodeUserSetup-x64-1.108.2.exe
      checksum: sha256:…
```

### `portable`

Files are extracted or copied to `win_workman_portable_path`
(`C:\PortableApps` by default). No registry entry. Detection is based on
filesystem presence under the portable path.

```yaml
package:
  provider: portable
  portable_dir: MyApp          # subdirectory under win_workman_portable_path
files:
  - filename: myapp.7z
    url: https://…
    checksum: sha256:…
    extract: 7z                # optional: extract with 7-Zip after download
    dest_dir: MyApp
```

---

## Global variables

These variables are meaningful across the whole collection.

| Variable | Default | Description |
|---|---|---|
| `win_workman_tasks` | `[]` | List of task strings for the dispatcher |
| `win_workman_storage_path` | `~/win_workman_storage` | Path (controller-side) where installers are stored |
| `win_workman_remote_tmp` | `C:\Windows\Temp\ansible` | Temp directory on the Windows target |
| `win_workman_portable_path` | `C:\PortableApps` | Root directory for portable applications |
| `win_workman_restart_timeout` | `180` | Seconds to wait after a reboot |
| `win_workman_restart` | `true` | Whether schema roles may trigger a reboot |
| `win_workman_default_lang` | `en_US` | Default locale hint for multi-locale roles |

### Maintenance mode variables (used by `lock`, `pkg_utils`)

| Variable | Default | Description |
|---|---|---|
| `win_workman_mode_title` | `"Maintenance in progress"` | Legal notice title on login screen |
| `win_workman_mode_text` | *(see defaults)* | Legal notice body text |
| `win_workman_mode_force_logoff` | `true` | Force active sessions to log off when locking |
| `win_workman_mode_interactive_logon_users` | `[Administrators]` | Groups allowed to log in during maintenance |
