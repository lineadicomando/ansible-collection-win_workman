# lineadicomando.win_workman

[![GitHub tag](https://img.shields.io/github/v/tag/lineadicomando/ansible-collection-win_workman?label=version)](https://github.com/lineadicomando/ansible-collection-win_workman/tags)
[![License: GPL v3](https://img.shields.io/badge/license-GPL%20v3-blue)](./LICENSE)
[![CI](https://github.com/lineadicomando/ansible-collection-win_workman/actions/workflows/lint.yml/badge.svg)](https://github.com/lineadicomando/ansible-collection-win_workman/actions/workflows/lint.yml)

**Schema-driven management of Windows 11 workstations with Ansible**, built for school
labs: software deployment, system policy and maintenance through one interface.

- **Deploy**: install, upgrade and remove a catalog of software (browsers, dev tools,
  CAD, office, runtimes) from checksummed installers kept on the controller. No
  Chocolatey, no external feed.
- **Govern**: Windows Update, maintenance lock, autologon, OpenSSH hardening, domain
  membership, wallpaper and display settings across every profile, classroom tools
  (Veyon, Galène, Safe Exam Browser).
- **Maintain**: chkdsk, sfc, DISM component store, volume optimisation, scheduled
  shutdown, Wake-on-LAN.

Everything is a dash-separated **task string**, `<role>[-<action>[-<arg>…]]`:
`chrome`, `chrome-off`, `wu-pause-14`, `veyon-on-master`.

## Requirements

Windows 11 targets reachable over WinRM or SSH; on the controller `ansible.windows`,
`community.windows` ≥ 2.0.0 and `community.general` ≥ 8.0.0. The `galene` role builds
its Windows binary on the controller and needs Go ≥ 1.21 there.

## Installation

```yaml
# requirements.yml
collections:
  - name: git+https://github.com/lineadicomando/ansible-collection-win_workman
    type: git
    version: vX.Y.Z   # a release tag (see the badge); main follows every commit
```

```bash
ansible-galaxy collection install -r requirements.yml
```

Package versions change often and each batch is released as a patch version: pin a
tag to choose when an update reaches your hosts.

## Quick start

```yaml
- name: Manage workstation software
  hosts: lab_pcs
  roles:
    - role: lineadicomando.win_workman.dispatcher
      vars:
        win_workman_storage_path: /srv/software
        win_workman_tasks:
          - chrome
          - vscode
          - python312
          - wu-pause-14
```

Or from the command line:

```bash
ansible-playbook lineadicomando.win_workman.win_workman -i inventory -l lab_pcs \
  -e '{"todo": "chrome,vlc-off"}'
```

## Documentation

| Read | For |
|---|---|
| [docs/index.md](docs/index.md) | the catalog: every role, one line each, linked to its page |
| [docs/architecture.md](docs/architecture.md) | task strings, standard actions, package schema, global variables |
| [docs/roles/core/pkg_utils.md](docs/roles/core/pkg_utils.md) | schema fields and the shared task toolbox |
| [docs/mcp.md](docs/mcp.md) | the MCP server for AI assistants (`get_role_info`, `run_tasks`) |

## License

GPL-3.0-or-later. Author: Alessandro Gagliano — [lineadicomando.it](https://lineadicomando.it)
