# Software roles of win_workman

Packages installed, removed and configured. Written by tools/fleet_skills.py from roles/*/meta/mcp.yaml: do not edit by hand.

### adobe_reader_dc: Adobe Acrobat Reader DC

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### audacity: Audacity

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Notes: Audacity 4.x, the new major line: MSI package (3.x and earlier are Inno Setup), x86_64 only — upstream also publishes an arm64 MSI, which this role does not cover. Installed under %ProgramFiles%\Audacity 4. Two things the installer does not do on its own: it declares no ALLUSERS, so the role passes ALLUSERS=1 or the shortcuts land in the profile of the connecting Ansible user instead of being visible to everyone; and its UpgradeCode supersedes only the 4.x line, so `on` first uninstalls any Audacity matching win_workman_audacity_superseded_searchnames (1.x, 2.x, 3.x by default), which would otherwise stay installed alongside it. `off` removes only 4.x.

### autocadlt2026: AutoCAD LT 2026

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
- `autocadlt2026-on`: Install AutoCAD LT 2026 (no-op if already installed)
- `autocadlt2026-off`: Uninstall AutoCAD LT 2026
Notes: Uses explicit on/off actions instead of the standard pkg_utils flow. Locale (en/it) is auto-detected from the host and can be forced with autocadlt2026-on-it; the two locales are separate ODIS bundles and cannot coexist, so "on" fails if the other one is installed. autocadlt2026-off-full also purges the shared Autodesk stack, including C:\Program Files\Autodesk: use it only when no other Autodesk product remains. Installs side by side with older releases: run autocadlt2023-off first to replace rather than add.

### blender: Blender

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### brave: Brave Browser

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Variables:
- `win_workman_brave_shortcuts` bool (default `False`): Create shortcuts on Desktop and Start Menu
- `win_workman_brave_shortcut_url` str: Default URL to open; empty means default new tab
- `win_workman_brave_shortcut_no_first_run` bool (default `True`): Pass --no-first-run flags to shortcut

### chrome: Google Chrome

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
- `chrome-privacy`: Requires an 'on' or 'off' argument (chrome-privacy-on). Applies or removes lockdown policies under HKLM\SOFTWARE\Policies\Google\Chrome. 'on' disables sign-in, sync, guest mode, profile creation, password manager, autofill, telemetry and extension installs (the last one unless win_workman_chrome_block_extensions is false), force-installs the extensions in win_workman_chrome_extension_forcelist, and clears cookies, cache and history on browser exit. 'off' removes those policies. Does not delete existing profile data.
- `chrome-rm`: Requires the 'profile' argument (chrome-rm-profile). Force-closes Chrome, then deletes AppData\Local\Google\Chrome for every local user profile on the host and removes per-profile Chrome desktop shortcuts. Affects all local users, not a single one.
Variables:
- `win_workman_chrome_shortcuts` bool (default `False`): Create shortcuts on Desktop and Start Menu
- `win_workman_chrome_shortcut_url` str: Default URL to open; empty means default new tab
- `win_workman_chrome_shortcut_no_first_run` bool (default `True`): Pass --no-first-run --no-default-browser-check flags to shortcut
- `win_workman_chrome_block_extensions` bool (default `True`): With chrome-privacy-on, block installation of all extensions (ExtensionInstallBlocklist = *). Set to false to apply the other privacy policies and leave extension installs allowed.
- `win_workman_chrome_extension_allowlist` list (default `[]`): With chrome-privacy-on and extensions blocked, IDs of the extensions users may still install from the Chrome Web Store (ExtensionInstallAllowlist). E.g. ghbmnnjooekpmoecnnnilnnbdlolhkhi for Google Docs Offline, which the context-menu copy and paste in Docs and Sheets relies on. Users still have to install them; see win_workman_chrome_extension_forcelist to install them for everyone.
- `win_workman_chrome_extension_forcelist` list (default `[]`): With chrome-privacy-on, extensions Chrome installs by itself for every user, who cannot remove them (ExtensionInstallForcelist). They are installed whether or not the other extensions are blocked. An entry is an extension ID, taken from the Chrome Web Store, or "<id>;<update URL>". E.g. ghbmnnjooekpmoecnnnilnnbdlolhkhi for Google Docs Offline.
- `win_workman_chrome_clear_site_data_on_exit` bool (default `True`): With chrome-privacy-on, clear cookies and site data when Chrome closes. Set to false to keep Google sign-ins and offline data between sessions; cache and history are cleared either way.
Notes: Accepts '32bit' task argument. Closes running Chrome before install/uninstall.

### dbeaver: DBeaver Community

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### driver_reviver: Driver Reviver

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Notes: Commercial driver updater by ReviverSoft (Corel). The setup installs without a licence and runs as a trial: it scans and reports outdated drivers, but the actual update needs a registration code entered in the GUI, so there is nothing to automate beyond the install. The same setup also deploys the shared "ReviverSoft Smart Monitor" companion, which registers an auto-start service but no Uninstall entry: it is invisible to detect_sw and driver_reviver-off leaves it behind. See the catalog doc for how to remove it by hand.

### edge: Microsoft Edge

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
- `edge-off`: Not implemented: it accepts the action and does nothing. Edge cannot be uninstalled because Windows components depend on it; removing it leaves the system unstable (verified on a lab machine).
- `edge-privacy`: Requires an 'on' or 'off' argument (edge-privacy-on). Applies or removes lockdown policies under HKLM\SOFTWARE\Policies\Microsoft\Edge. 'on' disables sign-in, sync, password manager, autofill, history saving, telemetry and extension installs (except win_workman_edge_extension_allowlist), force-installs the extensions in win_workman_edge_extension_forcelist, and clears browsing data on exit. 'off' removes those policies. Does not delete existing profile data.
- `edge-rm`: Remove the Edge profile directory for a specific user
Variables:
- `win_workman_edge_shortcuts` bool (default `False`): Create shortcuts on Desktop and Start Menu
- `win_workman_edge_shortcut_url` str: Default URL to open; empty means default new tab
- `win_workman_edge_shortcut_no_first_run` bool (default `True`): Pass --no-first-run flags to shortcut
- `win_workman_edge_extension_allowlist` list (default `[]`): With edge-privacy-on, IDs of the extensions users may still install despite the blocklist (ExtensionInstallAllowlist). IDs are looked up in the Edge Add-ons store; one from the Chrome Web Store also needs the user to turn on "Allow extensions from other stores".
- `win_workman_edge_extension_forcelist` list (default `[]`): With edge-privacy-on, extensions Edge installs by itself for every user, who cannot remove them (ExtensionInstallForcelist), despite the blocklist. An entry is "<id>;<update URL>"; a bare ID is looked up in the Edge Add-ons store. For a Chrome Web Store extension add ";https://clients2.google.com/service/update2/crx", e.g. ghbmnnjooekpmoecnnnilnnbdlolhkhi;https://clients2.google.com/service/update2/crx for Google Docs Offline.
Notes: Accepts '32bit' task argument. Closes running Edge before install. This role installs and upgrades Edge but never removes it: see the 'off' action.

### embarcadero_devcpp: Embarcadero Dev-C++

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### filezilla: FileZilla

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### firefox: Mozilla Firefox

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
- `firefox-privacy`: Clear user data (history, cache, cookies) for all Firefox profiles
- `firefox-rm`: Remove the Firefox profile directory for a specific user
Variables:
- `win_workman_firefox_shortcuts` bool (default `False`): Create shortcuts on Desktop and Start Menu
- `win_workman_firefox_shortcut_url` str: Default URL to open; empty means default new tab
- `win_workman_firefox_shortcut_no_first_run` bool (default `True`): Pass --no-first-run flag to shortcut
- `win_workman_firefox_arch` str (default `64bit`): Architecture variant; '32bit' or '64bit'
Notes: Accepts '32bit' task argument. Closes running Firefox before install/uninstall.

### foxit_pdf_reader: Foxit PDF Reader

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### gcpw: Google Credential Provider for Windows (GCPW)

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Variables:
- `win_workman_gcpw_domains_allowed_to_login` str: Comma-separated list of Google Workspace domains allowed to sign in (required for the 'on' action; e.g. 'example.com' or 'school.edu,other.edu')
Notes: Accepts '32bit' task argument for 32-bit installer. win_workman_gcpw_domains_allowed_to_login must be set to a valid domain list before running the 'on' action — the role fails if absent or malformed.

### geogebra: GeoGebra Classic 6

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### geogebra5: GeoGebra Classic 5

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### gimp: GIMP

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### git: Git

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### goldendict: GoldenDict-ng

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### googledrive: googledrive

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### inkscape: Inkscape

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### laragon: Laragon

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### libreoffice: LibreOffice

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
- `libreoffice-rm_data`: Remove LibreOffice user profile data (resets per-user settings)
Notes: Accepts the 'fresh' task argument (libreoffice-on-fresh, libreoffice-info-fresh): installs the Fresh branch instead of the default Still branch. Still is the branch The Document Foundation recommends for institutional deployments.

### mysql_server: MySQL Server

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### mysql_workbench: MySQL Workbench

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### netbeans: Apache NetBeans

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### nircmd: NirCmd

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### nodejs26: Node.js 26 LTS

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Variables:
- `win_workman_nodejs26_firewall` bool (default `False`): On 'on', allow node.exe inbound and remove the rules left by the firewall prompt and any block rule
- `win_workman_nodejs26_firewall_profiles` list (default `['domain', 'private', 'public']`): Firewall profiles the rule applies to
- `win_workman_nodejs26_firewall_remoteip` str (default `LocalSubnet`): Allowed sources, LocalSubnet, Any, or a list of addresses/ranges
Notes: One Node.js major line per host: every Node.js MSI shares the same UpgradeCode, so 'on' removes any other version (24, 27, ...) before installing 26, and 'off' removes only 26. 'on' also runs ps_policy-on (RemoteSigned, LocalMachine) so that npm and npx work from PowerShell; nodejs26-on-nodep skips it. The PATH of global npm packages (%APPDATA%\npm) is not added for the users. With win_workman_nodejs26_firewall true, 'on' adds an inbound allow rule for node.exe (any port, from win_workman_nodejs26_firewall_remoteip, LocalSubnet by default) and removes the rules the firewall prompt leaves (block or allow) and any other block rule on node.exe; 'off' always removes the rule. End of life 2029-04-30.

### notepadpp: Notepad++

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### ntop: ntopng

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### opera: Opera Browser

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Variables:
- `win_workman_opera_shortcuts` bool (default `False`): Create shortcuts on Desktop and Start Menu
- `win_workman_opera_shortcut_url` str: Default URL to open; empty means default new tab
- `win_workman_opera_shortcut_no_first_run` bool (default `True`): Pass --no-first-run flags to shortcut

### orwell_devcpp: Orwell Dev-C++

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### p7zip: 7-Zip

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### patchcleaner: PatchCleaner

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### peazip: PeaZip

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### postman: Postman

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### powertoys: Microsoft PowerToys

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### puredata: Pure Data

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### putty: PuTTY

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### python310: Python 3.10

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### python311: Python 3.11

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### python312: Python 3.12

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### python313: Python 3.13

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### python314: Python 3.14

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### python315: Python 3.15

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### redpanda_cpp: Red Panda C++

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Notes: Modern alternative to orwell_devcpp and embarcadero_devcpp: same Dev-C++ workflow and file associations (.dev, .c, .cpp), but a maintained IDE bundled with MinGW64 GCC 11.5.0. Installed for all users under %ProgramFiles%\RedPanda-Cpp.

### rustdesk: RustDesk

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### seb: Safe Exam Browser

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
- `seb-deploy`: Install SEB and deploy the current win_workman_seb_client_settings as a .seb config file
- `seb-undeploy`: Remove the deployed .seb config file (leaves SEB installed)
- `seb-config_key`: Print the Browser Exam Key for the current configuration (for server-side verification)
Variables:
- `win_workman_seb_client_settings` dict (default `(baseline lockdown preset)`): Full SEB client settings dict. Key fields: startURL, allowQuit, browserViewMode (1=fullscreen), createNewDesktop, killExplorerShell, allowScreenSharing (required for Veyon), sebServicePolicy (2=enforce), URLFilterEnable, URLFilterRules, clipboardPolicy, sendBrowserExamKey.
- `win_workman_seb_client_settings_dest` str (default `C:\ProgramData\SafeExamBrowser\SebClientSettings.seb`): Destination path for the deployed .seb config file
- `win_workman_seb_shortcuts` bool (default `False`): Create a Desktop shortcut for SEB
Notes: Use 'deploy' instead of 'on' when you want to push a specific exam config. allowScreenSharing must be true when Veyon is used alongside SEB (prevents black screen). Accepts '32bit' task argument.

### sketchup2026: SketchUp 2026

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
- `sketchup2026-license`: Deploy activation_info.txt with the classic/network serial number and authorization code, so the License window opens pre-filled instead of being typed by hand. When the credentials differ from the deployed ones it also removes SketchUp.lic, so the next launch activates the new license
- `sketchup2026-unlicense`: Remove the deployed activation_info.txt and the activated SketchUp.lic
Variables:
- `win_workman_sketchup2026_serial_number` str: Classic/network license serial number (keep it in a vault)
- `win_workman_sketchup2026_auth_code` str: Classic/network license authorization code (keep it in a vault)
- `win_workman_sketchup2026_allow_reactivation` bool (default `True`): Add the allow_reactivation flag so a renewed license re-activates on its own
- `win_workman_sketchup2026_program_data_dir` str (default `C:\ProgramData\SketchUp\SketchUp 2026`): Directory SketchUp reads activation_info.txt from
- `win_workman_sketchup2026_force_close` bool (default `False`): 'license' and 'unlicense' fail on a host where SketchUp or LayOut is running and a license change is due; true kills the processes instead (unsaved work is lost)
Notes: Trimble offers no command-line activation. The 'license' action deploys activation_info.txt; verified on SketchUp 2026, simply opening the application once per workstation then activates the license with no user interaction at all (Trimble's docs still describe a manual "Add License" click, which turns out not to be needed). The activated license lives in SketchUp.lic next to it and wins over activation_info.txt: 'license' removes it when the credentials change, which was verified to switch a workstation from one network license to another on the next launch. Trimble documents seat removal only through Help > License > Remove License. A seat extracted for offline use is not detected and stays taken until it expires. Run 'unlicense' before 'off': whether the uninstaller removes SketchUp.lic on its own has not been verified.

### tinycad: TinyCAD

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### vcredist14: Visual C++ Redistributable 2015-2022

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### veyon: Veyon

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
- `veyon-config`: Deploy Veyon configuration and keypairs to target hosts
Variables:
- `win_workman_veyon_master` bool (default `False`): Install Veyon with Master component (teacher station); false installs Service only
- `win_workman_veyon_labs` list (default `[]`): Inventory groups whose hosts become Veyon locations on this master: a group name (the location takes its name) or {group, name} to keep the location's own name, e.g. {group: win_managed, name: Lab A}
- `win_workman_veyon_keypairs_dir` str (default `{{ win_workman_storage_path }}/veyon`): Local controller path where Veyon keypairs are stored
- `win_workman_veyon_lab_force_replace` bool (default `False`): Remove and recreate each location instead of reconciling it in place
- `win_workman_veyon_lab_prune` bool (default `False`): Also remove computers of the location that are not in the inventory group (by default they are kept and reported as unmanaged)
Notes: Use the dedicated 'veyon' playbook (run_playbook) for full lab setup including key generation. Use run_tasks with 'veyon-config' only to push config/key updates to already-provisioned hosts.

### virtiogt: VirtIO Guest Tools

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### vivaldi: Vivaldi Browser

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Variables:
- `win_workman_vivaldi_shortcuts` bool (default `False`): Create shortcuts on Desktop and Start Menu
- `win_workman_vivaldi_shortcut_url` str: Default URL to open; empty means default new tab
- `win_workman_vivaldi_shortcut_no_first_run` bool (default `True`): Pass --no-first-run flags to shortcut

### vlc: VLC Media Player

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### vscode: Visual Studio Code

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Variables:
- `win_workman_vscode_shortcuts` bool (default `False`): Create shortcuts on Desktop and Start Menu

### windirstat: WinDirStat

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### winfsp: WinFsp

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### winmerge: WinMerge

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### winrar: WinRAR

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
Variables:
- `win_workman_winrar_shortcut_desktop` bool (default `True`): Create a Desktop shortcut
- `win_workman_winrar_shortcut_startmenu` bool (default `True`): Create a Start Menu shortcut

### winscp: WinSCP

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.

### zed: Zed

Common actions: `download`, `usr` (default).
Install scopes: usr.
Notes: Per-user only: the installer cannot install machine-wide, so use zed-usr-<verb> (zed alone means zed-usr-on). Installation happens at each target's next logon; zed-usr-apply runs it now for logged-on users. Zed updates itself inside each profile, and the agent never downgrades.

### zoom: Zoom

Common actions: `on` (default), `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`.
