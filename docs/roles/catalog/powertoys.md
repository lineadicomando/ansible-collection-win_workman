# Role: powertoys

> **Work in progress** — preliminary draft.

Installs Microsoft PowerToys, a set of utilities for power users to tune and
streamline their Windows experience. Supports standard package operations:
install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Microsoft PowerToys |
| `off` | Uninstall Microsoft PowerToys |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Microsoft PowerToys is installed |

---

## Variables

No role-specific variables. Standard `pkg_utils` defaults apply.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - powertoys
  - powertoys-off
```

---

## Schema details

Software name: `PowerToys (Preview)`  
Provider: `registry`  
Installer: `PowerToysSetup-0.102.3101.0-x64.exe`  
Homepage: https://github.com/microsoft/PowerToys

---

## Notes

Requires Windows 11. Only the 64-bit installer is provided; there is no 32-bit build.

The installer is a per-machine WiX Burn bundle that registers two uninstall entries:
the MSI, `PowerToys (Preview)`, and the bundle, `PowerToys (Preview) x64`, whose
uninstaller is its copy under `%ProgramData%\Package Cache`. The role detects the
bundle and removes it with that uninstaller (`/quiet`), so Burn takes the MSI, its own
registration and the caches with it. Detecting the MSI, as the role did up to 0.99.1,
made `off` remove only the MSI and left PowerToys listed under Apps.

The bundle carries the WebView2 bootstrapper as a shared prerequisite: its cached copy
(`MicrosoftEdgeWebview2Setup.exe`, about 2 MB) stays after `off`, as Burn intends for
packages other software may depend on.
