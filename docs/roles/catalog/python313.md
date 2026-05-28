# Role: python313

> **Work in progress** — preliminary draft.

Manages Python 3.13, a general-purpose, high-level programming language. Supports
standard package operations: install, uninstall, download, and info queries.
Installation includes the Python interpreter and IDLE development environment.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Python 3.13 |
| `off` | Uninstall Python 3.13 |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Python 3.13 is installed |

---

## Configuration

Python 3.13 is installed with the following defaults:

- **Install scope**: System-wide (all users)
- **PATH integration**: Python is added to system PATH for command-line access
- **Launcher**: Not installed (launcher is typically unused in managed environments)
- **Shortcuts**: Creates desktop shortcuts for Python interpreter and IDLE IDE

No user-configurable variables.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - python313
  - python313-off
```

---

## Schema details

Software name: `Python 3.13`  
Provider: `registry`  
Installer: `python-3.13.9-amd64.exe`  
Homepage: https://www.python.org/

---

## Notes

- Installation location: `%ProgramFiles%\Python313`
- Includes IDLE (interactive development environment) and pip package manager
- Python launcher is not installed; use `python.exe` directly from PATH
- Both Python interpreter and IDLE shortcuts are created on the public desktop
