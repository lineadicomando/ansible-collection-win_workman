# CLAUDE.md

`lineadicomando.win_workman`: Ansible collection managing Windows 11 lab
workstations. Conversation in Italian; code, docs and commits in English. Public repo:
no real site, host, domain or account names in files or commit messages.

## Start of a session

`git pull` (one clone per workstation, not synced), then `TODO.md` for open work. The
lab project `ansible-win_edulab`, checked out beside this repo, symlinks this working
tree under its `ansible_collections/`, so edits here take effect there at once; its
test VMs and MCP servers are where roles are run and tested.

## How it works, in one paragraph

Everything is a dash-separated task string `<role>-<action>-<arg…>`:
`plugins/filter/parse_tasks.py` splits it, the `dispatcher` role includes the role
named by `argv[0]`, which dispatches on `argv[1]`. Package roles delegate to
`pkg_utils` (`pkg_workflow` → `pkg_act_<action>`); management roles have their own
`tasks/act_<action>.yaml`. **A role name never contains a dash**: the parser would
read it as an action boundary (`display_scale`).

## Read these instead of exploring

`roles/` has 92 roles plus `dispatcher` and `pkg_utils`: grepping it is the
expensive way to answer what a doc answers.

| To find out | Read |
|---|---|
| Dispatch, task syntax, standard actions, providers, global variables, layout | `docs/architecture.md` |
| Which roles exist | `docs/index.md` |
| One role: actions, variables, traps | `docs/roles/{catalog,management,core}/<role>.md` |
| Actions and defaults as the MCP server sees them | `get_role_info` (win-workman MCP), live from `meta/mcp.yaml` |
| Schema fields, the `tasks_from` toolbox | `docs/roles/core/pkg_utils.md` |
| MCP server | `docs/mcp.md` |
| Open work | `TODO.md` (index), full entries in `docs/todo/` |

## Working rules

1. **Commits**: English, imperative subject, body with the reasoning and trade-offs.
2. **Reuse `pkg_utils`** (`include_role … tasks_from:`) before writing PowerShell:
   `profiles`, `logoff`, `user_sessions`, `restart`, `pending_restart`, `kill`,
   `services_stop`, `detect_sw`, `registry_read`, `download`, `win_copy`,
   `win_extract`, `win_path`, `shortcuts`, `start_process`, `run_as_system`,
   `wait_installer`, `win_clean_temp`, `remote_tmp` (inputs and outputs in
   `pkg_utils.md`). `profiles` returns `win_workman_profiles` (`SID`, `Name`,
   `LocalPath`, `HiveRoot`, `HivePath`, `HiveExists`, `HiveMounted`, `Loaded` = active
   interactive session). Writing an `HKCU` setting into every profile, users who never
   logged on included: copy `roles/wallpaper/` or `roles/display_scale/` (force
   logoff, select `Loaded == false and HiveExists == true`, loop `win_regedit` over
   `profiles | product(entries)`).
3. **Adding a role** (skill `win-workman-new-role` in the project repo): mirror one
   of the same family. `vars/main.yaml` (`win_workman_<role>_schema` with `name` and
   `default_action`), `tasks/main.yaml` (includes `act_{{ win_workman_action or
   default_action }}`), `meta/main.yaml` (`dependencies: [pkg_utils]`,
   `allow_duplicates: true`), `meta/mcp.yaml` (required: without it the role is
   invisible to MCP and to the cockpit-fleet skill), the page
   `docs/roles/<family>/<role>.md` following `docs/roles/TEMPLATE.md`, and one row
   in `docs/index.md`. Variables `win_workman_<role>_*`: user-overridable in
   `defaults/`, computed in `vars/`.
4. **`on`/`off` everywhere**: every schema has a `default_action`; where a role's
   verbs differ (`set`/`reset`), wire `on`/`off` as aliases.
5. **Lint is the gate**: CI runs `ansible-lint --profile production` (ansible-core
   2.20.4) and `python3 tools/fleet_skills.py --check`, in
   `.gitea/workflows/lint.yml` (git.cmdln.it, where it is pushed) and
   `.github/workflows/lint.yml` (GitHub mirror): keep the two in step. Run lint on what
   you touched, and `python3 tools/fleet_skills.py` after changing any
   `meta/mcp.yaml`.
6. **Release often** with `tools/release.sh patch|minor [--pin FILE] [--dry-run]`:
   projects pin a tag. `patch` after a package bump or a fix, `minor` after a new
   role, action or default behaviour; same-day commits can share one. It bumps
   `galaxy.yml`, tags, pushes branch and tag in **one atomic push** (two pushes start
   two runs of the GitHub mirror, one is rejected and the tag never arrives), then
   `--pin` moves the project's requirements file to the tag and pushes it.
7. **Docs follow the code** in the same commit: role page, manifest, index row;
   a finished TODO entry is deleted from `TODO.md` and its file.

## PowerShell traps already paid for

Both fail **silently**.

- **`ConvertFrom-Json` does not unroll arrays**: a multi-element array comes back as
  one object; `@(...)` and `ForEach-Object` yield one element with every value
  concatenated. Works with one element, breaks with two. Iterate with
  `foreach ($x in (ConvertFrom-Json -InputObject $Json))`.
- **`Start-Process -Wait` waits on the job object**, i.e. every descendant: a task
  hangs after an installer that left a helper running. NSIS uninstallers that
  re-spawn into temp depend on it, so do not change it globally; wait for the process
  alone with `-PassThru` + `WaitForExit()` and a timeout. (`pkg_utils/start_process`
  has a `win_workman_exec_wait_tree` switch for this, broken: see `TODO.md`.)
