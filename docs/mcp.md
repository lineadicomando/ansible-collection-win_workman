# MCP server

`mcp/server.py` ("win-workman") exposes the collection to MCP clients (Claude Code,
Claude Desktop) over stdio. It reads role manifests (`roles/<role>/meta/mcp.yaml`)
live from the tree, so a new or changed manifest is visible with no restart, and runs
tasks through the collection playbook.

```
MCP client ─stdio─► mcp/server.py
                     ├─ get_role_info          → mcp/roles.py reads meta/mcp.yaml
                     ├─ run_tasks              → ansible-playbook lineadicomando.win_workman.win_workman
                     └─ run_status / wait_run  → mcp/runlog.py, the run logs
```

| File | Does |
|---|---|
| `server.py` | tool schemas and dispatch |
| `roles.py` | `list_roles`, `get_role_info`; also used by `tools/fleet_skills.py` |
| `runner.py` | builds and validates the `ansible-playbook` command |
| `runlog.py` | logged, supervised runs; byte-identical copy in the project repo (`ansible-win_edulab/mcp/`) |

## Setup

Python 3.12+, `pip install -r mcp/requirements.txt` (`mcp`, `jsonschema`, `pyyaml`),
`ansible-playbook` in `PATH`, the collection installed or symlinked.

| Environment | Meaning |
|---|---|
| `ANSIBLE_PROJECT_ROOT` | required: project with `inventories/<name>/hosts.yaml` |
| `ANSIBLE_MCP_LOG_DIR` | optional: log directory, default `<root>/logs` |

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

Each run writes `<logs>/<timestamp>-<label>.log` while it runs, repoints
`<logs>/latest.log` at it, and creates `<log>.done` when it ends (what a client waits
on). Secrets passed as `sensitive_vars` are masked in the log.

## Tools

### `get_role_info(role)`

Returns, from the manifest: `display_name`, `common_actions` (each with `handled_by`:
`pkg_utils` or the role when it reimplements the action, and `default`),
`custom_actions`, `defaults` (variable, type, default, description), `notes`; for
package roles `install_scopes` (`sys`, `usr`), and `usr_actions` when `usr` is one.

### `run_tasks`

| Parameter | Default | Meaning |
|---|---|---|
| `t` | required | task strings, e.g. `["chrome-info", "vlc-off"]` |
| `l` | `win_managed` | limit (host or group); `lab_win` in an inventory that still has only the old name. `all` reaches every host of the inventory, a DC too: only when asked |
| `inventory` | `school` | name under `inventories/` |
| `extra_vars` | — | role variables as extra vars; `t`, `todo`, `ansible_*` refused |
| `sensitive_vars` | — | like `extra_vars`, for secrets: passed in a private temp file, masked in log, output and preview |
| `forks` | Ansible's (5) | hosts in parallel; set it to the host count for a whole lab |
| `preview` | `false` | return the command, run nothing |
| `background` | `false` | return a run id at once; follow it with `run_status` / `wait_run` |

### `run_status(run="latest", since_line=0, max_lines=200)`

New output of a background run since a line, and whether it is still running.

### `wait_run(run="latest", timeout=900, since_line=0, max_lines=200)`

Blocks until the run ends or `timeout` (5–3600 s) runs out, then returns the output;
a run still going is marked so, with the line to resume from.

## Role manifest (`meta/mcp.yaml`)

Every role has one: without it the role is invisible to `get_role_info` and missing
from the skill of cockpit-fleet (`.fleet/skills/win-workman/`, written from the
manifests by `python3 tools/fleet_skills.py`; CI runs it with `--check`).

```yaml
display_name: Google Chrome
custom_actions:                 # beyond the standard package actions
  - name: privacy
    description: Apply the privacy policies
defaults:                       # user-overridable variables (defaults/main.yaml)
  - var: win_workman_chrome_shortcuts
    type: bool                  # bool | str | int | list | dict
    default: false
    description: Create shortcuts on Desktop and Start Menu
notes: >
  Free text for the assistant: argument tokens, side effects, traps.
```

The standard package actions are not listed: `roles.py` derives them from
`roles/pkg_utils/vars/main.yaml`.

## Collection playbook

`playbooks/win_workman.yaml`, FQCN `lineadicomando.win_workman.win_workman`: takes
`todo` (comma-separated string or list; `t` is its old name, `todo` wins) and runs the
`dispatcher` with it.

```bash
ansible-playbook lineadicomando.win_workman.win_workman \
  -i inventories/school/hosts.yaml -l win_managed -e '{"todo": "chrome,vscode"}'
```
