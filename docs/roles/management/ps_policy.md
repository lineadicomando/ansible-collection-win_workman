# ps_policy — PowerShell execution policy

Sets the machine-wide execution policy of Windows PowerShell 5.1. Client editions
default to `Restricted`, which refuses every `.ps1`: the npm/npx shims, a venv's
`Activate.ps1`, the scripts students write. The `nodejs*` roles call `ps_policy-on`
as a dependency.

## Actions

| Action | Does |
|---|---|
| `set[-<policy>]` (default) | Write the policy (argument, else `win_workman_ps_policy`) in the chosen mode, then report the effective one |
| `reset` | Remove what the mode writes: Windows falls back to its default (`Restricted` on client, `RemoteSigned` on Server) |
| `on` | Alias of `set` (no argument: uses the variable) |
| `off` | Alias of `reset` |
| `info` | Report `effective`, its `source` (`MachinePolicy`, `LocalMachine`, `Windows default`) and the raw values |

Policies: `Restricted`, `AllSigned`, `RemoteSigned`, `Unrestricted`, `Bypass`
(case-insensitive). Anything else, or `Bypass` in `machine_policy` mode, fails before
the registry is touched.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_ps_policy` | `RemoteSigned` | Policy when the task string carries none |
| `win_workman_ps_policy_mode` | `local_machine` | `local_machine` or `machine_policy`, below |

| Mode | Writes | Effect |
|---|---|---|
| `local_machine` | `ExecutionPolicy` in `HKLM\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell` and its `WOW6432Node` twin | The LocalMachine scope; users may still set their CurrentUser scope |
| `machine_policy` | `EnableScripts` (`0` for `Restricted`, else `1`) and `ExecutionPolicy` in `HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell` | "Turn on Script Execution": wins over every scope; a domain GPO setting it overwrites it at the next refresh |

## Notes

- `Set-ExecutionPolicy` from a 64-bit process writes only the first key, leaving the
  32-bit `powershell.exe` on `Restricted`: the role writes both.
- In `local_machine` mode `set` warns when a policy (GPO or local) sets a different
  value, since it wins; `reset` never touches the policy key, which may belong to a GPO.
- `effective` ignores the per-profile CurrentUser and UserPolicy scopes, which are not
  read.
- `RemoteSigned` runs local scripts and refuses unsigned ones carrying the Mark of
  the Web; files installed by an MSI have none.
- Not a security boundary: anyone can run `powershell -ExecutionPolicy Bypass`, and
  Ansible always does, so it is unaffected.
- PowerShell 7 keeps its own setting in `powershell.config.json` (default
  `RemoteSigned`): not managed.
