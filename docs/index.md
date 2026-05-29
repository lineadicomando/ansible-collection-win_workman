# lineadicomando.win_workman — Documentation

> **Work in progress** — This documentation is a preliminary draft and may be
> incomplete or inaccurate.

Ansible collection for managing **Windows 11 workstations** (not Windows Server).
Designed for classroom and lab environments; covers software deployment, system
hardening, UX configuration, and lab-specific infrastructure (Veyon, SEB).

---

## Quick start

```yaml
# requirements.yml
collections:
  - name: git+https://github.com/lineadicomando/ansible-collection-win_workman
    type: git
    version: main
```

```yaml
# playbook
- name: Configure workstations
  hosts: lab_pcs
  roles:
    - role: lineadicomando.win_workman.dispatcher
      vars:
        win_workman_tasks:
          - chrome
          - vscode
          - python312
          - veyon-on-student
```

Tasks are **dash-separated strings**: `<schema>[-<action>[-<arg>...]]`.
See [Architecture](architecture.md) for the full syntax.

---

## Role families

The collection has two distinct role families:

- **Catalog roles** — schema-based roles for installable software. Each defines a
  `win_workman_<schema>_schema` variable consumed by `pkg_utils`. Supports `on`,
  `off`, `download`, `copy`, `info`, and role-specific actions.
- **Management roles** — procedural roles for workstation-level operations (system
  maintenance, OS configuration, session control, network). No schema variable;
  actions map directly to system tasks.

---

## Documentation index

