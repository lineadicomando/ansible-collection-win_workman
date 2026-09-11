# Role: autocadlt2023

Removes AutoCAD LT 2023 from a Windows host, in any installed locale. This is a
**removal-only** role: win_workman never installs AutoCAD LT 2023, it only clears
it out of the way.

Its reason to exist is [`autocadlt2026`](autocadlt2026.md): Autodesk releases
install side by side in version-specific folders and registry keys, so running
`autocadlt2026` on a host that already has the 2023 release leaves **both**
installed. Pair the two tasks to get a replacement.

---

## Actions

| Action | Description |
|---|---|
| `off` | Uninstall AutoCAD LT 2023 (any locale) |
| `off-full` | As above, plus the leftovers of the 2023 product family |

`off` is the only action and must be spelled out. A bare `autocadlt2023` task
fails with an explicit message, so a typo in a playbook can never trigger a
silent uninstall. The role exposes no `on`, `download`, `info` or `is_present`:
it does not reach the `pkg_utils` package workflow at all.

Example:

```yaml
# playbooks/lab_cad.yaml
win_workman_tasks:
  - autocadlt2023-off     # must run first
  - autocadlt2026         # locale auto-detected from the host
```

Order matters: removing 2023 **after** installing 2026 risks taking shared
Autodesk components down with it.

---

## How removal works

AutoCAD LT 2023 is an ODIS bundle, like the 2026 release, but its bundle GUID is
locale-dependent and not documented, and localized bundles are inconsistent about
registering themselves in the Windows uninstall hive. The role therefore
discovers the removal path at run time instead of pinning a GUID in `vars/`:

1. **Detect** — `pkg_utils/detect_sw` with `name_like: "*AutoCAD LT 2023*"`.
2. **Locate the bundle** — scan `C:\ProgramData\Autodesk\ODIS\metadata\*\bundleManifest.xml`
   for the manifest naming AutoCAD LT 2023; derive the bundle GUID and the
   matching `SetupRes\manifest.xsd` (falling back to the AdODIS copy).
3. **Uninstall** — `AdODIS\V1\Installer.exe -i uninstall -q --trigger_point system -m <manifest> -x <xsd>`,
   waiting on the uninstaller process alone (see Notes).
4. **Fallback** — if no ODIS manifest survives but the registry still carries an
   uninstall string, run that instead, adding the silent flag if missing.
5. **Verify** — re-detect and fail if the product is still registered.
6. **Reboot** — only if Windows reports a pending restart.

Exit codes `0`, `1604` (suspended, reboot needed) and `3010` (soft reboot) count
as success.

If the product is present but neither a manifest nor an uninstall string can be
found, the role fails with an explicit message rather than guessing.

---

## The `full` variant

`autocadlt2023-off-full` removes what the ODIS uninstaller leaves behind, and
**only** what belongs to the 2023 product family:

| Leftover | Why it is removed |
|---|---|
| `Autodesk Material Library 2023` | tied to the 2023 release; 2026 installs its own |
| `Autodesk Material Library Base Resolution Image Library 2023` | same, ~279 MB together |
| `C:\Program Files\Autodesk\AutoCAD LT 2023` | emptied by the uninstall, removed only if it holds no files |
| `C:\ProgramData\Autodesk\Uninstallers\*AutoCAD LT 2023*` | orphaned uninstaller payload |
| `C:\ProgramData\Autodesk\Adlm\AdlSdk-ACDLT2023*.log` | licensing logs of the removed product |

The shared Autodesk stack — AdODIS, Autodesk Access, CER, Identity Manager,
AdSSO, Genuine Service, AdskLicensing — is **never** touched, by either `off` or
`off-full`. Those components are version-independent, Autodesk Access keeps them
up to date on its own, and every newer release reuses them: removing them would
only force `autocadlt2026` to reinstall them.

Products are matched by display-name pattern and their GUIDs resolved at run
time (`tasks/find_products.yaml`), because Autodesk component GUIDs change with
every release: a pinned `product_id` that no longer matches turns `win_package`
into a silent no-op.

The install directory is removed only when it contains no files, so a
half-finished uninstall never loses data behind the operator's back.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_autocadlt2023_name_like` | `*AutoCAD LT 2023*` | Registry `DisplayName` pattern used for detection |
| `win_workman_autocadlt2023_manifest_match` | `AutoCAD LT 2023` | Text matched inside `bundleManifest.xml` |
| `win_workman_autocadlt2023_install_path` | `C:\Program Files\Autodesk\AutoCAD LT 2023` | Install directory, used as a presence hint |
| `win_workman_autocadlt2023_kill_processes` | `[acadlt]` | Processes force-closed before uninstalling |
| `win_workman_autocadlt2023_success_exit_codes` | `[0, 1604, 3010]` | Uninstaller exit codes treated as success |
| `win_workman_autocadlt2023_uninstall_timeout` | `1800` | Seconds to wait for the uninstaller before failing |
| `win_workman_autocadlt2023_full_product_patterns` | `[Autodesk Material Library*2023*]` | Display-name patterns removed by `off-full` |
| `win_workman_autocadlt2023_full_paths` | see `vars/` | Directories removed by `off-full`, only when empty |
| `win_workman_autocadlt2023_full_globs` | see `vars/` | Glob patterns removed by `off-full` |

These live in `vars/` and normally need no override.

---

## Notes

- **Shared components are left in place on purpose.** AdODIS, AdskLicensing and
  Autodesk Access are used by every Autodesk product on the host, including the
  2026 install that usually follows. There is no `full` variant here — unlike
  `autocadlt2026-off[full]`, which purges `C:\Program Files\Autodesk` and
  `C:\ProgramData\Autodesk` wholesale and must only be used when no other
  Autodesk product remains.
- The role force-closes `acadlt.exe` before uninstalling; make sure nobody is
  drawing on the target machines.
- The role does **not** use `pkg_utils/start_process` for the uninstall. That
  helper runs `Start-Process -Wait`, which in PowerShell 5.1 waits for the whole
  job object rather than the launched process, and Autodesk's uninstaller ends
  by spawning `ADPClientService.exe` (desktop analytics) which outlives it — the
  task would hang for minutes after the removal had already succeeded. The role
  starts the uninstaller with `-PassThru` and calls `WaitForExit()` on that
  process only, with `win_workman_autocadlt2023_uninstall_timeout` as a ceiling.
- Licensing is not touched: the 2023 license entry is removed with its bundle,
  and `autocadlt2026` registers its own afterwards.
