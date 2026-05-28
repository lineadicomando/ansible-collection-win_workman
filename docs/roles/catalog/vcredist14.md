# Role: vcredist14

Manages Visual C++ Redistributable Runtime Libraries, required by many
applications compiled with Visual C++. Supports standard package operations:
install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Visual C++ Redistributable |
| `off` | Uninstall Visual C++ Redistributable |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Visual C++ Redistributable is installed |

---

## Configuration

No variables. Visual C++ Redistributable is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - vcredist14
  - vcredist14-off
```

---

## Schema details

Software name: `Visual C++ Redistributable`  
Provider: `registry`  
Installer: `vc_redist.x64.exe`  
Homepage: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

---

## Notes

Visual C++ Redistributable libraries are dependencies for many Windows applications.
Installing this ensures compatibility with applications built using Visual C++ toolchain.
This role is automatically included as a dependency by the `seb` role when installing
Safe Exam Browser.
