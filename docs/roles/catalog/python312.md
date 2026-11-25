# Role: python312

> **Work in progress** — preliminary draft.

Manages Python 3.12, a general-purpose, high-level programming language. Supports
standard package operations: install, uninstall, download, and info queries.
Installation includes the Python interpreter and IDLE development environment.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Python 3.12 |
| `off` | Uninstall Python 3.12 |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Python 3.12 is installed |

---

## Configuration

Python 3.12 is installed with the following defaults:

- **Install scope**: System-wide (all users)
- **PATH integration**: Python is added to system PATH for command-line access
- **Launcher**: Not installed (launcher is typically unused in managed environments)
- **Shortcuts**: Creates desktop shortcuts for Python interpreter and IDLE IDE

No user-configurable variables.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - python312
  - python312-off
```

---

## Schema details

Software name: `Python 3.12`  
Provider: `registry` (Burn bundle, detected through its Core Interpreter MSI)  
Installer: `python-3.12.10-amd64.exe`  
Homepage: https://www.python.org/

---

## Notes

- **Deprecated**: Python 3.12 is in security-fix-only mode and python.org publishes no
  Windows installer past 3.12.10, so this role cannot be updated further. End-of-life is
  2028-10-31. The role prints a warning on every run; migrate to `python314` or `python315`
- **Detection**: the python.org installer is a WiX Burn bundle that registers its
  `Python 3.12.x (64-bit)` entry only in HKCU of the account that ran it, even for an
  all-users install. The role detects the machine-wide `Python 3.12.* Core Interpreter
  (64-bit)` MSI instead, so `info`, `on` and `off` work from any account; `off` also
  removes the other MSIs of the bundle and the bundle registration of the connecting
  account (`bundle_parts`, see `pkg_utils`). A registration left in another profile
  points at packages that are gone.
- Installation location: `%ProgramFiles%\Python312`
- Includes IDLE (interactive development environment) and pip package manager
- Python launcher is not installed; use `python.exe` directly from PATH
- Both Python interpreter and IDLE shortcuts are created on the public desktop
