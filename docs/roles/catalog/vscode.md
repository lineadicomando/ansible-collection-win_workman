# vscode — Visual Studio Code

Visual Studio Code, machine-wide from the system installer (`VSCodeSetup-x64`, Inno
Setup), `registry` provider.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_vscode_shortcuts` | `false` | Manage `%Public%\Desktop\Visual Studio Code.lnk` through the schema's `shortcuts` |

## Notes

- Installed with `/TASKS=desktopicon,addtopath /MERGETASKS=!runcode`: the installer
  makes its own desktop icon and puts `code` on the system PATH, and does not launch
  the editor at the end of a silent install.
