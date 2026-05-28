# Role: dispatcher

> **Work in progress** — preliminary draft.

Entry point of the collection. Parses `win_workman_tasks` and includes the
matching schema role for each item.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_tasks` | `[]` | List of task strings to execute |

## Variables set for each included role

The dispatcher sets these variables in the scope of each schema role:

| Variable | Source |
|---|---|
| `win_workman_action` | `argv[1]` of the task string, or `""` if omitted; each schema role resolves its own default via `win_workman_{role}_schema.default_action` |
| `win_workman_task` | Full parsed task object |
| `win_workman_task_argv` | List of tokens from the task string |
| `win_workman_task_argc` | Number of tokens |

---

## Usage

```yaml
- name: Manage workstations
  hosts: lab_pcs
  roles:
    - role: lineadicomando.win_workman.dispatcher
      vars:
        win_workman_tasks:
          - chrome-on
          - vscode
          - zoom-off
          - veyon-config-student
```

For the task string syntax see [architecture.md](../architecture.md).
