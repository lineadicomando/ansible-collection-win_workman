# Role: vivaldi

Manages Vivaldi, a Chromium-based web browser with built-in privacy controls and
advanced tab management. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Vivaldi |
| `off` | Uninstall Vivaldi |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Vivaldi is installed |

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `win_workman_vivaldi_shortcuts` | `false` | Create Desktop and Start Menu shortcuts |
| `win_workman_vivaldi_shortcut_url` | `""` | URL opened by the shortcut on launch |
| `win_workman_vivaldi_shortcut_no_first_run` | `true` | Pass `--no-default-browser-check --no-first-run` to the shortcut |

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_vivaldi_shortcuts: true
win_workman_vivaldi_shortcut_url: "https://moodle.school.example/"
win_workman_vivaldi_shortcut_no_first_run: true

win_workman_tasks:
  - vivaldi
```

---

## Schema details

Software name: `Vivaldi`  
Provider: `registry`  
Installer: `Vivaldi.7.9.3970.67.x64.exe`  
Homepage: https://vivaldi.com/

---

## Notes

Vivaldi uses a Chromium-based mini-installer. Silent system-wide installation requires
`--vivaldi-silent --do-not-launch-chrome --system-level`; NSIS-style flags (`/silent
/allusers`) are accepted by the outer wrapper but not forwarded correctly to the inner
`setup.exe`.

Uninstall runs via `uninstall_via_helper` because the Vivaldi uninstaller returns exit
code 19 in non-interactive sessions even on success. `uninstall_valid_rc: [0, 19]`
marks both codes as acceptable.
