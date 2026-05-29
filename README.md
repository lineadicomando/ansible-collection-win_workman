# lineadicomando.win_workman

[![GitHub tag](https://img.shields.io/github/v/tag/lineadicomando/ansible-collection-win_workman?label=version)](https://github.com/lineadicomando/ansible-collection-win_workman/tags)
[![License: GPL v3](https://img.shields.io/badge/license-GPL%20v3-blue)](./LICENSE)
[![CI](https://github.com/lineadicomando/ansible-collection-win_workman/actions/workflows/lint.yml/badge.svg)](https://github.com/lineadicomando/ansible-collection-win_workman/actions/workflows/lint.yml)
[![GitHub issues](https://img.shields.io/github/issues/lineadicomando/ansible-collection-win_workman)](https://github.com/lineadicomando/ansible-collection-win_workman/issues)


> **Work in progress** — This README is a preliminary draft. Role-level documentation,
> variable references, and usage examples are incomplete and subject to change.

**Schema-driven Windows workstation management for Ansible —
software deployment, system governance, and maintenance from a single interface.**

`win_workman` manages Windows 11 workstations across three dimensions:

- **Deploy** — install, upgrade, and uninstall a growing catalog of software packages
  (browsers, dev tools, CAD, office, runtimes) using a schema-based approach with
  checksum verification and offline-friendly installer storage. No Chocolatey, no
  external feed, no rate limits.

- **Govern** — enforce system-level policy: Windows Update control, OS hardening,
  user session management, automatic logon, SSH configuration, and classroom
  infrastructure (Veyon monitoring, Safe Exam Browser).

- **Maintain** — run recurring maintenance operations: disk check, system file repair,
  DISM store cleanup, volume optimisation, and targeted patch removal.

All operations share the same dispatcher interface: a list of dash-separated task
strings dispatched to schema roles, keeping playbooks declarative and readable
regardless of what the task actually does.

---

## Requirements

| Dependency | Version |
|---|---|
| `ansible.windows` | >= 2.0.0 |
| `community.windows` | >= 2.0.0 |
| `community.general` | >= 8.0.0 |

Target hosts must run Windows 11. WinRM or SSH connectivity is required.

---

## Installation

```yaml
# requirements.yml
collections:
  - name: git+https://github.com/lineadicomando/ansible-collection-win_workman
    type: git
    version: main
```

```bash
ansible-galaxy collection install -r requirements.yml
```

---

## Quick start

```yaml
- name: Manage workstation software
  hosts: lab_pcs
  roles:
    - role: lineadicomando.win_workman.dispatcher
      vars:
        win_workman_storage_path: /mnt/software
        win_workman_tasks:
          - chrome
          - vscode
          - python312
```

Tasks are dash-separated strings: `<schema>[-<action>[-<arg>...]]`.
When the action token is omitted, each role uses its own default
(`win_workman_{role}_schema.default_action`); most package roles default to
`on` (install), `wu` defaults to `run`, `wim` to `check`.
See [Architecture](#architecture) for the full syntax.

---

## Software catalog

All catalog roles support the standard package actions: `on` (install), `off` (uninstall),
`download`, `copy`, `info`, `is_present`. Additional role-specific actions are listed in the
**Extra actions** column.

### Browsers

| Role | Software | Extra actions |
|---|---|---|
| `chrome` | Google Chrome (Enterprise MSI) | `rm`, `privacy` |
| `firefox` | Mozilla Firefox (locale-aware) | `rm`, `privacy` |
| `edge` | Microsoft Edge (uninstall not supported) | `rm`, `privacy` |
| `brave` | Brave Browser | — |
| `opera` | Opera Browser | — |
| `vivaldi` | Vivaldi | — |
| `seb` | Safe Exam Browser 3.x | `deploy`, `undeploy`, `config_key` |

### Developer tools

| Role | Software | Extra actions |
|---|---|---|
| `vscode` | Visual Studio Code | — |
| `git` | Git | — |
| `embarcadero_devcpp` | Embarcadero Dev-C++ | — |
| `orwell_devcpp` | Orwell Dev-C++ | — |
| `laragon` | Laragon | — |
| `mysql_server` | MySQL Server | — |
| `mysql_workbench` | MySQL Workbench | — |
| `dbeaver` | DBeaver | — |
| `postman` | Postman | — |
| `netbeans` | Apache NetBeans | — |
| `python310` | Python 3.10 | — |
| `python311` | Python 3.11 | — |
| `python312` | Python 3.12 | — |
| `python313` | Python 3.13 | — |
| `python314` | Python 3.14 | — |

### Graphics, CAD & Multimedia

| Role | Software | Extra actions |
|---|---|---|
| `gimp` | GIMP | — |
| `inkscape` | Inkscape | — |
| `blender` | Blender | — |
| `sketchup2026` | SketchUp 2026 | — |
| `autocadlt2026` | AutoCAD LT 2026 (locale auto-detected) | — |
| `tinycad` | TinyCAD | — |
| `vlc` | VLC media player | — |
| `puredata` | Pure Data | — |

### Education & Productivity

| Role | Software | Extra actions |
|---|---|---|
| `geogebra` | GeoGebra Calculator Suite | — |
| `geogebra5` | GeoGebra Classic 5 | — |
| `libreoffice` | LibreOffice | `rm_data` |
| `zoom` | Zoom | — |

### Documents & Editors

| Role | Software | Extra actions |
|---|---|---|
| `adobe_reader_dc` | Adobe Acrobat Reader DC | — |
| `foxit_pdf_reader` | Foxit PDF Reader | — |
| `notepadpp` | Notepad++ | — |
| `winmerge` | WinMerge | — |

### Utilities & Runtimes

| Role | Software | Extra actions |
|---|---|---|
| `p7zip` | 7-Zip | — |
| `peazip` | PeaZip | — |
| `winrar` | WinRAR | — |
| `filezilla` | FileZilla Client | — |
| `winscp` | WinSCP | — |
| `putty` | PuTTY | — |
| `powertoys` | Microsoft PowerToys | — |
| `rustdesk` | RustDesk | — |
| `windirstat` | WinDirStat | — |
| `ntop` | NTop | — |
| `winfsp` | WinFsp | — |
| `vcredist14` | Visual C++ Redistributable 14 | — |
| `virtiogt` | VirtIO Win Guest Tools | — |
| `nircmd` | NirCmd | — |
| `patchcleaner` | PatchCleaner | — |

> Contributions to the catalog are welcome. See [how schema roles work](#schema-roles).

---

## Workstation management

Additional roles for system-level operations, all accessible through the same
dispatcher interface.

### System & OS

| Role | Actions | Description |
|---|---|---|
| `optimize` | `on` | Volume optimisation and TRIM / defrag |
| `wu` | `run` *(default)*, `on`, `off`, `pause`, `resume`, `max_pause_days`, `is_paused`, `policy_standard` | Windows Update control |
| `wim` | `check` *(default)*, `scan`, `repair`, `on` *(alias for `check`)* | DISM component store health |
| `sfc` | `on` | System File Checker |
| `chkdsk` | `on` | Check Disk |
| `oobe` | `on`, `off` | Suppress Out-of-Box Experience prompts |
| `widgets` | `on`, `off` | Windows 11 Widgets panel (news and interests) |
| `wallpaper` | `on`, `off`, `set`, `reset`, `lock`, `unlock` | Wallpaper across all user profiles |

### Session & Access

| Role | Actions | Description |
|---|---|---|
| `autologon` | `on`, `off` | Automatic logon for a local account |
| `lock` | `on`, `off` | Maintenance mode: login banner + logon restrictions |
| `ms_account` | `on`, `off` | Block or allow Microsoft account sign-in |
| `logoff` | `on` | Force logoff all interactive sessions |
| `restart` | `on`, `if-pending` | Controlled system restart |
| `shutdown` | `on`, `wait` | Controlled system shutdown |

### Network & Security

| Role | Actions | Description |
|---|---|---|
| `secure_ssh` | `on`, `off` | Harden OpenSSH server |
| `veyon` | `on`, `off`, `config` | Veyon classroom agent (install + key/network config) |
| `ping` | `on` | Connectivity test |
| `wol` | `on` | Send Wake-on-LAN magic packets |

---

## MCP integration

The collection includes an optional MCP (Model Context Protocol) server that
lets AI assistants (Claude Desktop, Claude Code) query role information and
execute tasks directly.

```json
{
  "mcpServers": {
    "win-workman": {
      "command": "python",
      "args": ["/path/to/ansible-collection-win_workman/mcp/server.py"],
      "env": { "ANSIBLE_PROJECT_ROOT": "/path/to/your/ansible-project" }
    }
  }
}
```

See [`docs/mcp.md`](docs/mcp.md) for setup instructions, tool reference, and
the `meta/mcp.yaml` role manifest format.

---

## Architecture

The collection is built around a **dispatcher + schema** pattern:

```
win_workman_tasks (list of strings)
        │
        ▼  parse_tasks filter (Jinja2)
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

### Task string syntax

```
<schema>[-<action>[-<arg1>[-<arg2>…]]]
```

| Task string | Schema | Action | Args |
|---|---|---|---|
| `chrome` | `chrome` | *(default: `on`)* | — |
| `chrome-off` | `chrome` | `off` | — |
| `veyon-config-student` | `veyon` | `config` | `student` |
| `chrome-on-32bit` | `chrome` | `on` | `32bit` |
| `wu` | `wu` | *(default: `run`)* | — |
| `wu-pause-14` | `wu` | `pause` | `14` |

### Schema roles

Each software role exposes a `win_workman_<schema>_schema` variable in
`vars/main.yaml` describing the package:

```yaml
win_workman_vscode_schema:
  name: Visual Studio Code
  default_action: !!str on      # action used when task string has no action token
  package:
    setup_file: VSCodeSetup-x64-1.108.2.exe
    searchName: "Microsoft Visual Studio Code"
    version: "1.108.2"
    provider: registry          # registry | portable
    install_args: [/VERYSILENT]
    uninstall_args: [/VERYSILENT]
  files:
    - filename: VSCodeSetup-x64-1.108.2.exe
      url: https://…
      checksum: sha256:…
```

`pkg_utils` reads this schema and handles download, detection, install,
uninstall, and shortcut management. To add a new software role to the catalog,
define the schema variable and call `pkg_utils tasks_from: pkg_workflow`.

---

## Key variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_tasks` | `[]` | List of task strings for the dispatcher |
| `win_workman_storage_path` | `~/win_workman_storage` | Controller-side path for installer storage |
| `win_workman_remote_tmp` | `C:\Windows\Temp\ansible` | Temp directory on the Windows target |
| `win_workman_portable_path` | `C:\PortableApps` | Root directory for portable applications |
| `win_workman_restart_timeout` | `180` | Seconds to wait after a reboot |
| `win_workman_restart` | `true` | Allow roles to trigger a reboot when needed |

Role-specific variables follow the pattern `win_workman_<schema>_*`.
See [`docs/`](docs/index.md) for full per-role documentation.

---

## License

GPL-3.0-or-later

## Author

Alessandro Gagliano — [lineadicomando.it](https://lineadicomando.it)
