# CLAUDE.md

Agent instructions for `lineadicomando.win_workman` — an Ansible collection that
manages Windows 11 workstations in school labs.

## The one thing to understand first

Everything is driven by **dash-separated task strings**: `<schema>-<action>-<arg…>`.
`plugins/filter/parse_tasks.py` splits them, the `dispatcher` role resolves
`argv[0]` to a role of the same name, and that role dispatches on `argv[1]`.
Package roles delegate the actual work to `pkg_utils`; management roles
implement their own `tasks/act_<action>.yaml`.

Consequence worth remembering: **a role name can never contain a dash** — the
parser would read it as an action boundary. Use underscores (`display_scale`).

## Read these instead of exploring

`roles/` holds over 70 roles plus `dispatcher` and `pkg_utils`. Grepping across it is
almost always the expensive way to answer a question that a doc already answers.

| To find out | Read |
|---|---|
| How dispatch, task syntax, actions, and providers work | `docs/architecture.md` |
| Which roles exist and what each one covers | `docs/index.md` (catalog table) |
| What a specific role does, its actions and variables | `docs/roles/{catalog,management}/<role>.md` |
| A role's actions/defaults as the MCP server sees them | `roles/<role>/meta/mcp.yaml` |
| The package schema fields | `docs/roles/core/pkg_utils.md` |
| What is planned but not built, and why | `TODO.md` — entries carry status and rationale |

Prefer the `win-workman` MCP server's `get_role_info` over reading files when the
question is "what actions does X support": it returns exactly that, already
structured. It reads `meta/mcp.yaml` live from this working tree, so a role added
now is visible immediately, with no server restart.

## Working rules

### 1. Commit messages in English

**Rule**: Git commit messages are always written in English, regardless of the
language used in conversation.

**Why**: the repository history is a technical artifact meant to stay readable to
any contributor and consistent with the code and docs, which are in English.
Mixed-language history is hard to search and to skim.

**How to apply**: imperative subject line, English body covering the reasoning and
the trade-offs. Conversation and explanations to the user stay in Italian.

### 2. Reuse `pkg_utils`, do not reimplement

`roles/pkg_utils/tasks/` is the shared toolbox; include it with `tasks_from`.
Before writing PowerShell, check whether one of these already does the job:

`profiles` · `logoff` · `restart` · `pending_restart` · `kill` · `services_stop` ·
`detect_sw` · `registry_read` · `download` · `win_copy` · `win_extract` ·
`win_path` · `shortcuts` · `start_process` · `run_as_system` · `win_clean_temp`

`profiles` is the one most worth knowing, and its implementation is ~300 lines of
P/Invoke you never need to read. It returns `win_workman_profiles`, one entry per
local profile (plus `Default` when `win_workman_profiles_include_default`), with:

| Field | Meaning |
|---|---|
| `SID`, `Name`, `LocalPath` | identity of the profile |
| `HiveRoot` | `HKU:\<SID>\` when mounted, else `HKLM:\ANSIBLE\` |
| `HivePath` | path to `NTUSER.DAT`, for `win_regedit`'s `hive:` parameter |
| `HiveExists`, `HiveMounted` | whether the hive is on disk / currently loaded |
| `Loaded` | true only when the user has an **active interactive session** |

The established pattern for writing an `HKCU` setting to every profile — including
users who never logged on — is in `roles/wallpaper/` and `roles/display_scale/`:
force a logoff, select `Loaded == false and HiveExists == true`, then loop
`win_regedit` over `profiles | product(entries)`.

### 3. Adding a role

Minimum set, mirroring an existing role of the same family:

- `vars/main.yaml` — `win_workman_<role>_schema` with `name` and `default_action`
- `tasks/main.yaml` — dispatcher that includes `act_{{ win_workman_action or default_action }}`
- `meta/main.yaml` — galaxy info, `dependencies: [pkg_utils]`, `allow_duplicates: true`
- `meta/mcp.yaml` — **required**, or the role is invisible to the MCP server
- `docs/roles/<family>/<role>.md`, plus its rows in `docs/index.md` (catalog table
  *and* thematic list) and in the two tables in `docs/architecture.md`

Variables are namespaced `win_workman_<role>_*`. User-overridable ones go in
`defaults/`, computed and structural ones in `vars/`.

### 4. Lint is the gate

CI runs `ansible-lint --profile production` on ansible-core 2.20.4 over the whole
tree, and nothing else. Run it on the role you touched before declaring done —
it catches module misuse, not just formatting.

### 5. Keep `on`/`off` meaningful

Every schema has a `default_action`, so a bare `chrome` or `wallpaper` does
something sensible, and `on`/`off` mean enable/disable across the whole
collection. When a role's natural verbs are different (`set`/`reset`), still wire
`on`/`off` as aliases rather than leaving them undefined.

## PowerShell traps already paid for

Both of these fail **silently**, which is why they are here rather than in a doc.

- **`ConvertFrom-Json` does not unroll arrays.** It returns a multi-element array
  as a single object, and the pipeline does not flatten it: `@(...)` and
  `ForEach-Object` yield one element holding every value concatenated. Works with
  one element, breaks with two or more, without an error. Always iterate with
  `foreach ($x in (ConvertFrom-Json -InputObject $Json))`.
- **`Start-Process -Wait` waits on the job object, not the process.** It returns
  only once every descendant has exited, so a task hangs on an operation that
  already succeeded (an installer leaving a telemetry helper alive). That same
  behaviour is load-bearing for NSIS uninstallers that re-spawn into temp and exit
  immediately — so do not "fix" it globally. Use `-PassThru` plus `WaitForExit()`
  with a timeout where you need the process alone.

## Environment

The lab project at `/home/alessandro/Progetti/ansible-win_edulab` reaches this
collection through a symlink under its `ansible_collections/`, so edits here take
effect there with no reinstall. That project drives runs through its own
`playbooks/win_wm.yaml`; this collection's own entry point is
`ansible-playbook lineadicomando.win_workman.win_workman -e '{"t": "chrome,vlc-off"}'`.
