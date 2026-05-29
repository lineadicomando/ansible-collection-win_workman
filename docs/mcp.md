# MCP Server

The collection ships an optional **Model Context Protocol (MCP) server** that
exposes win_workman operations to AI assistants (Claude Desktop, Claude Code,
or any MCP-compatible client).

---

## Overview

```
AI assistant (MCP client)
        │
        ▼  MCP stdio transport
  mcp/server.py  ("win-workman")
        │
        ├─ get_role_info  →  reads meta/mcp.yaml from the role directory
        │
        └─ run_tasks  →  ansible-playbook lineadicomando.win_workman.win_workman
```

The server reads role metadata from each role's `meta/mcp.yaml` manifest and
delegates task execution to the collection playbook `playbooks/win_workman.yaml`
(invokable by FQCN `lineadicomando.win_workman.win_workman`).

---

## Prerequisites

- Python 3.12+ on the controller
- `mcp` Python package installed (`pip install mcp`)
- `ansible-playbook` in `PATH`
- Collection installed (see [installation](../README.md#installation))
- An Ansible project directory with the expected structure:
  ```
  <project_root>/
  └── inventories/
      └── <inventory_name>/
          └── hosts.yaml
  ```

---

## Configuration

The server requires one environment variable:

| Variable | Description |
|---|---|
| `ANSIBLE_PROJECT_ROOT` | Absolute path to your Ansible project directory |

---

## Wiring into Claude Desktop

Add the server to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "win-workman": {
      "command": "python",
      "args": ["/path/to/ansible-collection-win_workman/mcp/server.py"],
      "env": {
        "ANSIBLE_PROJECT_ROOT": "/path/to/your/ansible-project"
      }
    }
  }
}
```

---

## Tools

### `get_role_info`

Returns the display name, custom actions, configurable defaults, and notes for
a single win_workman role. Data is read from the role's `meta/mcp.yaml` manifest.

**Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `role` | string | yes | Role name (e.g. `chrome`, `vscode`, `wu`) |

**Returns** — JSON object with the following keys:

| Key | Description |
|---|---|
| `display_name` | Human-readable name |
| `custom_actions` | List of role-specific actions beyond the standard package actions |
| `defaults` | Configurable role variables with type, default value, and description |
| `notes` | Free-text notes about the role |

---

### `run_tasks`

Runs one or more win_workman tasks on an Ansible host or group by invoking
`ansible-playbook lineadicomando.win_workman.win_workman`.

**Parameters**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `t` | list of strings | yes | — | Task list (e.g. `["chrome"]`, `["chrome-off", "vlc-on"]`) |
| `l` | string | no | `"all"` | Ansible limit: hostname or group name |
| `inventory` | string | no | `"school"` | Inventory name under `inventories/` |
| `preview` | boolean | no | `false` | Return the command string without executing |

The tasks follow the same dash-separated syntax as the collection:
`<role>` or `<role>-<action>` (e.g. `chrome`, `chrome-off`, `wu-pause-14`).

**Example** — install Chrome on a single host (preview mode):

```
run_tasks(t=["chrome"], l="pc01", preview=true)
```

Returns:

```
Command to run:

  ansible-playbook lineadicomando.win_workman.win_workman \
  -i '/srv/ansible/inventories/school/hosts.yaml' \
  -l 'pc01' \
  -e '{"t": "chrome"}'

No command executed.
```

---

## Role manifest format (`meta/mcp.yaml`)

Each role may optionally provide a `meta/mcp.yaml` file. The server falls back
to safe defaults when the file is absent.

```yaml
# meta/mcp.yaml — all keys are optional
display_name: Google Chrome           # human-readable name (default: role directory name)

custom_actions:                       # actions beyond the standard package set
  - name: privacy                     # action token used in task strings
    description: >
      Apply privacy Group Policy (disables telemetry, sync, etc.)

defaults:                             # configurable role variables
  - var: win_workman_chrome_shortcuts
    type: bool                        # bool | str | int | list
    default: false
    description: Create shortcuts on Desktop and Start Menu

notes: >
  Free-text notes visible to the AI assistant.
  Accepts '32bit' task argument. Closes running Chrome before install/uninstall.
```

Standard package actions (`on`, `off`, `download`, `copy`, `info`, `is_present`)
are common to all catalog roles and do not need to be listed in `custom_actions`.

---

## Collection playbook

`playbooks/win_workman.yaml` is the entry point used by the MCP server. It is
also usable standalone:

```bash
ansible-playbook lineadicomando.win_workman.win_workman \
  -i inventories/school/hosts.yaml \
  -l lab_win \
  -e '{"t": "chrome,vscode"}'
```

The `t` extra-var accepts a comma-separated task list. The playbook normalises
it into a list and passes it to the `dispatcher` role.
