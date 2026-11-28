# Code defects found by the documentation audit

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

**Status:** found 2026-11-28 by reading the code while every role page was checked
against its role; none reproduced on a host yet. The role pages already describe the
current behaviour. Fix one, test it, delete its line.

## P2: wrong result with no error

- **`start_process`: `win_workman_exec_wait_tree: false` has no effect.**
  `roles/pkg_utils/tasks/start_process.yaml:93` uses `default(true, true)`, which also
  replaces `false`. Use `default(true)`. No caller sets it today.
- **`wu-run` reports the pause state after the run as "before".**
  `roles/wu/tasks/act_run.yaml:80`: the second `build_info` overwrites the first, read by
  `run_report.yaml:63-66`.
- **`display_scale-set-100` may not give 100 %.** `roles/display_scale/vars/main.yaml:57`
  writes `Win8DpiScaling=0`, which means "recommended": on a panel recommending more
  than 100 % the scale stays above it.
- **`vcredist14-off` can remove the 2012/2013 runtimes.** Its `searchName` also matches
  the 2012 and 2013 x64 entries; on a host without v14 they are what `off` finds.
- **`firefox`: the detected language overrides `win_workman_default_lang` from the
  inventory** (`roles/firefox/tasks/main.yaml:2`, `detect_lang`); only a task token or
  `-e` forces it.
- **`autocadlt2026-off` pins the language for the rest of the play**
  (`tasks/act_off.yaml:13`, `set_fact`): a later `autocadlt2026-on-<lang>` in the same
  run ignores its argument.
- **`seb-config_key` probably prints a wrong key.** `plugins/modules/seb_config.py:165`
  hashes the gzipped file; SEB derives the Config Key from the settings. Check against
  SEB's source before relying on it.

## P3: upgrades that never happen, small faults

- **Files with no version and no checksum** never refresh the copy in storage
  (`get_url` skips an existing file), so `on` installs the old build again or never
  upgrades: `ntop` (filename `NTop.exe`), `nircmd`, `googledrive`, `winrar`; `brave` and
  `chrome` re-run their installer at every `on`.
- **`laragon`: `searchName` contains the version** (`vars/main.yaml:18`): an older
  Laragon reads as absent and `off` leaves it.
- **`seb` kills a process named `seb`** (`vars/main.yaml:233`); the program is
  `SafeExamBrowser.exe`.
- **`edge-on-32bit` on 64-bit Windows**: shortcuts and `version_file` point to
  `%ProgramFiles%`, not `(x86)` (`vars/main.yaml:424`).
- **`wol` waits on port 22 unless `ansible_port` is set** (`tasks/act_on.yaml:22`),
  ignoring WinRM; `shutdown` gets it right.
- **`pkg_utils/info.yaml`** passes a provider detected as `appx` to `win_package`,
  which does not accept it.
- **`pkg_utils/shortcuts.yaml:7,9`**: `icon` and `directory` have no default, so an
  entry without them fails.
- **`googledrive`**: `defaults/maint.yaml` is never loaded (typo for `main.yaml`;
  harmless only because the templates use `default(true)`); `off` leaves the
  `AutoStartOnLogin` value.
- **`sketchup2026`**: the `vcredist14` dependency guard lacks the `nodep` test
  (`tasks/main.yaml:19`).
- **`winfsp` installs the VirtIO guest tools** as a dependency, also on a physical PC.
- **Stale text**: `python310` warns that its end of life (2026-10-31) "is imminent";
  `python313` has no warning though 3.13 gets no more Windows installers; header of
  `roles/ntop/vars/main.yaml` says "Postman"; `user_sessions.yaml:3` comment "Unlike
  logoff" is no longer true; `roles/winrar/meta/main.yaml` has a different licence and
  author from every other role.
