# Role: notepadpp

Manages Notepad++, a free source code editor and Notepad replacement. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Notepad++ |
| `off` | Uninstall Notepad++ |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Notepad++ is installed |

---

## Configuration

No variables. Notepad++ is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - notepadpp
  - notepadpp-off
```

---

## Schema details

Software name: `Notepad++`  
Provider: `msi`  
Installer: `npp.8.9.5.Installer.x64.msi`  
Homepage: https://notepad-plus-plus.org/

---

## Notes

Notepad++ is a popular text and source code editor for Windows. It supports
syntax highlighting for dozens of programming languages and is commonly used
as a lightweight alternative to a full IDE.
