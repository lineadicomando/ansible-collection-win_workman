# Role: vscode

> **Work in progress** — preliminary draft.

Manages Visual Studio Code, a lightweight source-code editor with integrated
development tools. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Visual Studio Code |
| `off` | Uninstall Visual Studio Code |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Visual Studio Code is installed |

---

## Configuration

No variables. Visual Studio Code is installed with default settings and desktop
icon shortcut.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - vscode
  - vscode-off
```

---

## Schema details

Software name: `Visual Studio Code`  
Provider: `registry`  
Installer: `VSCodeSetup-x64-1.108.2.exe`  
Homepage: https://code.visualstudio.com/

---

## Notes

Installation includes the `desktopicon` and `addtopath` tasks, which create a
desktop shortcut and add VSCode to the system PATH for command-line access.
