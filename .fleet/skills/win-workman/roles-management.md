# Management roles of win_workman

The system, sessions, updates, maintenance. Written by tools/fleet_skills.py from roles/*/meta/mcp.yaml: do not edit by hand.

### autocadlt2023: AutoCAD LT 2023

- `autocadlt2023-off`: Uninstall AutoCAD LT 2023 (any locale)
Notes: Removal-only role: "off" is the only supported action and must be spelled out (autocadlt2023-off); win_workman never installs AutoCAD LT 2023. Use it before autocadlt2026, which installs side by side and does not replace older versions. By default the shared Autodesk stack (AdODIS, Access, CER, Identity Manager, AdSSO, Genuine Service) is left in place, because newer releases reuse it. autocadlt2023-off-full additionally clears what is left of the 2023 product family - the Material Library 2023 packages, the emptied install directory and the ACDLT2023 licensing logs - and still does not touch the shared stack.

### autologon: Windows Autologon

- `autologon-on`: Enable automatic logon with specified credentials
- `autologon-off`: Disable automatic logon and clear stored credentials
Variables:
- `win_workman_autologon_user` str (default `{{ ansible_user }}`): Username for autologon; defaults to the Ansible connection user
- `win_workman_autologon_password` str (default `{{ ansible_password }}`): Password for autologon; defaults to the Ansible connection password
- `win_workman_autologon_restart` bool (default `False`): Restart the host after on/off, only when something changed
Notes: The password is stored as the LSA secret DefaultPassword, decryptable by any administrator of the host. Use a dedicated account and a vaulted password.

### autoshutdown: Automatic Shutdown

- `autoshutdown-on`: Create or update the scheduled task that shuts the host down at the times in win_workman_autoshutdown_schedule (default action). A time passed as task argument, HHMM, means that time on every day and wins over the variable, e.g. autoshutdown-on-1830
- `autoshutdown-off`: Remove the scheduled task
- `autoshutdown-info`: Report the scheduled times, the task state and its last outcome without changing anything
Variables:
- `win_workman_autoshutdown_schedule` str (default `18:30`): A quoted "HH:MM" time for every day, or a list of entries, each a time or a mapping {time: "HH:MM", days: [monday, ...]}; an entry without days applies to every day, a day in no entry has no shutdown. Host local time
- `win_workman_autoshutdown_warning` int (default `60`): Seconds of warning shown to the logged-on user before the shutdown; 0 shuts down at once
- `win_workman_autoshutdown_message` str (default `Spegnimento automatico programmato: salvare il lavoro.`): Text of the warning shown to the logged-on user
- `win_workman_autoshutdown_mode` str (default `always`): always shuts down whoever is logged on. nouser (only when no user session is open) is reserved and not implemented yet: it fails validation
- `win_workman_autoshutdown_task_path` str (default `\win_workman`): Task Scheduler folder of the task, starting with a backslash
- `win_workman_autoshutdown_task_name` str (default `AutoShutdown`): Name of the scheduled task
Notes: Does not install software and does not shut down anything when run: it leaves a scheduled task on the host, which then shuts down on its own with no controller involved. To shut hosts down now use the shutdown role. Per-lab times belong in the inventory group_vars. off removes only the task with the current name and path, so run autoshutdown-off before changing either. During the warning a logged-on user can normally cancel with 'shutdown /a'. A host that was off at the scheduled time does not shut down at the next boot.

### chkdsk: Check Disk (chkdsk)

- `chkdsk-on`: Run an online scan (chkdsk /scan) on target volumes and report the outcome
Variables:
- `win_workman_chkdsk_volumes` list (default `['C']`): Drive letters to scan
Notes: The scan runs at once with the volume in use: no restart, and nothing is scheduled for the next boot. Errors it can fix are repaired online and the task reports changed. The exit code is a Volume.RepairStatus value (5 = fixed online, 13 = needs an offline scan and fix), cross-checked against the volume's dirty bit and health; Repair-Volume -Scan decides only an unknown code or a contradiction. The task fails only when an offline repair is still needed (chkdsk /spotfix or /f), with a msg naming the volume, the status and the files involved.

### display_scale: Display Scaling

- `display_scale-set`: Apply a display scale percentage (default action). The percentage can be passed as task argument, e.g. display_scale-set-150
- `display_scale-reset`: Restore the scale recommended by the display driver
- `display_scale-on`: Alias for 'set' — applies win_workman_display_scale_percent
- `display_scale-off`: Alias for 'reset'
- `display_scale-info`: Report the scale configured in every user profile without changing it
Variables:
- `win_workman_display_scale_percent` int (default `100`): Scale percentage applied when no argument is given. Supported values: 100, 125, 150, 175, 200, 225, 250, 300, 350, 400
- `win_workman_display_scale_profiles_include_default` bool (default `True`): Apply the scale to the default user profile (new user template)
- `win_workman_display_scale_clear_per_monitor` bool (default `True`): Remove per-monitor overrides (PerMonitorSettings) so the global scale takes effect on every display
Notes: The scale is a per-user setting written into each profile hive, so it applies at the next logon. Profiles of users currently logged in are skipped: the action forces a logoff first. A reboot is not required.

### domain: Active Directory Domain Membership

- `domain-status`: Report whether the host is joined to a domain or in a workgroup, and which (default, read-only)
- `domain-join`: Join the domain win_workman_domain_name, after pointing DNS at win_workman_domain_dns_servers
- `domain-leave`: Leave the domain for the workgroup win_workman_domain_workgroup (the computer account is disabled, not deleted)
- `domain-on`: Alias for join
- `domain-off`: Alias for leave
Variables:
- `win_workman_domain_name` str: DNS name of the AD domain, e.g. example.com (required by join and leave)
- `win_workman_domain_admin_user` str (default `Administrator`): Domain account that joins the computer, or disables its account on leave (used as user@win_workman_domain_name)
- `win_workman_domain_admin_password` str: Password of the domain account; a secret, from a vault-encrypted variable (required by join and leave)
- `win_workman_domain_dns_servers` list (default `[]`): DNS servers set on every adapter before joining (the domain controllers); empty leaves the adapters as they are
- `win_workman_domain_workgroup` str (default `WORKGROUP`): Workgroup the host moves to on leave
- `win_workman_domain_reboot` bool (default `True`): Reboot the host when join or leave requires it
- `win_workman_domain_set_fact` bool (default `True`): status: publish the result as the win_workman_domain_status fact (hostname, part_of_domain, domain, workgroup)
Notes: Join and leave use microsoft.ad.membership and reboot the host when needed. Pass win_workman_domain_admin_password as a secret, never in extra_vars.

### file_copy: File Copy

- `file_copy-push`: Copy files and folders from the controller to the host (default action). Idempotent: files equal to the controller copy are not sent again.
- `file_copy-pull`: Fetch files and folders from the host into win_workman_file_copy_pull_root/<dest>/<host>/[<profile>/]. A source missing on a host is reported, not an error.
- `file_copy-status`: Compare every destination with the controller copy (size and SHA1) and report match, differ or missing. Changes nothing.
- `file_copy-remove`: Delete from the host what push created. The destination folder itself is never removed. Reads the controller source to know what to delete.
- `file_copy-on`: Alias for push
- `file_copy-off`: Alias for remove
Variables:
- `win_workman_file_copy_items` list (default `[]`): The items, each a dict. src: for push a path relative to win_workman_file_copy_root, a trailing / copies the contents of a directory; for pull a host path. dest: for push the host folder that receives src; for pull a controller subfolder of the pull root. profile: a profile name, a list, a wildcard or "all"; when set, the host path is relative to that user's folder. folder: desktop (default), documents, downloads, pictures, music, videos or profile (the profile root); the folder is read from the profile, so OneDrive redirection is followed. include_default: also the Default profile, for users created later. archive: transfer a directory as a single zip.
- `win_workman_file_copy_root` str (default `{{ win_workman_storage_path }}/file_copy`): Controller folder push sources are relative to. A src that leaves it (absolute path, '..', symbolic link) fails the run.
- `win_workman_file_copy_pull_root` str (default `{{ win_workman_storage_path }}/file_copy_pull`): Controller folder pull writes to
- `win_workman_file_copy_profiles_exclude` list (default `[]`): Profiles skipped when profile is a wildcard or "all", e.g. the maintenance accounts. A profile named explicitly is never excluded.
Notes: Pass the items as extra_vars of run_tasks, e.g. {"win_workman_file_copy_items": [{"src": "esercizi/", "profile": "all", "dest": "Esercizi"}]} with t=file_copy-push. The items must be the same for every host of the run. No logoff is needed. Use archive for directories with many small files; extraction overwrites but never deletes, as win_copy does.

### galene: Galène

- `galene-on`: Default action. On the master (galene-on-master, or win_workman_galene_master true): build galene.exe on the controller if needed, install it as the Galene service with WinSW, open the firewall, write group and tokens, add the teacher shortcut. On any other host: only the shortcut to the master
- `galene-off`: Remove service, firewall rules, directory and both shortcuts (master or client)
- `galene-info`: Master: service, listening sockets, HTTP answer, firewall rules and block rules on galene.exe, version, tokens vs inventory, link speed vs clients. Client: shortcut and reachability of the master. Reports issues, changes nothing
- `galene-build`: Only download the source and WinSW and build galene.exe on the controller
Variables:
- `win_workman_galene_master` bool (default `False`): This host runs the server (teacher PC); same as the master task argument
- `win_workman_galene_master_host` str (default `first host of the teachers group`): Inventory host the client shortcuts point to
- `win_workman_galene_clients_group` str (default `students`): Inventory group whose hosts get a token on the master
- `win_workman_galene_group` str (default `lab`): Galène group (room) name
- `win_workman_galene_http_port` int (default `8443`): TCP port of the web server
- `win_workman_galene_udp_port` int (default `8444`): UDP port for all the media
- `win_workman_galene_firewall_remoteip` str (default `LocalSubnet`): Remote addresses allowed by the firewall rules (LocalSubnet, Any or a list)
- `win_workman_galene_secret_file` str (default `{{ win_workman_storage_path }}/galene/<inventory>_secret`): Controller file of the secret the tokens are derived from, created on first use
Notes: The master must be the teacher PC: the teacher opens http://localhost, a secure context, so screen and audio sharing work without a certificate. In the browser choose the whole screen and "share system audio". galene.exe is built on the controller, which needs Go (any version from 1.21; the pinned toolchain is downloaded by Go). The tokens on the master list the hosts of the clients group: after adding a client run galene-on-master again. Galène sends one stream per client: about 2.5 Mbit/s each, so a teacher PC on a 100 Mbit/s port is at its limit with 30 students (info warns about it).

### lock: Workstation Lock (maintenance mode)

- `lock-on`: Engage maintenance mode — logon banner, logon restricted to the allowed users, optionally force logoff all users; saves what the host had
- `lock-off`: Disengage maintenance mode and give back what 'on' saved; changes nothing on a host that is not locked
- `lock-reset`: Unlock without the saved state — empty legal notice, last username shown, logon right set to the fallback users, saved state dropped. For a host left locked with its saved state lost; whatever it had before the lock is not restored
Variables:
- `win_workman_mode_title` str (default `Maintenance in progress`): Title shown on the lock screen
- `win_workman_mode_text` str (default `The system is currently undergoing maintenance. Contact IT for assistance.`): Body text shown on the lock screen
- `win_workman_mode_force_logoff` bool (default `True`): Force logoff of all interactive sessions when engaging lock
- `win_workman_mode_interactive_logon_users` list (default `['Administrators']`): Groups/users still allowed to log on while lock is active
- `win_workman_mode_interactive_logon_fallback_users` list (default `['S-1-5-32-544', 'S-1-5-32-545', 'S-1-5-32-551']`): Who may log on when there is nothing to restore (off with an empty saved right, and reset). Default Administrators, Users, Backup Operators as SIDs
Notes: Does not install software. A run that stops between on and off leaves the host locked: put lock-off in the always section of a block, or run it later. Remote Desktop logons are not restricted.

### logoff: User Logoff

- `logoff-on`: Force logoff of every user session, Active or Disconnected, and wait for them to end
Variables:
- `win_workman_logoff_timeout_seconds` int (default `300`): Seconds to wait for the sessions to end; the task fails if any is left
Notes: Does not install software.

### ms_account: Microsoft Account (block/unblock)

- `ms_account-on`: Default. Block Microsoft accounts (NoConnectedUser=3, MicrosoftAccount DisableUserAuth=1): local accounts only
- `ms_account-off`: Allow Microsoft accounts again (removes both policy values)
Notes: Does not install software; manages a registry/policy setting only.

### oobe: Windows OOBE

- `oobe-on`: Enable Windows Out-Of-Box Experience (OOBE) flow
- `oobe-off`: Suppress/skip OOBE on next logon
Notes: Does not install software; manages registry keys that control the OOBE flow.

### openssh: OpenSSH Server

- `openssh-info`: Default. Report how OpenSSH Server is installed (msi, capability), its version and the state of the sshd service; changes nothing
- `openssh-update`: Upgrade an MSI installation of OpenSSH Server to the release in vars/main/msi.yaml. Checks the current sshd_config with the new sshd first, runs msiexec from a SYSTEM scheduled task outside the SSH session, reconnects and reads the outcome. Refuses a capability installation (updated by Windows Update)
- `openssh-harden`: Apply the hardened OpenSSH configuration (authorized keys, pubkey auth on, password and keyboard-interactive auth off, AllowUsers), test it with sshd -t and restart sshd if it changed
- `openssh-unharden`: Revert the OpenSSH configuration to the defaults
- `openssh-on`: Alias for harden; it installs nothing
- `openssh-off`: Alias for unharden; it never uninstalls OpenSSH
Variables:
- `win_workman_openssh_update_up_timeout` int (default `600`): update: seconds to wait for sshd and for the outcome of the upgrade once it has started
- `win_workman_openssh_manage_authorized_keys` bool (default `True`): Deploy authorized_keys from ansible_ssh_pub_key_path
- `win_workman_openssh_enable_pubkey_auth` bool (default `True`): Enable public key authentication
- `win_workman_openssh_disable_password_auth` bool (default `True`): Disable password-based SSH authentication
- `win_workman_openssh_manage_allow_users` bool (default `True`): Restrict SSH access to ansible_user (AllowUsers)
Notes: Requires OpenSSH Server to be already installed. Roll out update on one host first, then the lab: a host whose sshd does not come back needs console access. Replaces the secure_ssh role, which is kept as a deprecated alias: secure_ssh and secure_ssh-on run openssh-harden, secure_ssh-off runs openssh-unharden, and the win_workman_secure_ssh_* variables are still honoured as fallbacks.

### optimize: Disk Optimization

- `optimize-on`: Run disk optimization (TRIM for SSDs, defrag for HDDs) on target volumes
Variables:
- `win_workman_optimize_volumes` list (default `['C']`): Drive letters to optimize
- `win_workman_optimize_defrag` bool (default `False`): Force defragmentation even on SSDs (not recommended)
Notes: Only 'on' is implemented; there is no 'off'. Without win_workman_optimize_defrag Windows picks the operation by media type: retrim on SSDs, analysis and defragmentation on HDDs, which can take long.

### ping: Host Ping

- `ping-on`: Ping the target host and report reachability
Notes: Does not install software. Useful as a connectivity check before other tasks.

### ps_policy: PowerShell Execution Policy

- `ps_policy-set`: Apply an execution policy (default action). The policy can be passed as task argument, e.g. ps_policy-set-AllSigned
- `ps_policy-reset`: Remove the value this role writes, so Windows falls back to its default (Restricted on client editions)
- `ps_policy-on`: Alias for 'set' — applies win_workman_ps_policy
- `ps_policy-off`: Alias for 'reset'
- `ps_policy-info`: Report the machine-wide scopes and the resulting policy without changing them
Variables:
- `win_workman_ps_policy` str (default `RemoteSigned`): Policy applied when no argument is given: Restricted, AllSigned, RemoteSigned, Unrestricted or Bypass
- `win_workman_ps_policy_mode` str (default `local_machine`): local_machine writes the LocalMachine scope (64 and 32 bit), which users may override for themselves; machine_policy writes the "Turn on Script Execution" policy key, which wins over every scope but is overwritten by a domain GPO that sets it
Notes: Windows PowerShell 5.1 only; PowerShell 7 defaults to RemoteSigned on its own. Needed by tools that ship .ps1 shims (npm, npx) or activation scripts (venv Activate.ps1): on Windows client the default Restricted blocks them. The nodejs roles call ps_policy-on as a dependency. In local_machine mode, a GPO that sets the policy wins: set warns about it.

### restart: System Restart

- `restart-on`: Restart the host immediately
- `restart-if`: Restart only if the condition holds; the condition is required, and the only one supported is pending: restart-if-pending restarts when a reboot is pending (CBS, WUA, PendingFileRenameOperations, WinSxS). A bare restart-if fails validation
Notes: Does not install software. Use 'restart-if-pending' after updates or installs that require a reboot.

### scoobe: SCOOBE (finish setting up your device)

- `scoobe-info`: Report the SCOOBE settings of every user profile and the Default profile (default action)
- `scoobe-off`: Suppress the "Let's finish setting up your device" page shown at logon after updates, in every profile and in the Default profile
- `scoobe-on`: Remove the values written by 'off', giving Windows back its default behaviour
Variables:
- `win_workman_scoobe_profiles_include_default` bool (default `True`): Also write the Default profile, template for accounts created later
Notes: Per-user settings (UserProfileEngagement\ScoobeSystemSettingEnabled, ContentDeliveryManager\SubscribedContent-310093Enabled, the CloudContent user policy DisableWindowsSpotlightWindowsWelcomeExperience), written into every profile hive: loaded hives in place, the others loaded from NTUSER.DAT. No logoff or reboot; takes effect at the next logon. A profile whose hive is held by another process is reported as unavailable. Not the first-boot OOBE: that is the oobe role.

### secure_ssh: Secure SSH (deprecated, use openssh)

- `secure_ssh-on`: Deprecated: runs openssh-harden
- `secure_ssh-off`: Deprecated: runs openssh-unharden
Notes: Deprecated alias of the openssh role, to be removed in a later release. The win_workman_secure_ssh_* variables still work as fallbacks of the win_workman_openssh_* ones.

### sfc: System File Checker (sfc)

- `sfc-on`: Run sfc /scannow to scan and repair protected system files
Variables:
- `win_workman_restart` bool (default `True`): Restart the host first when Windows has a reboot pending, whoever is logged on; false skips the check
Notes: Does not install software. Consider running 'wim-repair' first for severe corruption. Fails when sfc cannot repair a file and when it did not scan at all, e.g. with a repair pending that needs a restart.

### shutdown: System Shutdown

- `shutdown-on`: Shut down the host (delay: win_workman_shutdown_timeout seconds, default 30) and wait until it goes offline, failing if it does not; set win_workman_shutdown_wait=false to return as soon as the command is sent
- `shutdown-no_wait`: Shut down the host as 'on' but return as soon as the command is sent, even with win_workman_shutdown_wait=true
- `shutdown-abort`: Abort a pending shutdown previously scheduled with 'on'
- `shutdown-a`: Alias for 'abort'
- `shutdown-wait`: Shut down the host and wait until it goes offline, even with win_workman_shutdown_wait=false
- `shutdown-if`: Shut down only if the condition holds; the condition is required, and the only one supported is nouser: shutdown-if-nouser shuts down when no user session is open in any state (a locked or disconnected session keeps the host on) and otherwise reports who is logged on. Waits for the shutdown as 'on' does. A bare shutdown-if fails validation
Notes: Does not install software. Override the delay with -e win_workman_shutdown_timeout=<seconds>. The wait watches the connection port from the controller; win_workman_shutdown_wait_timeout (default 900) is the margin after the delay, sized for hosts installing updates at shutdown.

### sysinfo: System Information

- `sysinfo-on`: Collect system information and print a per-host line plus an aggregated summary (default action). Optional args select sections, e.g. 'sysinfo-on-os-disk'
- `sysinfo-os`: Collect only the OS section (Windows edition, DisplayVersion, build, uptime)
- `sysinfo-security`: Collect only the security section: TPM state and provisioning, Secure Boot, firmware type and partition style. Not collected by default because it costs about a second per host
- `sysinfo-wu`: Collect only the Windows Update section: update policy, pause state, appraiser upgrade indicators and the setup compatibility report
- `sysinfo-full`: Collect and dump the whole information dictionary for each host
- `sysinfo-save`: Collect and write an aggregated JSON report to win_workman_sysinfo_dest on the controller
Variables:
- `win_workman_sysinfo_sections` list (default `['os', 'identity', 'hw', 'disk', 'net', 'wu']`): Sections collected when the task string carries no explicit section list. Available sections: os, identity, hw, disk, net, security, wu. "security" is opt-in: Get-Tpm and Get-Disk cost about a second per host, so ask for it explicitly, e.g. 'sysinfo-on-os-security'
- `win_workman_sysinfo_dest` str (default `/tmp/win_workman_sysinfo.json`): Controller-side path for the JSON report written by the 'save' action. Must be absolute: a relative path resolves against the collection playbook directory, not the project directory
Notes: Read-only: never changes state on the target. Collects everything in a single PowerShell round-trip and does not rely on gathered facts. Results are exposed as the win_workman_sysinfo fact, so other roles can branch on OS build or hardware. Sections can be narrowed per task, e.g. 'sysinfo-on-os' for a fast Windows version check across a lab, or 'sysinfo-on-os-security-wu' to see why a feature update is not being offered. The security section needs an elevated session for Get-Tpm and Confirm-SecureBootUEFI; without it the section degrades to an error entry instead of failing the run. Beware that the appraiser indicators and the compatibility report are stored values, not recomputed on read: after a BIOS change they keep reporting the old reason until the Microsoft Compatibility Appraiser task runs again.

### visual_effects: Visual Effects

- `visual_effects-set`: Apply a preset to every profile (default action). The preset can be passed as task argument, e.g. visual_effects-set-balanced. Presets: minimal (every effect off except font smoothing), balanced (animations, fades, shadows and Peek off; font smoothing, thumbnails, window contents while dragging, translucent selection and icon label shadows kept), full (best appearance), default (a fresh Windows 11 profile)
- `visual_effects-reset`: Restore the visual effects of a fresh Windows 11 profile (same as set-default)
- `visual_effects-on`: Alias for 'set' — applies win_workman_visual_effects_preset
- `visual_effects-off`: Alias for 'reset'
- `visual_effects-info`: Report the preset of every user profile (minimal, balanced, full, default, custom when changed by hand, unset when never customised) without changing it
Variables:
- `win_workman_visual_effects_preset` str (default `minimal`): Preset applied when no argument is given: minimal, balanced, full, default
- `win_workman_visual_effects_profiles_include_default` bool (default `True`): Apply to the default user profile (new user template)
Notes: Per-user setting written into each profile hive, so it applies at the next logon. Profiles of users currently logged in are skipped: set and reset force a logoff first. No reboot required. minimal is worth it on old hardware with integrated graphics and little RAM.

### wallpaper: Wallpaper Management

- `wallpaper-on`: Copy the wallpaper, apply it to every local profile and lock it on that file (set + lock). Forces a logoff of the interactive sessions first.
- `wallpaper-off`: Restore the Windows default wallpaper in every profile and remove the lock (reset + unlock). The deployed file is left in place. Forces a logoff first.
- `wallpaper-set`: Copy the wallpaper to the host and write it into every local profile, including the Default profile, without locking it. Clears the per-profile wallpaper cache. A profile that is already locked is locked again on the new file. Forces a logoff first.
- `wallpaper-reset`: Restore the Windows default wallpaper in every profile and clear the per-profile wallpaper cache. A profile that is already locked is locked again on the default wallpaper. Forces a logoff first.
- `wallpaper-lock`: Prevent users from changing the wallpaper, whatever it is now: each profile is locked on its current picture through the Desktop Wallpaper policy, and the Background settings are hidden. A picture inside the user's profile is copied to win_workman_wallpaper_lock_dir first; solid colour, slideshow, Spotlight or a missing file fall back to win_workman_wallpaper_default_path. A profile already locked keeps its locked picture. Needs no prior set. Forces a logoff first.
- `wallpaper-unlock`: Remove the wallpaper lock from every profile. Forces a logoff first.
- `wallpaper-clear_history`: Clear the recent wallpaper list of the Background settings in every profile. Forces a logoff first.
Variables:
- `win_workman_wallpaper_source` str (default `{{ role_path }}/files/default_wallpaper.png`): Image file on the controller to deploy as wallpaper (a file, not a directory)
- `win_workman_wallpaper_dir` str (default `C:\ProgramData\Wallpaper`): Destination directory on the remote host
- `win_workman_wallpaper_path` str (default `{{ win_workman_wallpaper_dir }}\wallpaper.png`): Full destination path on the remote host, written to the registry
- `win_workman_wallpaper_lock_dir` str (default `{{ win_workman_wallpaper_dir }}\locked`): Where lock copies a picture that lives inside a user profile, out of the user's reach
- `win_workman_wallpaper_set_style` str (default `10`): Wallpaper style: 0=center, 2=stretch, 6=fit, 10=fill, 22=span
- `win_workman_wallpaper_set_tile` str (default `0`): Tiling: 0=off, 1=on
- `win_workman_wallpaper_profiles_include_default` bool (default `True`): Apply wallpaper to the default user profile (new user template)
- `win_workman_wallpaper_default_path` str (default `{{ ansible_env.SystemRoot | default('C:\Windows') }}\Web\Wallpaper\Windows\img0.jpg`): Wallpaper restored by reset
- `win_workman_wallpaper_default_style` str (default `10`): Style restored by reset
- `win_workman_wallpaper_default_tile` str (default `0`): Tiling restored by reset

### widgets: Windows Widgets

- `widgets-on`: Enable Windows 11 Widgets panel
- `widgets-off`: Disable Windows 11 Widgets panel via policy
Notes: Does not install software; manages policy/registry only.

### wim: Windows Image (DISM)

- `wim-scan`: Scan the component store for corruption (DISM /ScanHealth) and report how much was detected
- `wim-check`: Check whether the component store is repairable (DISM /CheckHealth)
- `wim-repair`: Repair the component store (DISM /RestoreHealth), from Windows Update or from a local source
Variables:
- `win_workman_wim_check_fail_on_repairable` bool (default `True`): 'check' fails on a Repairable store. false reports the state without failing, so the tasks after it still run; NonRecoverable and errors fail anyway.
- `win_workman_wim_scan_fail_on_repairable` bool (default `True`): 'scan' fails on a Repairable store. false reports state and counts without failing, so the tasks after it still run; NonRecoverable and errors fail anyway.
- `win_workman_wim_repair_source` str: Local source for 'repair': an image and its index (wim:C:\Temp\install.wim:1, or esd:) or a folder with the components (a Windows directory or its WinSxS). Empty: Windows Update.
- `win_workman_wim_repair_limit_access` bool (default `True`): With a source, keep DISM from falling back on Windows Update (/LimitAccess). Ignored without a source.
Notes: Does not install software. Typical sequence: check → scan → repair. The source path is local to the host: no UNC paths. DISM repairs a component only from a copy in the very same version.

### win_iso: Windows installation ISO

- `win_iso-build`: Build an unattended installation ISO from a Microsoft ISO in win_workman_win_iso_root (default action): only the chosen editions, the local administrator of the target host, OpenSSH Server ready from the first boot. An argument picks how OpenSSH gets there: win_iso-build-msi (default), win_iso-build-dism, win_iso-build-none.
- `win_iso-info`: Without a source, list the ISOs in win_workman_win_iso_root; with one, list its editions and those build would keep. Changes nothing.
- `win_iso-on`: Alias for build
Variables:
- `win_workman_win_iso_source` str: The Microsoft ISO, relative to win_workman_win_iso_root or absolute. Required by build.
- `win_workman_win_iso_root` str (default `{{ win_workman_storage_path }}/win_iso`): Controller folder of the ISOs, source and output
- `win_workman_win_iso_output` str: Output ISO, relative to the root or absolute. Empty means <source>-unattended.iso.
- `win_workman_win_iso_work_dir` str: Absolute controller folder for the private build directory (about twice the ISO, password in clear, removed at the end). Empty means the folder of the output.
- `win_workman_win_iso_ssh` str (default `msi`): msi: the Win32-OpenSSH MSI installed during Setup, not updated by Windows Update. dism: the Windows capability added to the image by DISM on the target host, updated by Windows Update. none: no SSH. A task argument wins.
- `win_workman_win_iso_fod_source` str: ssh=dism: the Languages and Optional Features ISO of the servicing branch of the image (26100 for 24H2/25H2/26H2), relative to the root or absolute.
- `win_workman_win_iso_editions` list (default `['Core', 'Professional', 'Education', 'ProfessionalEducation']`): Editions kept, by edition ID, name or index of the source. Empty keeps all.
- `win_workman_win_iso_image` str: Edition installed without asking (index in the output, name or edition ID). Empty: Setup asks, or uses the edition of the key in the firmware.
- `win_workman_win_iso_wipe_disk` bool (default `False`): Erase disk 0 without asking. A PC booting from a forgotten stick then reinstalls itself.
- `win_workman_win_iso_product_key` str: Product key for PCs without one in the firmware
- `win_workman_win_iso_dism_dir` str (default `C:\win_iso`): ssh=dism, working folder on the target host, removed at the end
Notes: Runs on the controller; target exactly one host, which gives the credentials written into the ISO (ansible_user, ansible_password, so the ISO is per lab). With msi or none nothing connects to the host, which may be off. With dism the host must be a reachable Windows PC with about 40 GB free: install.wim goes there and back over SSH and DISM mounts each edition (several minutes each). Long: start it with background=true. Needs 7z, genisoimage and wimlib-imagex on the controller. The ISO holds the password in clear and is written mode 0600.

### wol: Wake-on-LAN

- `wol-on`: Send a Wake-on-LAN magic packet to the target host's MAC address
Variables:
- `win_workman_wol_packets` int (default `3`): Magic packets sent, one second apart
- `win_workman_wol_timeout` int (default `300`): Seconds to wait for the host to answer on ansible_port (default 22)
Notes: Requires MAC address in inventory. Use the dedicated 'wol' playbook for broadcast scenarios.

### wu: Windows Update

- `wu-run`: Install Windows updates. wu-run / wu-run-security: security, critical, rollups, Defender definitions. wu-run-full: all but feature updates. wu-run-upgrades: feature updates only. wu-run-cat-<a>+<b>: explicit categories (security, critical, rollups, definitions, updates, drivers, featurepacks, servicepacks, tools, upgrades, ...). wu-run-optional-<a>+<b>: the same categories among the updates offered as optional (preview cumulatives, optional feature updates and drivers), installed as SYSTEM through the Windows Update Agent. Then reports build before/after and each update's outcome (fact win_workman_wu_report); fails if an update fails to install
- `wu-scan`: Read-only: list what Windows Update offers, both the updates wu-run can install and the optional ones (fact win_workman_wu_scan with build, pending, optional)
- `wu-sync_ui`: Bring the Windows Update page of Settings in line with what is installed: an interactive Update Orchestrator scan in the logged-on user's session, then a wait for the new scan date. Fixes updates already installed by wu-run that Settings still offers ("Scarica e installa") or shows as failed. Skips hosts with nobody logged on. wu-run does it on its own after installing (win_workman_wu_sync_ui)
- `wu-reset`: By hand only, for a host whose Windows Update state is stuck (reboot asked for at every logon, history entries left in progress with 0x80242014, a "versione di ripristino" of an older release): stops the update services, renames SoftwareDistribution, catroot2 and the Update Orchestrator store (kept as .wu-reset-<stamp>, earlier copies deleted), clears RebootRequired, starts the services, then refreshes Settings and lists what is offered. Loses the download cache and the history in Settings. Refuses while updates are installing (TiWorker running)
- `wu-on`: Resume Windows Update (alias for resume)
- `wu-off`: Pause Windows Update for win_workman_wu_default_max_pause_days days (35), still bounded by FlightSettingsMaxPauseDays
- `wu-pause`: Pause Windows Update. Bare wu-pause uses win_workman_wu_pause_months plus win_workman_wu_pause_days; wu-pause-<n>[-d|-w|-m] gives the duration in days, weeks or calendar months (end date computed on the host, e.g. wu-pause-1-m on 10 Nov ends on 10 Dec). A pause longer than FlightSettingsMaxPauseDays (default 35) is shortened to it; raise it with max_pause_days first
- `wu-max_pause_days`: Read or set FlightSettingsMaxPauseDays: without args reports current value; with a duration (e.g. max_pause_days-35, max_pause_days-5-w, max_pause_days-6-m) sets the cap, in days (a month counts as 31). The cap only bounds wu-pause/wu-off of this role: on 25H2 and 26H2 the "Seleziona data" picker of Settings ignores it and stays at 35 days. The picker follows the SetMaxPauseDays policy instead, which accepts 1-35 and can only lower it. To pause beyond 35 days, raise the cap here, then wu-pause-<n>: Settings accepts and shows the longer pause
- `wu-resume`: Resume Windows Update (clear pause)
- `wu-is_paused`: Check if Windows Update is currently paused (sets win_workman_wu_is_paused fact)
- `wu-policy_standard`: Restore the default Windows Update policy: WaaSMedicSvc manual with default recovery, automatic updates on, no WSUS; removes AUOptions, NoAutoRebootWithLoggedOnUsers and ExcludeWUDriversInQualityUpdate
- `wu-policy_ansible_managed`: Removed; fails on purpose. Use pause/off, or policy_standard to restore the default policy
Variables:
- `win_workman_wu_pause_days` int (default `7`): Days of a bare 'pause', added to win_workman_wu_pause_months
- `win_workman_wu_pause_months` int (default `0`): Calendar months of a bare 'pause'
- `win_workman_wu_default_max_pause_days` int (default `35`): Maximum pause duration used by 'off' and as reset target for max_pause_days-0
- `win_workman_wu_default_profile` str (default `security`): Profile used by a bare wu-run
- `win_workman_wu_categories` list (default `[]`): Category aliases replacing the chosen profile's categories (a wu-run-cat-... selector still wins)
- `win_workman_restart` bool (default `True`): Allow restart after update installation if required
- `win_workman_wu_reboot_timeout` int (default `1800`): Seconds wu-run waits after each restart for the host to be back with servicing idle (a cumulative can take several Windows-driven reboots)
- `win_workman_wu_max_rounds` int (default `5`): Install rounds in one wu-run, each followed by a restart when needed
- `win_workman_wu_optional_timeout` int (default `7200`): Seconds wu-run-optional-... may take to download and install in one round
- `win_workman_wu_sync_ui` bool (default `True`): After a wu-run that installed something, refresh the Windows Update page of Settings (as wu-sync_ui); a failed refresh is reported, not fatal
- `win_workman_wu_sync_ui_timeout` int (default `300`): Seconds wu-sync_ui waits for the Update Orchestrator to record the new scan
- `win_workman_wu_unpause` bool (default `False`): Resume updates before 'run' (when updates are kept paused between runs)
Notes: Windows Update publishes some updates with DeploymentAction OptionalInstallation: the monthly non-security preview cumulative (Settings shows "Aggiornamento della versione di anteprima (KBxxxxxxx) è disponibile" with "Scarica e installa"), some feature updates (26H2 on 25H2 hosts) and optional drivers. No wu-run profile or wu-run-cat-... reaches them, because win_updates searches with the fixed query "IsInstalled = 0", which implies DeploymentAction='Installation': they do not even show among the found or filtered updates, and wu-run-upgrades reports 0 found. Use wu-scan to list them and wu-run-optional-<category>[+<category>...] to install them, e.g. wu-run-optional-upgrades for the feature update, wu-run-optional-updates for the preview. A category is required on purpose: optional drivers are in the same set. wu-run-optional-upgrades stops at the feature update; chain wu-run after it for the cumulative of the new release. Setting the TargetReleaseVersion policy does not help: on a 25H2 host it hid the 26H2 update from both searches.
