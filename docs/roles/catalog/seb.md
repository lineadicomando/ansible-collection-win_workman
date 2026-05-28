# Role: seb

Installs Safe Exam Browser (SEB) and can generate/deploy a machine-level
`SebClientSettings.seb` in `%PROGRAMDATA%`.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install/update SEB package and apply client settings file |
| `off` | Uninstall SEB package |
| `deploy` | Generate and deploy the client settings file only (no install) |
| `undeploy` | Remove the client settings file from the target |
| `config_key` | ⚠️ **Experimental** — Print the SEB Config Key for Moodle (see below) |

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_seb_shortcuts` | `false` | Create desktop shortcuts for SEB |
| `win_workman_seb_client_settings_dest` | `C:\\ProgramData\\SafeExamBrowser\\SebClientSettings.seb` | Destination file path |
| `win_workman_seb_client_settings` | see defaults | Dictionary serialized as XML plist into `.seb` |

### Default `win_workman_seb_client_settings`

```yaml
win_workman_seb_client_settings:
  startURL: "https://classroom.google.com/?hl=it"
  allowQuit: false
  enableLogging: true
  logDirectoryWin: 'C:\\ProgramData\\SafeExamBrowser\\Logs'
  allowVirtualMachine: false      # WARNING: enable only for test purposes
  browserViewMode: 1              # 0=window 1=fullscreen 2=touch

  blockPopUpWindows: true

  # Kiosk / Desktop (Windows only)
  createNewDesktop: true          # Isolated Windows desktop
  killExplorerShell: true         # Terminate Explorer shell
  sebServicePolicy: 2             # 0=ignore 1=warn 2=enforce SEB Service
  removeBrowserProfile: true      # Clean Chromium profile on exit

  # Keyboard hooks (Windows only — require hookKeys: true)
  hookKeys: true
  enableAltTab: false
  enableAltF4: false
  enablePrintScreen: false
  enableCtrlEsc: false
  enableAltCtrl: true             # Keep true: allows Ctrl+Alt+Del for technicians

  # Ctrl+Alt+Del security screen (Windows only)
  insideSebEnableStartTaskManager: false
  insideSebEnableLogOff: false
  insideSebEnableShutDown: true   # Keep true: allows manual shutdown by technicians
  insideSebEnableLockThisComputer: false
  insideSebEnableSwitchUser: false
  insideSebEnableEaseOfAccess: false

  # Exam integrity
  sendBrowserExamKey: true

  # URL filtering
  URLFilterEnable: true
  URLFilterEnableContentFilter: false
  URLFilterRules:
    - action: 1   # allow
      active: true
      expression: "https://classroom.google.com"
    - action: 0   # block
      active: true
      expression: ".*"
```

### Notes on key compatibility

| Key | Platform | Notes |
|---|---|---|
| `startURL` | Win / Mac / iOS | Starting URL |
| `allowQuit` | Win / Mac | Spec: "currently Mac only", honored on Win in practice |
| `enableLogging` | Win / Mac | Enable SEB log file |
| `logDirectoryWin` | **Windows only** | Log directory path |
| `allowVirtualMachine` | Win / Mac | Allow running inside a VM |
| `browserViewMode` | Win / Mac | 0=window 1=fullscreen 2=touch |
| `blockPopUpWindows` | Win / Mac | Block JS popups |
| `createNewDesktop` | **Windows only** | Run SEB on isolated desktop |
| `killExplorerShell` | **Windows only** | Terminate Explorer shell |
| `sebServicePolicy` | **Windows only** | Enforce SEB Windows Service |
| `removeBrowserProfile` | **Windows only** | Delete Chromium profile on quit |
| `hookKeys` | **Windows only** | Master switch for keyboard hooks |
| `enableAltTab` | **Windows only** | Default in SEB spec is `true` |
| `enableAltCtrl` | **Windows only** | Default in SEB spec is `true` — left `true` to allow Ctrl+Alt+Del for technicians |
| `insideSebEnableShutDown` | **Windows only** | Left `true` to allow manual shutdown by technicians |
| `insideSebEnableStartTaskManager` | **Windows only** | Controls "Start Task Manager" in the Ctrl+Alt+Del screen |
| `sendBrowserExamKey` | Win / Mac / iOS | Adds `X-SafeExamBrowser-RequestHash` header; only meaningful if the LMS verifies it |
| `URLFilterEnable` / `URLFilterRules` | Win / Mac / iOS | URL allowlist/blocklist |

---

## Notes

- The `.seb` file is generated unencrypted (PLND format) directly from the settings dictionary.
- Generation happens on the controller (`localhost`) and the file is copied to the target via `win_copy`.
- Override keys in `win_workman_seb_client_settings` from inventory or group_vars as needed.
- Any change to `win_workman_seb_client_settings` changes the Config Key — re-register it in Moodle after every update.

---

## Moodle integration (`sendBrowserExamKey`)

When `sendBrowserExamKey: true`, SEB adds an `X-SafeExamBrowser-RequestHash` header to every request. Moodle verifies it using the **Config Key** registered in the quiz settings.

To obtain the Config Key and configure Moodle:

1. Run the `config_key` action (see below) — **experimental**.
2. Or open `SebClientSettings.seb` in **SEB Config Tool** (Windows app) to read the Config Key directly.
3. In Moodle: *Quiz → Edit settings → Safe Exam Browser → Require Safe Exam Browser*
   - Upload the `.seb` file (Moodle extracts the key automatically), **or**
   - Paste the Config Key manually.

> **Important:** `sendBrowserExamKey` is inert unless the LMS actively verifies the header.
> With Google Classroom as `startURL`, no verification occurs.

### `config_key` action (experimental)

> ⚠️ **Experimental.** The Config Key is computed as SHA-256 of the raw `.seb` file bytes
> produced by the `seb_config` module. The exact calculation used internally by SEB Windows
> has not been independently verified against the SEB source code. Cross-check the printed
> value against **SEB Config Tool** before registering it in Moodle.

```yaml
win_workman_tasks:
  - "seb-config_key"
```

The action runs only on `localhost` (`run_once`), generates a temporary `.seb` from the
current `win_workman_seb_client_settings`, prints the Config Key, and removes the temp file.
No Windows hosts are contacted.

---

## Usage

```yaml
- name: Configure SEB for lab PCs
  hosts: lab_pcs
  roles:
    - role: lineadicomando.win_workman.dispatcher
      vars:
        win_workman_tasks:
          - seb-on
          - seb-deploy
        win_workman_seb_client_settings:
          startURL: "https://moodle.example.test/mod/quiz/view.php?id=42"
          allowQuit: false
          enableLogging: true
          allowVirtualMachine: false
```
