# Role: redpanda_cpp

> **Work in progress** — preliminary draft.

Manages Red Panda C++, an actively maintained lightweight C and C++ IDE bundled with
a MinGW64 GCC toolchain. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Red Panda C++ |
| `off` | Uninstall Red Panda C++ |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Red Panda C++ is installed |

---

## Configuration

No variables. Red Panda C++ is installed with default settings, for all users.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - redpanda_cpp
  - redpanda_cpp-off
```

---

## Schema details

Software name: `Red Panda C++`  
Provider: `registry`  
Installer: `RedPanda.C++.3.4.win64.MinGW64_11.5.0.Setup.exe`  
Homepage: https://github.com/royqh1979/RedPanda-CPP

---

## Notes

Proposed as the replacement for `orwell_devcpp` (last released in 2016) and
`embarcadero_devcpp`: it keeps the Dev-C++ workflow and project format, takes over
the same `.dev`, `.c`, `.cpp` and header file associations, and ships MinGW64
GCC 11.5.0 instead of TDM-GCC 9.2. Install the three side by side only for
comparison — whichever is installed last owns the file associations.

The installer is NSIS with the MultiUser extension: `/AllUsers` installs under
`%ProgramFiles%\RedPanda-Cpp` and creates the all-users desktop and Start Menu
shortcuts itself, so the schema declares none. Uninstall runs the NSIS
`uninstall.exe` through `uninstall_via_helper`.

The upstream uninstaller removes the `DevCpp.*` ProgID keys but leaves the eight
file extension keys under `HKLM:\Software\Classes` pointing at them, so `off`
runs an `after_uninstall_ps_script` that drops any of those extensions whose
ProgID is really gone — an `orwell_devcpp` or `embarcadero_devcpp` install that
still owns `DevCpp.*` keeps its associations.

The 64-bit build with the bundled compiler is the one packaged here. Upstream also
publishes 32-bit, portable and `NoCompiler` variants, which this role does not cover.
