# win_workman documentation

Ansible collection for **Windows 11 workstations** in school labs (not Windows
Server). Start with [architecture](architecture.md) (task strings, standard actions,
package schema, global variables); [mcp](mcp.md) for the MCP server;
[TEMPLATE](roles/TEMPLATE.md) for writing a role page.

Two families of roles: **catalog** roles install a package through `pkg_utils`
(standard actions `on`, `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`,
`usr-*`; the table shows only the extra ones); **management** roles implement their own
actions (all listed, default first). The exact actions and variables of any role are
also what `get_role_info` returns.

## Core

| Role | What |
|---|---|
| [`dispatcher`](roles/core/dispatcher.md) | entry point: parses `win_workman_tasks`, includes each role |
| [`pkg_utils`](roles/core/pkg_utils.md) | package workflow, schema reference, shared `tasks_from` toolbox |

## Catalog

| Role | What | Extra actions / args |
|---|---|---|
| **Browsers** | | |
| [`chrome`](roles/catalog/chrome.md) | Google Chrome Enterprise MSI, lockdown policies | `privacy`, `rm`; `32bit` |
| [`firefox`](roles/catalog/firefox.md) | Mozilla Firefox per-language installer, lockdown policies | `privacy`, `rm`; language token |
| [`edge`](roles/catalog/edge.md) | Microsoft Edge policies and profile removal; never uninstalled | `privacy`, `rm`; `32bit` |
| [`brave`](roles/catalog/brave.md) | Brave Browser | — |
| [`opera`](roles/catalog/opera.md) | Opera Browser | — |
| [`vivaldi`](roles/catalog/vivaldi.md) | Vivaldi | — |
| [`seb`](roles/catalog/seb.md) | Safe Exam Browser and its generated machine-level `.seb` | `deploy`, `undeploy`, `config_key` |
| **Classroom** | | |
| [`veyon`](roles/catalog/veyon.md) | Veyon: install, keys, lab locations from the inventory | `config`; `on-master` |
| [`galene`](roles/catalog/galene.md) | Galène server on the teacher PC, shortcuts on the students | `build`; own `on`/`off`/`info` |
| [`gcpw`](roles/catalog/gcpw.md) | Google Credential Provider for Windows, allowed domains | `nodep` |
| **Development** | | |
| [`vscode`](roles/catalog/vscode.md) | Visual Studio Code, machine-wide, on PATH | — |
| [`zed`](roles/catalog/zed.md) | Zed editor, per-user only (`usr-*`) | — |
| [`notepadpp`](roles/catalog/notepadpp.md) | Notepad++ (MSI) | — |
| [`git`](roles/catalog/git.md) | Git for Windows | — |
| [`embarcadero_devcpp`](roles/catalog/embarcadero_devcpp.md) | Embarcadero Dev-C++ 6.3 with TDM-GCC 9.2 | — |
| [`orwell_devcpp`](roles/catalog/orwell_devcpp.md) | Orwell Dev-C++ 5.11 with TDM-GCC 4.9.2 (unmaintained) | — |
| [`redpanda_cpp`](roles/catalog/redpanda_cpp.md) | Red Panda C++ with MinGW64 GCC | — |
| [`laragon`](roles/catalog/laragon.md) | Laragon WAMP development environment | — |
| [`mysql_server`](roles/catalog/mysql_server.md) | MySQL Server 9 binaries, no instance configured | — |
| [`mysql_workbench`](roles/catalog/mysql_workbench.md) | MySQL Workbench 8.0 CE | — |
| [`dbeaver`](roles/catalog/dbeaver.md) | DBeaver Community | — |
| [`postman`](roles/catalog/postman.md) | Postman, portable, latest upstream build | — |
| [`netbeans`](roles/catalog/netbeans.md) | Apache NetBeans with bundled JDK | — |
| [`python310`](roles/catalog/python310.md) … [`python315`](roles/catalog/python315.md) | Python 3.10–3.15, all users (one role per minor: `python311`…`python314`) | — |
| [`nodejs26`](roles/catalog/nodejs26.md) | Node.js 26 LTS, optional firewall rule | — |
| **Graphics, CAD, audio, video** | | |
| [`gimp`](roles/catalog/gimp.md) | GIMP 3 | — |
| [`inkscape`](roles/catalog/inkscape.md) | Inkscape (MSI) | — |
| [`blender`](roles/catalog/blender.md) | Blender, one minor series per host | — |
| [`sketchup2026`](roles/catalog/sketchup2026.md) | SketchUp 2026, classic or network licence | `license`, `unlicense` |
| [`autocadlt2026`](roles/catalog/autocadlt2026.md) | AutoCAD LT 2026, en/it detected | `off-full` |
| [`autocadlt2023`](roles/catalog/autocadlt2023.md) | removal of AutoCAD LT 2023, any locale | `off` only, `off-full` |
| [`tinycad`](roles/catalog/tinycad.md) | TinyCAD schematic editor, portable | — |
| [`vlc`](roles/catalog/vlc.md) | VLC media player | — |
| [`puredata`](roles/catalog/puredata.md) | Pure Data | — |
| [`audacity`](roles/catalog/audacity.md) | Audacity 4; removes 1.x–3.x first | — |
| **Education and office** | | |
| [`geogebra`](roles/catalog/geogebra.md) | GeoGebra Calculator Suite (Classic 6) | — |
| [`geogebra5`](roles/catalog/geogebra5.md) | GeoGebra Classic 5 | — |
| [`goldendict`](roles/catalog/goldendict.md) | GoldenDict-ng dictionary | — |
| [`libreoffice`](roles/catalog/libreoffice.md) | LibreOffice Still (or Fresh) | `rm_data`; `fresh` |
| [`zoom`](roles/catalog/zoom.md) | Zoom Workplace (MSI) | — |
| [`googledrive`](roles/catalog/googledrive.md) | Google Drive for desktop | — |
| [`adobe_reader_dc`](roles/catalog/adobe_reader_dc.md) | Adobe Acrobat Reader 64-bit MUI | — |
| [`foxit_pdf_reader`](roles/catalog/foxit_pdf_reader.md) | Foxit PDF Reader (Burn bundle) | — |
| [`winmerge`](roles/catalog/winmerge.md) | WinMerge file and folder comparison | — |
| **Utilities and runtimes** | | |
| [`p7zip`](roles/catalog/p7zip.md) | 7-Zip (MSI) | `32bit` |
| [`peazip`](roles/catalog/peazip.md) | PeaZip | — |
| [`winrar`](roles/catalog/winrar.md) | WinRAR, per-language installer | language token |
| [`powertoys`](roles/catalog/powertoys.md) | Microsoft PowerToys | — |
| [`windirstat`](roles/catalog/windirstat.md) | WinDirStat | — |
| [`ntop`](roles/catalog/ntop.md) | NTop console process viewer, portable | — |
| [`nircmd`](roles/catalog/nircmd.md) | NirCmd, portable | — |
| [`putty`](roles/catalog/putty.md) | PuTTY | — |
| [`winscp`](roles/catalog/winscp.md) | WinSCP | — |
| [`filezilla`](roles/catalog/filezilla.md) | FileZilla Client | — |
| [`rustdesk`](roles/catalog/rustdesk.md) | RustDesk remote desktop | — |
| [`vcredist14`](roles/catalog/vcredist14.md) | Visual C++ 2015–2022 x64 runtime (dependency of several roles) | — |
| [`virtiogt`](roles/catalog/virtiogt.md) | KVM/QEMU VirtIO guest tools | — |
| [`winfsp`](roles/catalog/winfsp.md) | WinFsp plus the VirtIO-FS service, for KVM guests | — |
| [`patchcleaner`](roles/catalog/patchcleaner.md) | PatchCleaner (orphaned `C:\Windows\Installer` files); install only | — |
| [`driver_reviver`](roles/catalog/driver_reviver.md) | Driver Reviver (trial) | — |

