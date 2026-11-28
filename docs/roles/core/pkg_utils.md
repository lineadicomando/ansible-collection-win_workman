# pkg_utils — Package workflow and shared toolbox

Internal role, never dispatched to (the parser refuses `pkg_utils-…`). It implements
the standard package actions for every schema role (`tasks_from: pkg_workflow`) and
holds the task files other roles include with `tasks_from` instead of writing their
own PowerShell. The actions themselves are described in
[architecture](../../architecture.md#actions), the providers in
[architecture](../../architecture.md#providers).

```yaml
# roles/<role>/tasks/main.yaml of a package role
- name: Run package workflow
  ansible.builtin.include_role:
    name: lineadicomando.win_workman.pkg_utils
    tasks_from: pkg_workflow
  vars:
    win_workman_schema: "{{ win_workman_<role>_schema }}"
```

`pkg_workflow` fails on an action outside `win_workman_pkg_actions` (`vars/main.yaml`:
`on`, `off`, `info`, `download`, `copy`, `shortcuts`, `is_present`, `usr`), on `usr-*`
for a schema without a `usr` block, and on any action but `usr`/`download` for a
schema with only a `usr` block; then it includes `pkg_act_<action>`.

## Package schema

`win_workman_<role>_schema` in `roles/<role>/vars/main.yaml`. Every field but `name`,
`role` and `default_action` is optional.

| Field | Meaning |
|---|---|
| `name` | display name; the default portable directory when none is given |
| `role` | FQCN of the role: hooks are included from it, its last segment names the `usr` policy |
| `default_action` | action of a bare task string (`!!str on`) |
| `package.setup_file` | installer under `win_workman_remote_tmp` (`package.filename` is a fallback); also what `copy`/cleanup handle when `files` is empty |
| `package.setup_dir` | subdirectory of `win_workman_remote_tmp` holding `setup_file` (an extracted archive); removed after the install |
| `package.searchName` | `-like` glob on `DisplayName` in the Uninstall keys (HKLM, WOW6432Node, HKCU of the connecting user); a string |
| `package.version` | target `DisplayVersion`; omitted means `latest`: `on` reinstalls at every run (Chrome-style MSIs) |
| `package.version_like` | `-like` glob on `DisplayVersion`, default `*`: see below |
| `package.exclusive` | remove the other versions of `searchName` before installing: see below |
| `package.version_file` | executable whose file version, against the MSI's `ProductVersion`, skips the install: see below |
| `package.provider` | `registry` (default) or `portable`; for registry packages it is also passed to `win_package` (absent: `auto`) |
| `package.install_args`, `uninstall_args` | list or string, `win_package` `arguments` |
| `package.expected_return_code` | `win_package` return codes accepted on install |
| `package.product_id` | uninstall by this id instead of the detected one (`detect`: use detection) |
| `package.uninstall_via_helper` | `true`: run the detected `UninstallString` (+ `uninstall_args`) with `Start-Process -Wait` instead of `win_package`; exit codes in `uninstall_valid_rc` (default `[0]`) |
| `package.uninstall_before_upgrade` | uninstall the old version before `on` upgrades, and allow a downgrade; with a portable file without checksum, reinstall at every run |
| `package.cleanup_registry_key` | after uninstall, delete the Uninstall key the uninstaller left behind |
| `package.cleanup_paths` | paths removed after a successful uninstall |
| `package.portable_dir`, `portable_dirs` | install directories under `win_workman_portable_path`; derived otherwise from the `dest_dir` of the files, then from `name` |
| `package.path_dirs` | directories under **`win_workman_portable_path`** added to the machine `PATH` by `on`, removed by `off` |
| `package.bundle_parts`, `bundle_parts_last`, `bundle_cleanup_keys`, `bundle_cache_version_like` | Burn bundle registered per user: see below |
| `package.before_install_ps_script`, `after_install_ps_script`, `before_uninstall_ps_script`, `after_uninstall_ps_script`, `after_copy_ps_script` | inline PowerShell run at that point (install/uninstall ones only when there is something to do) |
| `files[]` | `filename`, `url`, `checksum` (`sha256:…`; without it `download` prints the sha256), `validate_certs`, `extract: 7z` (extracted with 7-Zip into `dest_dir`), `dest_dir` |
| `shortcuts[]` | `description`, `src`, `dest`, `icon`, `directory`, `arguments`: `icon` and `directory` are required by the task; created by `on` and `shortcuts`, removed by `off` |
| `services[]` | `name`, `start_mode`, `state`: stopped before install so locked files get replaced, set to the declared state after `on` |
| `usr` | per-user deferred install: [below](#per-user-deferred-install-usr) |

Hooks: a role whose `defaults/` sets `win_workman_schema_hooks: {before_install: true,
…}` (keys `before_install`, `after_install`, `before_uninstall`, `after_uninstall`) gets
`roles/<role>/tasks/<hook>.yaml` included at that point (`include_tasks.yaml`), only when
there is something to install or uninstall. Only `gcpw` uses them.

`on` classifies the operation as `install`, `upgrade`, `downgrade` or `noop` from the
detected and the target version; a downgrade happens only with
`uninstall_before_upgrade`. Before `win_package` it waits for Windows Installer
(`wait_installer`) and retries return codes in `win_workman_installer_retry_codes`.

### Programs that update themselves (`version_file`)

Browsers such as Chrome install the vendor's current MSI with no `version` pinned
while their own updater moves them forward, at times leaving no uninstall entry. Then
detection finds nothing and the MSI refuses to downgrade (Chrome: rc 1603, "a newer
version is already installed"). With `version_file` (environment variables expanded),
`on` compares, after copying the installer, the executable's file version with the
MSI's `ProductVersion`: same or newer skips the install, removes the installer and
reports `ok`. Only `.msi` installers are checked; a missing executable installs as
usual. A program found only this way still has no uninstall entry, so `off` cannot
remove it (the skip message says so).

### One role per major line (`version_like`, `exclusive`)

Some vendors ship every release with the same unversioned `DisplayName` and MSI
`UpgradeCode` (every Node.js MSI is "Node.js"), so two major lines never coexist and a
role per line (`nodejs26`, `nodejs27`) needs:

- `version_like` (`"26.*"`): `info`, `is_present`, `on` and `off` see only matching
  entries, so `nodejs26-off` leaves a Node.js 27 alone.
- `exclusive: true`: `on` first uninstalls every machine-wide entry with the same
  `searchName` and a version outside `version_like` (`pkg_exclusive.yaml`), since the
  MSI refuses to go back to an older major and replaces a newer one only when
  upgrading. Skipped without `version_like` (every version would be "other").

`<role>-on` then means "this major line is on the host", in either direction; two such
roles in one run replace each other at every run.

### Burn bundles registered per user (`bundle_parts`)

A WiX Burn bundle can install its MSIs machine-wide but register the bundle only in
HKCU of the account that ran it: python.org's does, even with `InstallAllUsers=1`
(log: *bundle scope: PerUser, package scope: PerMachine*). Detecting the bundle entry
works only for that account: for anyone else `info` says absent, `on` reinstalls at
every run, `off` finds nothing. Such a schema detects one MSI through `searchName`
(Python: `Python 3.14.* Core Interpreter (64-bit)`) and sets `bundle_parts` to a
`DisplayName` glob matching every part and the bundle (`Python 3.14.* (64-bit)`). `off`
(`bundle_parts_off.yaml`) then:

1. removes with `msiexec /x` every other machine-wide MSI entry matching the glob (and
   `version_like`); the parts matching `bundle_parts_last` (string or list) go after
   the others, in list order;
2. uninstalls the detected MSI, last;
3. removes what Burn would have removed with the bundle: the connecting account's
   bundle registration when it matches the glob (uninstall key, the Package Cache copy
   in `BundleCachePath`, the dependency provider key), the
   `ProgramData\Package Cache\{ProductCode}v<version>` copy of every MSI removed, the
   keys in `bundle_cleanup_keys` with their empty parents (Python writes
   `HKLM:\SOFTWARE\Python\PythonCore\3.x\InstalledFeatures` itself);
4. with `bundle_cache_version_like` (`"3.14.*"`), removes every
   `{ProductCode}v<version>` cache directory whose version matches and whose product is
   gone: an upgrade run by an account that does not own the old registration leaves
   them, since Burn drops them only when upgrading its own related bundle.

The order matters: Python's MSIs find their directory in AppSearch through the
`python.exe` component of the *Executables* MSI, with two `DrLocator` rows naming each
other as parent; once that component is gone the search loops and msiexec dies with a
stack overflow (`0xc00000fd`, rc 1603), leaving the part installed. The Python roles
therefore set `bundle_parts_last` to the Executables MSI (Core Interpreter and
Executables have no AppSearch of their own). Registrations in other profiles are left:
they point at packages already gone.

### Uninstall cleanup

After the uninstall, `off` removes in order: the Uninstall key (`cleanup_registry_key`;
detection then runs again, so the next steps judge the state after it),
`cleanup_paths` (only once the package is no longer detected), then the install
directory (`InstallLocation`, or the uninstaller's folder) when every file left in it,
at any depth, matches `unins*`. Inno Setup cannot delete the `unins000.exe` it runs
from, so every Inno package (`vscode`, `git`, `gimp`, `netbeans`, `winmerge`, `peazip`,
`laragon`) leaves that directory; Laragon keeps its uninstaller in `bin\laragon`, hence
"at any depth". A directory holding anything else is reported and kept; drive roots and
shared system directories are refused. `win_workman_cleanup_uninstaller_dir: false`
keeps the leftovers; a package whose non-empty directory must go uses `cleanup_paths`.

## Toolbox (`tasks_from`)

Files meant for roles to include. Inputs go in `vars:` of the `include_role`; the
`pkg_act_*`, `pkg_usr_*`, `pkg_workflow`, `pkg_exclusive`, `bundle_parts_off`,
`info`, `win_extract` and `include_tasks` files are the workflow's own.

| tasks_from | Does | Inputs → output |
|---|---|---|
| `profiles` | list local user profiles (SID `S-1-5-21-*`, non-special) | `win_workman_profiles_include` / `_exclude` (name or `DOMAIN\name` globs), `_single`, `_include_default` → `win_workman_profiles` |
| `logoff` | log off every user session (any WTS state, not session 0 or system accounts) and wait for them to end; fails on timeout | `win_workman_logoff_timeout_seconds` |
| `user_sessions` | list user sessions (any state); fails rather than return a partial list | → `win_workman_user_sessions` (`SessionId`, `UserName`, `State`) |
| `restart` | `win_reboot`, back when sshd runs, uptime ≥ 60 s and TrustedInstaller/TiWorker idle for 20 s | `win_workman_restart_timeout` |
| `pending_restart` | reboot (through `restart`) only when CBS `RebootPending`, WU `RebootRequired`, `PendingFileRenameOperations` or `WinSxS\pending.xml` is set, logging why and the first 20 file operations | → `win_workman_pending_restart` |
| `kill` | stop processes by name | `win_workman_kill_process_name` or `_image_name` (string or list), `_user_name`, `_force` (default `true`) |
| `services_stop` | stop the services of `win_workman_schema.services` that exist | `win_workman_schema` |
| `detect_sw` | find an installed program in the Uninstall keys (HKLM, WOW6432Node, HKCU), optionally AppX; best match by version, then MSI over registry, machine over user | `win_workman_detect_sw_args: {name_like (string or list), version_like, version_not_like, search_appx}` → `win_workman_detect_sw.result` (`installed`, `id`, `provider`, `display_name`, `display_version`, `install_location`, `uninstall_string`, `scope`, `registry_key`, `match_count`, `results` when > 1) |
| `registry_read` | read one registry value (accepts `HKLM\…` and `HKLM:\…` forms) | `win_workman_winreg_path`, `win_workman_winreg_name` → `win_workman_registry_read.result` (`exists`, `value`, `kind`) |
| `se_read` | read the holders of a user right through `secedit /export` (fails if the export fails) | `win_workman_se_read_right` → `win_workman_se_read.result` |
| `detect_lang` | set `win_workman_default_lang` from the host locale | `win_workman_detect_lang_allowed` (required), `_map` (BCP47 → code); match order: map, `it-IT`→`it_IT`, `it`; unchanged when nothing matches |
| `download` | fetch `win_workman_schema.files` to `win_workman_storage_path` on the controller, run once, 3 retries | `win_workman_schema` |
| `win_copy` | copy the files (or `setup_file`) to `win_workman_remote_tmp` (portable: `win_workman_portable_path`, honouring `dest_dir`), extract `extract: 7z` entries, run `after_copy_ps_script` | `win_workman_schema` |
| `win_clean_temp` | delete the copied files and `setup_dir` from `win_workman_remote_tmp`; a locked file is reported, not failed | `win_workman_schema` |
| `7zip` | stage `7zr.exe` and 7-Zip Extra on the host and run `a`, `e` or `x` | `win_workman_7zip_command`, `_archive_path`, `_source_path` → `win_workman_7zip` |
| `win_path` | add or remove `portable_path\<dir>` for each `package.path_dirs` in the machine `PATH` | `win_workman_schema`, `win_workman_schema_win_path_state` |
| `shortcuts` | create or remove `win_workman_schema.shortcuts` | `win_workman_schema`, `win_workman_schema_shortcuts_state` |
| `shortcut_cleaner` | delete `.lnk` files in a folder whose target matches a regex and arguments a glob | `win_workman_shortcut_cleaner_path`, `_target_regex`, `_arguments_like` |
| `start_process` | run an executable, check its exit code | `win_workman_exec_path`, `_args` (string or list), `_success_exit_codes` (default `[0]`), `_wait_tree` (default `true`: waits on the job object), `_timeout` → `win_workman_start_process_response` |
| `run_as_system` | run an executable as SYSTEM through a temporary scheduled task, removed afterwards | `win_workman_system_task_exe`, `_name`, `_args`, `_timeout` (180) → `win_workman_run_as_system_result` |
| `wait_installer` | wait until no MSI holds `Global\_MSIExecute`; warns and goes on at timeout | `win_workman_installer_wait_timeout` |
| `remote_tmp` | give the remote temporary directories the ACL below | `win_workman_remote_tmp`, `ansible_remote_tmp` |

`start_process` has no caller in the collection today. With `_wait_tree: true`,
`Start-Process -Wait` waits for every descendant, which bootstrapper installers need
and which hangs on a stray helper (Autodesk uninstallers leave their analytics client):
see `CLAUDE.md`.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_storage_path` | `$HOME/win_workman_storage` | controller-side installer storage |
| `win_workman_remote_tmp` | `C:\Windows\Temp\ansible` | staging directory on the host |
| `win_workman_portable_path` | `C:\PortableApps` | root of portable packages and of `path_dirs` |
| `win_workman_portable_marker_name` | `.win_workman_source` | marker of a portable install ([providers](../../architecture.md#providers)) |
| `win_workman_default_lang` | `en_US` | locale hint of multi-locale roles; `detect_lang` overwrites it |
| `win_workman_restart` | `true` | roles may reboot (read by `wu` and `sfc`; `restart.yaml` does not check it) |
| `win_workman_restart_timeout` | `600` | seconds `restart` waits for the host |
| `win_workman_logoff_timeout_seconds` | `300` | seconds `logoff` waits for the sessions to end |
| `win_workman_installer_wait_timeout` | `120` | seconds `wait_installer` waits; TiWorker is not waited for |
| `win_workman_installer_retry_codes` | `[1601, 1618]` | `win_package` codes meaning "installer busy" |
| `win_workman_installer_retries` / `_retry_delay` | `5` / `60` | retries and seconds between them |
| `win_workman_cleanup_uninstaller_dir` | `true` | remove the install directory left with only `unins*` files |
| `win_workman_usr_path`, `_usr_targets`, `_usr_timeout`, `_usr_apply_timeout` | | [per-user install](#variables-of-usr) |

## Remote temporary directory

`win_workman_remote_tmp` stages installers, archives and scripts, and in the lab
inventories it is also `ansible_remote_tmp`. When missing, Ansible creates it readable
by the connecting user alone (owner `ansible_user`, inheritance off), and whatever does
not run as that user then fails there: `become_user: SYSTEM` (the optional updates of
`wu`: `CompileAssemblyFromSource ... path not found`), a SYSTEM scheduled task
(`run_as_system`), the Windows Installer service reading a staged file
(`openssh-update`), another `ansible_user` later.

`remote_tmp.yaml` sets on it, and on `ansible_remote_tmp` when that is another absolute
path: SYSTEM and Administrators full control, inherited, no inheritance from
`C:\Windows\Temp`, nothing else. Users get nothing: installers run as SYSTEM from there,
so a user able to replace one would run code as SYSTEM. The `ansible-moduletmp-*`
directories keep their own ACL, private to the connecting user. The dispatcher runs it
once per run before the first task that connects to the host (a leading `wol` does not
trigger it, so `wol,chrome` works on a powered-off PC); it reports a change only when
the ACL differed. `win_iso` creates the directory with this ACL during Setup. Roles
included without the dispatcher can include `tasks_from: remote_tmp` themselves.

## Per-user deferred install (`usr`)

Some software ships only a per-user installer: run by Ansible it lands in the Ansible
user's profile (`%LOCALAPPDATA%\Programs`, HKCU uninstall key), even elevated. The `usr`
action defers the install to each target user's logon. A schema may carry both a
`package` (machine-wide, now) and a `usr` block; `get_role_info` reports them as
`install_scopes`.

```
<schema>-usr-<verb>[-<target>[+<target>…]]
```

| Verb | Effect |
|---|---|
| `on` *(default)* | download, stage the installer, mark the targets `present` |
| `off` | mark the targets `absent`; without targets, every target of the policy |
| `info` | policy, and per profile (or given target) installed version and last agent outcome |
| `apply` | run the agent now in every interactive session and wait for it |
| `purge` | remove the policy and the staged installer (installed copies stay); no targets; the last purge also removes task, agent and tree |

Targets are account or group names, `DOMAIN\name` or SIDs, joined by `+`; everything
after the verb is rejoined on `-` first, so `zed-usr-on-student-alice+student-bob`
works (`+` cannot occur in an account name, `,` separates tasks in `todo`). Without
targets `on` uses `win_workman_usr_targets`. `on` and `off` merge into the policy:
`zed-usr-on` then `zed-usr-off-student-bob` means every member of `BUILTIN\Users` except
student-bob, who uninstalls at next logon.

```
C:\ProgramData\win_workman\usr\
├── agent.ps1                     # one agent for every policy
├── policies\<schema>.json        # version, args, sha256, targets by SID and state
└── payload\<schema>\<version>\   # staged installer
```

- **Logon task** `\win_workman\usr-agent`: principal `BUILTIN\Users`, trigger at any
  logon, runs the agent via `conhost.exe --headless` in the user's session, not
  elevated, no stored password. `usr-apply` starts it on demand.
- **Agent**: for each policy that applies, reads the HKCU uninstall key `uninstall_key`,
  then installs (missing or older), does nothing (same or newer: never downgrades,
  since Zed and the like update themselves) or uninstalls (`absent`, waiting for the
  key to go, since Inno and NSIS uninstallers return early). It checks the sha256
  first and records `State`, `Result`, `Changed`, `Version`, `Message`, `Timestamp`
  under `HKCU\Software\win_workman\usr\<schema>`, log in
  `%LOCALAPPDATA%\win_workman\usr-agent.log`.
- **Rules**: targets are resolved to SIDs on the host when the policy is written and
  matched against the user's token; a user entry beats group entries, among groups
  `absent` wins, an unmatched user is left alone. Each entry records its `kind`
  (`user`, `group`, `computer`, `unknown`): check it, a typo can resolve to a group (on
  an Italian Windows `nessuno` is the local group *None*). An unresolvable name fails.
- **ACL**: Users get read and execute only; write access for one user would mean
  running code as all the others.

Why a logon task (measured on Windows 11 25H2): an `S4U` task for another user cannot
be registered (*Access denied* from the Ansible session, from SYSTEM, with the batch
logon right, with the target in Administrators); a `Password` principal works but needs
every password and *Log on as a batch job*, which standard users lack; a group
principal at logon needs neither and covers users created later and domain users who
never logged on. The cost: `usr-on` installs nothing by itself, `usr-info` tells who has
what.

```yaml
win_workman_zed_schema:
  name: Zed
  role: lineadicomando.win_workman.zed      # last segment names the policy
  default_action: usr
  usr:
    setup_file: Zed-x86_64-<version>.exe     # needs a files entry with a sha256
    version: "<version>"
    uninstall_key: "{2DB0DA96-CA55-49BB-AF4F-64AF36A86712}_is1"   # under HKCU\…\Uninstall
    install_args: [/VERYSILENT, /SUPPRESSMSGBOXES, /NORESTART]
    uninstall_args: [/VERYSILENT, /SUPPRESSMSGBOXES, /NORESTART]
    success_exit_codes: [0]                  # optional
    timeout: 900                             # optional, seconds
  files:
    - filename: Zed-x86_64-<version>.exe
      url: https://…
      checksum: sha256:…
```

Bumping `version` and running `usr-on` again stages the new installer, removes the old
one, and upgrades each user at the next logon.

### Variables of usr

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_usr_targets` | `[BUILTIN\Users]` | targets of a bare `usr-on` (validated like inline ones) |
| `win_workman_usr_path` | `C:\ProgramData\win_workman\usr` | root of agent, policies, payloads |
| `win_workman_usr_timeout` | `900` | seconds the agent allows an installer or uninstaller |
| `win_workman_usr_apply_timeout` | `900` | seconds `usr-apply` waits in every session |
