# seb — Safe Exam Browser

Safe Exam Browser 3.x MSI (`msi` provider, pinned version and checksum), 64-bit by
default; the task argument `32bit` selects the x86 MSI. `on` also installs
`vcredist14`. The role can generate a machine-level `SebClientSettings.seb` from a
dict and deploy it, separately from the install.

## Actions

| Action | Does |
|---|---|
| `deploy` | Builds the `.seb` from `win_workman_seb_client_settings` on the controller and copies it to `win_workman_seb_client_settings_dest`; does not install SEB |
| `undeploy` | Deletes the deployed `.seb`; SEB stays installed |
| `config_key` | **Experimental.** Builds the `.seb` in a controller temp file and prints a "Config Key" for Moodle (`run_once`); nothing is written to the hosts |

`on` installs the package only: run `seb-on,seb-deploy` to push a configuration too.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_seb_client_settings` | baseline lockdown, see `defaults/main.yaml` | Settings dict serialised as an XML plist into the `.seb` |
| `win_workman_seb_client_settings_dest` | `C:\ProgramData\SafeExamBrowser\SebClientSettings.seb` | Path of the deployed file; its directory is created |
| `win_workman_seb_shortcuts` | `false` | Create a Public Desktop shortcut |

The baseline: start page `safeexambrowser.org`, no quit, logging to
`C:\ProgramData\SafeExamBrowser\Logs`, fullscreen, pop-ups blocked, separate desktop
with Explorer killed, SEB service enforced (`sebServicePolicy: 2`), browser profile
removed at the end, keyboard hooks on with Alt+Tab, Alt+F4, PrintScreen, Ctrl+Esc
blocked, Ctrl+Alt+Del screen limited to shutdown, clipboard blocked
(`clipboardPolicy: 1`), Browser Exam Key sent, URL filter allowing only
`safeexambrowser.org`. Override the whole dict in the inventory: a partial dict
replaces it, it is not merged.

## Notes

- `allowVirtualMachine: true` in the baseline is for the test VMs: set it to `false`
  for real exams.
- `allowScreenSharing: true` is required with Veyon: without it SEB calls
  `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)` and Veyon shows a black screen.
- `enableAltCtrl` and `insideSebEnableShutDown` stay `true` so technicians can use
  Ctrl+Alt+Del and shut down; Ctrl+Alt+Del itself cannot be intercepted (Windows SAS).
- Keys that do nothing on Windows SEB 3.x: `newBrowserWindowByLinkPolicy` (Mac/iOS
  only); `allowQuit` is "currently Mac only" in the spec but honoured on Windows.
  Windows-only keys: `logDirectoryWin`, `createNewDesktop`, `killExplorerShell`,
  `sebServicePolicy`, `removeBrowserProfile`, `hookKeys` and the `enable*` key
  switches (they need `hookKeys: true`), `insideSebEnable*`. Full list with defaults:
  skill `win-workman-seb-config` of the ansible-win_edulab project.
- The `.seb` is unencrypted: gzip of `plnd` + gzip of the plist, with `mtime=0`, so
  the same dict gives the same bytes and `deploy` reports `changed` only on a real
  change.
- `config_key` prints the SHA-256 of those file bytes. SEB derives its Config Key
  from the settings themselves, so expect the value to differ: read the key from the
  file in SEB Config Tool, or upload the `.seb` to Moodle (*Quiz → Safe Exam Browser
  → Require Safe Exam Browser*), which extracts it. Any change to the settings changes
  the key; register it again after each update.
- `sendBrowserExamKey` adds `X-SafeExamBrowser-RequestHash` to every request; it is
  inert unless the LMS verifies it (Google Classroom does not).
