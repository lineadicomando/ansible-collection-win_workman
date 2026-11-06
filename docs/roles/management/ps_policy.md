# Role: ps_policy

> **Work in progress** — preliminary draft.

Sets the machine-wide execution policy of Windows PowerShell 5.1. Windows client
editions default to `Restricted`, which refuses every `.ps1` file: the npm and
npx shims, a Python venv's `Activate.ps1`, the scripts students write. The
`nodejs*` roles call `ps_policy-on` as a dependency.

---

## Actions

| Action | Description |
|---|---|
| `set` | Apply a policy *(default action)*; the policy can be the task argument: `ps_policy-set-AllSigned` |
| `reset` | Remove the value this role writes; Windows falls back to its default |
| `on` | Alias for `set` — applies `win_workman_ps_policy` |
| `off` | Alias for `reset` |
| `info` | Report the machine-wide scopes and the resulting policy |

Policies: `Restricted`, `AllSigned`, `RemoteSigned`, `Unrestricted`, `Bypass`
(case-insensitive in the task string). Any other value fails before touching
the registry.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_ps_policy` | `RemoteSigned` | Policy applied when the task string carries no argument |
| `win_workman_ps_policy_mode` | `local_machine` | Where the policy is written, see below |

### Modes

| Mode | Registry | Effect |
|---|---|---|
| `local_machine` | `HKLM\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell` and its `WOW6432Node` twin, value `ExecutionPolicy` | The LocalMachine scope, as `Set-ExecutionPolicy -Scope LocalMachine`. Users may still set their own CurrentUser scope |
| `machine_policy` | `HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell`, values `EnableScripts` and `ExecutionPolicy` | The "Turn on Script Execution" policy: wins over every scope. Only `Restricted`, `AllSigned`, `RemoteSigned`, `Unrestricted`. A domain GPO that sets it overwrites it at the next refresh |

`Set-ExecutionPolicy` run from a 64-bit process writes only the first key, so the
32-bit `powershell.exe` would keep `Restricted`: the role writes both.

A policy (`machine_policy` scope, from a GPO or local) wins over LocalMachine:
in `local_machine` mode `set` warns when one is present with a different value.
`reset` in `local_machine` mode never touches the policy key, which may belong
to a GPO.

---

## Notes

- `RemoteSigned` runs local scripts and refuses unsigned scripts carrying the
  Mark of the Web (downloaded from the internet). Files installed by an MSI have
  none.
- The execution policy is not a security boundary: anyone can start
  `powershell -ExecutionPolicy Bypass`. Ansible itself always does, so it is not
  affected by this role.
- PowerShell 7 keeps its own setting in `powershell.config.json` and defaults to
  `RemoteSigned` on Windows: not managed here.
- `info` reports `effective` as what a user gets unless they override it in
  their CurrentUser scope or a user GPO does; those are per profile and not read.
