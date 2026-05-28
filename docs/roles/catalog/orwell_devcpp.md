# Role: orwell_devcpp

> **Work in progress** — preliminary draft.

Manages Orwell Dev-C++, a lightweight IDE for C and C++ development. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Orwell Dev-C++ |
| `off` | Uninstall Orwell Dev-C++ |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Orwell Dev-C++ is installed |

---

## Configuration

No variables. Orwell Dev-C++ is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - orwell_devcpp
  - orwell_devcpp-off
```

---

## Schema details

Software name: `Orwell Dev-Cpp`  
Provider: `registry`  
Installer: `Dev-Cpp_5.11_TDM-GCC_4.9.2_Setup.exe`  
Homepage: https://www.dev-cpp.com/

---

## Notes

Orwell Dev-C++ is a community fork with TDM-GCC 4.9.2 compiler for C and C++ development.
