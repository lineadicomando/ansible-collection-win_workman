# Role: embarcadero_devcpp

> **Work in progress** — preliminary draft.

Manages Embarcadero Dev-C++, a lightweight IDE for C and C++ development. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Embarcadero Dev-C++ |
| `off` | Uninstall Embarcadero Dev-C++ |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Embarcadero Dev-C++ is installed |

---

## Configuration

No variables. Embarcadero Dev-C++ is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - embarcadero_devcpp
  - embarcadero_devcpp-off
```

---

## Schema details

Software name: `Embarcadero Dev-Cpp`  
Provider: `registry`  
Installer: `Embarcadero_Dev-Cpp_6.3_TDM-GCC_9.2_Setup.exe`  
Homepage: https://www.embarcadero.com/free-tools/dev-cpp

---

## Notes

Embarcadero Dev-C++ includes TDM-GCC 9.2 compiler for C and C++ development.