| File | Contents |
|---|---|
| [architecture.md](architecture.md) | Dispatcher+schema pattern, task string syntax, actions, pkg_utils pipeline |
| [mcp.md](mcp.md) | MCP server — tools, manifest format, Claude Desktop wiring |
| [roles/core/dispatcher.md](roles/core/dispatcher.md) | `dispatcher` — entry point |
| [roles/core/pkg_utils.md](roles/core/pkg_utils.md) | `pkg_utils` — package schema format and operations |
| [roles/catalog/chrome.md](roles/catalog/chrome.md) | `chrome` — arch selection, shortcuts, privacy, rm_data |
| [roles/catalog/firefox.md](roles/catalog/firefox.md) | `firefox` — locale detection, private/kiosk mode, privacy, rm_data |
| [roles/catalog/edge.md](roles/catalog/edge.md) | `edge` — policy, privacy, rm_data (uninstall not supported) |
| [roles/catalog/brave.md](roles/catalog/brave.md) | `brave` — privacy-focused browser |
| [roles/catalog/opera.md](roles/catalog/opera.md) | `opera` — built-in VPN and battery saver browser |
| [roles/catalog/vivaldi.md](roles/catalog/vivaldi.md) | `vivaldi` — Chromium-based browser with advanced tab management |
| [roles/catalog/vscode.md](roles/catalog/vscode.md) | `vscode` — source-code editor and IDE |
| [roles/catalog/python310.md](roles/catalog/python310.md) | `python310` — Python 3.10 interpreter |
| [roles/catalog/python311.md](roles/catalog/python311.md) | `python311` — Python 3.11 interpreter |
| [roles/catalog/python312.md](roles/catalog/python312.md) | `python312` — Python 3.12 interpreter and IDLE |
| [roles/catalog/python313.md](roles/catalog/python313.md) | `python313` — Python 3.13 interpreter |
| [roles/catalog/python314.md](roles/catalog/python314.md) | `python314` — Python 3.14 interpreter |
| [roles/catalog/embarcadero_devcpp.md](roles/catalog/embarcadero_devcpp.md) | `embarcadero_devcpp` — C++ IDE |
| [roles/catalog/orwell_devcpp.md](roles/catalog/orwell_devcpp.md) | `orwell_devcpp` — C++ IDE community fork |
| [roles/catalog/laragon.md](roles/catalog/laragon.md) | `laragon` — portable WAMP/LEMP stack |
| [roles/catalog/mysql_workbench.md](roles/catalog/mysql_workbench.md) | `mysql_workbench` — database administration tool |
| [roles/catalog/mysql_server.md](roles/catalog/mysql_server.md) | `mysql_server` — MySQL Server 9.x database engine |
| [roles/catalog/dbeaver.md](roles/catalog/dbeaver.md) | `dbeaver` — universal database tool |
| [roles/catalog/netbeans.md](roles/catalog/netbeans.md) | `netbeans` — Apache NetBeans IDE for Java and web development |
| [roles/catalog/postman.md](roles/catalog/postman.md) | `postman` — API development platform |
| [roles/catalog/git.md](roles/catalog/git.md) | `git` — Git for Windows version control |
| [roles/catalog/gimp.md](roles/catalog/gimp.md) | `gimp` — image manipulation and editing |
| [roles/catalog/inkscape.md](roles/catalog/inkscape.md) | `inkscape` — vector graphics editor |
| [roles/catalog/notepadpp.md](roles/catalog/notepadpp.md) | `notepadpp` — Notepad++ text and source code editor |
| [roles/catalog/vlc.md](roles/catalog/vlc.md) | `vlc` — multimedia player |
| [roles/catalog/puredata.md](roles/catalog/puredata.md) | `puredata` — visual programming language for audio |
| [roles/catalog/autocadlt2026_en.md](roles/catalog/autocadlt2026_en.md) | `autocadlt2026_en` — 2D CAD (English) |
| [roles/catalog/autocadlt2026_it.md](roles/catalog/autocadlt2026_it.md) | `autocadlt2026_it` — 2D CAD (Italian) |
| [roles/catalog/sketchup2026.md](roles/catalog/sketchup2026.md) | `sketchup2026` — 3D modeling software |
| [roles/catalog/blender.md](roles/catalog/blender.md) | `blender` — 3D creation suite |
| [roles/catalog/adobe_reader_dc.md](roles/catalog/adobe_reader_dc.md) | `adobe_reader_dc` — Adobe Acrobat Reader DC PDF viewer |
| [roles/catalog/foxit_pdf_reader.md](roles/catalog/foxit_pdf_reader.md) | `foxit_pdf_reader` — Foxit PDF Reader |
| [roles/catalog/p7zip.md](roles/catalog/p7zip.md) | `p7zip` — file archive compression |
| [roles/catalog/peazip.md](roles/catalog/peazip.md) | `peazip` — file archiver and manager |
| [roles/catalog/powertoys.md](roles/catalog/powertoys.md) | `powertoys` — Microsoft PowerToys utilities suite |
| [roles/catalog/windirstat.md](roles/catalog/windirstat.md) | `windirstat` — disk usage analyzer |
| [roles/catalog/ntop.md](roles/catalog/ntop.md) | `ntop` — Windows port of Unix `top` (process monitor) |
| [roles/catalog/nircmd.md](roles/catalog/nircmd.md) | `nircmd` — system utilities command-line tool |
| [roles/catalog/winfsp.md](roles/catalog/winfsp.md) | `winfsp` — file system proxy framework |
| [roles/catalog/putty.md](roles/catalog/putty.md) | `putty` — SSH, Telnet, and serial console client |
| [roles/catalog/winscp.md](roles/catalog/winscp.md) | `winscp` — SFTP/FTP/SCP client |
| [roles/catalog/filezilla.md](roles/catalog/filezilla.md) | `filezilla` — FTP/SFTP/FTPS client |
| [roles/catalog/vcredist14.md](roles/catalog/vcredist14.md) | `vcredist14` — Visual C++ runtime libraries |
| [roles/catalog/virtiogt.md](roles/catalog/virtiogt.md) | `virtiogt` — KVM/QEMU guest tools |
| [roles/catalog/geogebra.md](roles/catalog/geogebra.md) | `geogebra` — dynamic mathematics software |
| [roles/catalog/geogebra5.md](roles/catalog/geogebra5.md) | `geogebra5` — mathematics software classic version |
| [roles/catalog/libreoffice.md](roles/catalog/libreoffice.md) | `libreoffice` — office productivity suite |
| [roles/catalog/zoom.md](roles/catalog/zoom.md) | `zoom` — video conferencing and collaboration |
| [roles/catalog/rustdesk.md](roles/catalog/rustdesk.md) | `rustdesk` — open-source remote desktop |
| [roles/catalog/seb.md](roles/catalog/seb.md) | `seb` — Safe Exam Browser install and client settings generation |
| [roles/catalog/veyon.md](roles/catalog/veyon.md) | `veyon` — classroom management agent |
| [roles/catalog/patchcleaner.md](roles/catalog/patchcleaner.md) | `patchcleaner` — WinSxS / superseded update cleanup |
| [roles/management/optimize.md](roles/management/optimize.md) | `optimize` — volume optimisation and defrag |
| [roles/management/wu.md](roles/management/wu.md) | `wu` — Windows Update enable/disable/pause/policy |
| [roles/management/wallpaper.md](roles/management/wallpaper.md) | `wallpaper` — set/reset/lock/unlock across all profiles |
| [roles/management/lock.md](roles/management/lock.md) | `lock` — maintenance mode, login banner, logon restrictions |
| [roles/management/autologon.md](roles/management/autologon.md) | `autologon` — automatic logon configuration |
| [roles/management/system-tools.md](roles/management/system-tools.md) | `chkdsk`, `sfc`, `oobe`, `widgets`, `wim`, `ms_account`, `secure_ssh`, `logoff`, `restart`, `shutdown`, `ping`, `wol` |

