# dispatcher — Entry point of the collection

Parses `win_workman_tasks` with the `parse_tasks` filter and includes, for each task
string, the role named by its first token. The playbook
`lineadicomando.win_workman.win_workman` wraps it for the CLI (`-e '{"todo": "…"}'`);
the task syntax is in [architecture](../../architecture.md#task-strings).

```yaml
- name: Manage workstations
  hosts: lab_a
  roles:
    - role: lineadicomando.win_workman.dispatcher
      vars:
        win_workman_tasks: [chrome-on, vscode, zoom-off, veyon-config]
```

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_tasks` | `[]` | task strings, run in order |

Set in the scope of each included role:

| Variable | Value |
|---|---|
| `win_workman_action` | `argv[1]`, `""` when omitted (the role falls back to its schema's `default_action`) |
| `win_workman_task` | the parsed task: `{task, schema, act, argc, argv}` |
| `win_workman_task_argv`, `win_workman_task_argc` | tokens and their count |

## Notes

- The filter fails on a task whose first token is not a role directory of the
  collection, or is `dispatcher`/`pkg_utils`, naming the task.
- Before the first task that connects to the host it includes `pkg_utils`
  `remote_tmp` once per run ([pkg_utils](pkg_utils.md#remote-temporary-directory)).
  Schemas listed in `_win_workman_controller_schemas` (`vars/main.yaml`: `wol`) run on
  the controller and do not trigger it, so `wol,chrome` can wake a powered-off PC first.