## Management

| Role | What | Actions |
|---|---|---|
| **System and maintenance** | | |
| [`wu`](roles/management/wu.md) | Windows Update: install in rounds, pause/resume, Settings refresh, reset | `run`, `scan`, `sync_ui`, `reset`, `on`, `off`, `pause`, `resume`, `max_pause_days`, `is_paused`, `policy_standard` |
| [`sysinfo`](roles/management/sysinfo.md) | read-only inventory: OS, hardware, disks, network, TPM, WU | `on`, `os`, `security`, `wu`, `full`, `save` |
| [`optimize`](roles/management/optimize.md) | Optimize-Volume: retrim SSDs, defragment HDDs | `on` |
| [`chkdsk`](roles/management/system-tools.md#chkdsk) | Check Disk | `on` |
| [`sfc`](roles/management/system-tools.md#sfc) | System File Checker | `on` |
| [`wim`](roles/management/system-tools.md#wim) | DISM component store: CheckHealth, ScanHealth, RestoreHealth | `check`, `scan`, `repair` |
| [`win_iso`](roles/management/win_iso.md) | unattended Windows ISO with OpenSSH, built on the controller | `build[-msi\|dism\|none]`, `info`, `on` |
| [`ps_policy`](roles/management/ps_policy.md) | machine-wide PowerShell 5.1 execution policy | `set`, `reset`, `on`, `off`, `info` |
| [`oobe`](roles/management/system-tools.md#oobe) | show (`on`) or skip (`off`) the OOBE privacy and first-logon screens | `on`, `off` |
| [`scoobe`](roles/management/scoobe.md) | suppress "finish setting up your device" after updates | `info`, `off`, `on` |
| [`widgets`](roles/management/system-tools.md#widgets) | allow or disable Windows 11 Widgets by policy | `on`, `off` |
| **Sessions and power** | | |
| [`lock`](roles/management/lock.md) | maintenance mode: logon banner, restricted logon, logoff | `on`, `off`, `reset` |
| [`autologon`](roles/management/autologon.md) | automatic logon for one account | `on`, `off` |
| [`ms_account`](roles/management/system-tools.md#ms_account) | block (`on`) or allow (`off`) Microsoft accounts by policy | `on`, `off` |
| [`logoff`](roles/management/system-tools.md#logoff) | log off every interactive session | `on` |
| [`restart`](roles/management/restart.md) | controlled reboot, optionally only when one is pending | `on`, `if-pending` |
| [`shutdown`](roles/management/system-tools.md#shutdown) | shut down and wait until the host is offline | `on`, `wait`, `no_wait`, `if-nouser`, `abort` (`a`) |
| [`autoshutdown`](roles/management/autoshutdown.md) | scheduled task shutting the host down at set times | `on`, `off`, `info` |
| [`wol`](roles/management/system-tools.md#wol) | Wake-on-LAN from the controller | `on` |
| [`ping`](roles/management/system-tools.md#ping) | connectivity test | `on` |
| **Network and access** | | |
| [`domain`](roles/management/domain.md) | Active Directory join, leave, status | `status`, `join`, `leave`, `on`, `off` |
| [`openssh`](roles/management/openssh.md) | OpenSSH Server: info, MSI upgrade, hardening (`secure_ssh`: deprecated alias) | `info`, `update`, `harden`, `unharden`, `on`, `off` |
| [`file_copy`](roles/management/file_copy.md) | copy files to and from hosts, per-user folders too | `push`, `pull`, `status`, `remove`, `on`, `off` |
| **Appearance, every profile** | | |
| [`wallpaper`](roles/management/wallpaper.md) | set and lock the desktop wallpaper | `on`, `off`, `set`, `reset`, `lock`, `unlock`, `clear_history` |
| [`display_scale`](roles/management/display_scale.md) | display scaling | `set`, `reset`, `on`, `off`, `info` |
| [`visual_effects`](roles/management/visual_effects.md) | Performance Options presets, for old hardware | `set`, `reset`, `on`, `off`, `info` |