---

## Role index

### Core
- [`dispatcher`](roles/core/dispatcher.md) — entry point, iterates task list
- [`pkg_utils`](roles/core/pkg_utils.md) — low-level package operations

### Catalog — Browsers
[`brave`](roles/catalog/brave.md) · [`chrome`](roles/catalog/chrome.md) · [`edge`](roles/catalog/edge.md) · [`firefox`](roles/catalog/firefox.md) · [`opera`](roles/catalog/opera.md) · [`seb`](roles/catalog/seb.md) · [`vivaldi`](roles/catalog/vivaldi.md)

### Catalog — Developer tools
[`vscode`](roles/catalog/vscode.md) · [`notepadpp`](roles/catalog/notepadpp.md) · [`git`](roles/catalog/git.md) · [`embarcadero_devcpp`](roles/catalog/embarcadero_devcpp.md) · [`orwell_devcpp`](roles/catalog/orwell_devcpp.md) · [`laragon`](roles/catalog/laragon.md) · [`mysql_server`](roles/catalog/mysql_server.md) · [`mysql_workbench`](roles/catalog/mysql_workbench.md) · [`dbeaver`](roles/catalog/dbeaver.md) · [`postman`](roles/catalog/postman.md) · [`netbeans`](roles/catalog/netbeans.md) · [`python310`](roles/catalog/python310.md) · [`python311`](roles/catalog/python311.md) · [`python312`](roles/catalog/python312.md) · [`python313`](roles/catalog/python313.md) · [`python314`](roles/catalog/python314.md)

### Catalog — Graphics, CAD & Multimedia
[`gimp`](roles/catalog/gimp.md) · [`inkscape`](roles/catalog/inkscape.md) · [`blender`](roles/catalog/blender.md) · [`sketchup2026`](roles/catalog/sketchup2026.md) · [`autocadlt2026_en`](roles/catalog/autocadlt2026_en.md) · [`autocadlt2026_it`](roles/catalog/autocadlt2026_it.md) · [`vlc`](roles/catalog/vlc.md) · [`puredata`](roles/catalog/puredata.md)

### Catalog — Education & Productivity
[`geogebra`](roles/catalog/geogebra.md) · [`geogebra5`](roles/catalog/geogebra5.md) · [`libreoffice`](roles/catalog/libreoffice.md) · [`zoom`](roles/catalog/zoom.md)

### Catalog — Utilities & Runtimes
[`adobe_reader_dc`](roles/catalog/adobe_reader_dc.md) · [`foxit_pdf_reader`](roles/catalog/foxit_pdf_reader.md) · [`p7zip`](roles/catalog/p7zip.md) · [`peazip`](roles/catalog/peazip.md) · [`powertoys`](roles/catalog/powertoys.md) · [`windirstat`](roles/catalog/windirstat.md) · [`ntop`](roles/catalog/ntop.md) · [`nircmd`](roles/catalog/nircmd.md) · [`winfsp`](roles/catalog/winfsp.md) · [`putty`](roles/catalog/putty.md) · [`winscp`](roles/catalog/winscp.md) · [`filezilla`](roles/catalog/filezilla.md) · [`vcredist14`](roles/catalog/vcredist14.md) · [`virtiogt`](roles/catalog/virtiogt.md) · [`patchcleaner`](roles/catalog/patchcleaner.md) · [`rustdesk`](roles/catalog/rustdesk.md)

### Catalog — Classroom & Lab
[`veyon`](roles/catalog/veyon.md)

### Management — System & OS
[`optimize`](roles/management/optimize.md) · [`wu`](roles/management/wu.md) · [`oobe`](roles/management/system-tools.md#oobe) · [`widgets`](roles/management/system-tools.md#widgets) · [`sfc`](roles/management/system-tools.md#sfc) · [`chkdsk`](roles/management/system-tools.md#chkdsk) · [`wim`](roles/management/system-tools.md#wim)

### Management — Session & Access
[`autologon`](roles/management/autologon.md) · [`ms_account`](roles/management/system-tools.md#ms_account) · [`lock`](roles/management/lock.md) · [`logoff`](roles/management/system-tools.md#logoff) · [`restart`](roles/management/system-tools.md#restart) · [`shutdown`](roles/management/system-tools.md#shutdown)

### Management — Network & Security
[`secure_ssh`](roles/management/system-tools.md#secure_ssh) · [`wol`](roles/management/system-tools.md#wol) · [`ping`](roles/management/system-tools.md#ping)

### Management — UX & Appearance
[`wallpaper`](roles/management/wallpaper.md) · [`widgets`](roles/management/system-tools.md#widgets)
