# autocadlt2023 — AutoCAD LT 2023 removal

Removes AutoCAD LT 2023, in any locale. Removal-only: win_workman never installs it.
Autodesk releases install side by side, so [autocadlt2026](autocadlt2026.md) on a host
with 2023 leaves both; run this first to get a replacement.

## Actions

| Action | Does |
|---|---|
| `off` | Uninstalls AutoCAD LT 2023, any locale |
| `off-full` | As `off`, plus the leftovers of the 2023 product family |

`off` must be spelled out: any other action, a bare `autocadlt2023` included, fails
with an explicit message, so a typo can never trigger a silent uninstall. The role
never reaches the pkg_utils package workflow.

```yaml
win_workman_tasks:
  - autocadlt2023-off     # first: removing 2023 after installing 2026 risks shared components
  - autocadlt2026
```

## How `off` works

The 2023 bundle GUID is locale-dependent and undocumented, and localized bundles are
inconsistent about registering in the uninstall hive, so the removal path is found at
run time:

1. Detect with `pkg_utils/detect_sw`, `name_like: "*AutoCAD LT 2023*"`.
2. Scan `C:\ProgramData\Autodesk\ODIS\metadata\*\bundleManifest.xml` for the one naming
   AutoCAD LT 2023; take its GUID and `SetupRes\manifest.xsd` (falling back to the
   AdODIS copy).
3. Force-close `acadlt`, then run `AdODIS\V1\Installer.exe -i uninstall -q
   --trigger_point system -m <manifest> -x <xsd>`.
4. With no manifest but a registry uninstall string, run that instead, adding the
   silent flag (`/qn /norestart` for msiexec, `-q` otherwise) if missing. With neither,
   fail rather than guess.
5. Re-detect and fail if still registered; reboot only if Windows reports a pending
   restart.

Exit codes `0`, `1604` (suspended, reboot needed) and `3010` count as success.

## `off-full`

Removes only what belongs to the 2023 family:

| Leftover | Why |
|---|---|
| `Autodesk Material Library*2023*` (two packages, ~279 MB) | tied to 2023; 2026 installs its own |
| `C:\Program Files\Autodesk\AutoCAD LT 2023` | emptied by the uninstall; removed only if it holds no files |
| `C:\ProgramData\Autodesk\Uninstallers\*AutoCAD LT 2023*` | orphaned uninstaller payload |
| `C:\ProgramData\Autodesk\Adlm\AdlSdk-ACDLT2023*.log` | licensing logs of the removed product |

The shared Autodesk stack (AdODIS, Autodesk Access, CER, Identity Manager, AdSSO,
Genuine Service, AdskLicensing) is never touched, by either variant: it is
version-independent, kept current by Autodesk Access and reused by every newer
release, so removing it would only force `autocadlt2026` to reinstall it. Unlike
`autocadlt2026-off-full`, which purges it wholesale.

## Notes

- Products are matched by display-name pattern and their GUIDs resolved at run time
  (`tasks/find_products.yaml`): Autodesk component GUIDs change with every release, and
  a stale `product_id` makes `win_package` a silent no-op. Found 2026-09-11 on a lab
  host: of four GUIDs pinned in `autocadlt2026/vars`, only Autodesk Access matched.
- The uninstall does not use `pkg_utils/start_process`: `Start-Process -Wait` waits for
  the whole job object, and the Autodesk uninstaller ends by spawning
  `ADPClientService.exe`, which outlives it and hung the task for minutes after a
  successful removal. The role waits on the uninstaller process alone, up to
  `win_workman_autocadlt2023_uninstall_timeout` (1800 s).
- Patterns, paths, exit codes and the timeout are in `vars/main.yaml` (role vars, not
  overridable from the inventory).
- Licensing is not touched: the 2023 license entry goes with its bundle, and
  `autocadlt2026` registers its own.
