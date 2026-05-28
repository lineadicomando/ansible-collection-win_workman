# lineadicomando.win_workman

[![GitHub tag](https://img.shields.io/github/v/tag/lineadicomando/ansible-collection-win_workman?label=version)](https://github.com/lineadicomando/ansible-collection-win_workman/tags)
[![License: GPL v3](https://img.shields.io/badge/license-GPL%20v3-blue)](./LICENSE)
[![CI](https://github.com/lineadicomando/ansible-collection-win_workman/actions/workflows/ci.yml/badge.svg)](https://github.com/lineadicomando/ansible-collection-win_workman/actions/workflows/ci.yml)
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

## Why not Chocolatey?

Chocolatey is the de-facto standard for Windows package management in Ansible,
but it depends on an external service: the public feed has rate limits and
private feeds require a paid subscription. `win_workman` stores installers on
a path you control (UNC share, local directory, S3 mount) and verifies them via
checksum — fully air-gap friendly.

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
The default action is `on` (install). See [Architecture](#architecture) for
the full syntax.

---

## Software catalog

Ready-to-use schema roles, grouped by category. All support `on` (install),
`off` (uninstall), `download`, and `info` actions.

### Browsers

| Role | Software | Extra actions |
|---|---|---|
| `chrome` | Google Chrome (Enterprise MSI, 32/64-bit) | `privacy-on`, `privacy-off`, `rm-profile` |
| `firefox` | Mozilla Firefox (locale-aware) | `privacy-on`, `privacy-off`, `rm-profile` |
| `edge` | Microsoft Edge (policy only, uninstall not supported) | `privacy-on`, `privacy-off`, `rm-profile` |
| `brave` | Brave Browser | — |
| `seb` | Safe Exam Browser (Windows 3.x) | — |

### Developer tools

`vscode` · `git` · `embarcadero_devcpp` · `orwell_devcpp` · `laragon` · `mysql_server`
· `mysql_workbench` · `dbeaver` · `postman` · `python310` · `python311` · `python312`
· `python313` · `python314`

### Graphics, CAD & Multimedia

`gimp` · `inkscape` · `blender` · `sketchup2026` · `autocadlt2026_en` · `autocadlt2026_it`
· `vlc` · `puredata`

### Education & Productivity

`geogebra` · `geogebra5` · `libreoffice` · `zoom`

### Utilities & Runtimes

`p7zip` · `windirstat` · `ntop` · `winfsp` · `vcredist14` · `virtiogt` · `nircmd`

> Contributions to the catalog are welcome. See [how schema roles work](#schema-roles).

---

## Workstation management

Additional roles for system-level operations, all accessible through the same
dispatcher interface.

### System & OS

| Role | Actions | Description |
|---|---|---|
| `optimize` | `on` | Volume optimisation and TRIM / defrag |
| `wu` | `on`, `off`, `pause_on`, `pause_off`, `pause_max` | Windows Update control |
| `wim` | `check`, `scan`, `repair` | DISM component store health |
| `sfc` | `on` | System File Checker |
| `chkdsk` | `on` | Check Disk |
| `patchcleaner` | `on`, `off`, `download` | WinSxS / superseded update cleanup |
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
| `shutdown` | `on` | Controlled system shutdown |

### Network & Security

| Role | Actions | Description |
|---|---|---|
| `secure_ssh` | `on`, `off` | Harden OpenSSH server |
| `veyon` | `on`, `off`, `config` | Veyon classroom agent (install + key/network config) |
| `ping` | `on` | Connectivity test |
| `wol` | `on` | Send Wake-on-LAN magic packets |

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
| `wu-pause_on` | `wu` | `pause_on` | — |

### Schema roles

Each software role exposes a `win_workman_<schema>_schema` variable in
`vars/main.yaml` describing the package:

```yaml
win_workman_vscode_schema:
  name: Visual Studio Code
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
| `win_workman_action_default` | `"on"` | Default action when omitted from the task string |
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
