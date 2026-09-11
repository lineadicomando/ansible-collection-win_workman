# TODO

Planned improvements for the `lineadicomando.win_workman` collection.

Reviewed 2026-09-11: every entry below was checked against the current tree, and
the notes say what has changed since each was written.

---

## Package workflow

### Opt-in clean install directory (`clean_install_dir`)

**Status:** proposed — still unimplemented, verified 2026-09-11

Add an optional `clean_install_dir: true` field to the package schema. When set,
`pkg_utils` removes the leftover installation directory after the preliminary
uninstall of an upgrade and before the new installer runs, so that the package
is always laid down on a clean directory.

**Why:** silent installers (NSIS in particular) skip files that are locked by
running processes and exit with a success code. The result is an installation
that mixes binaries of two versions while the registry reports the new version,
so both `win_package` and the schema `info` action report success. Veyon 4.10.0
to 4.11.2 on the `ario_info` lab (2026-09-10) left 48 stale DLLs on 8 of 30
hosts: the service was gone and every binary failed with `0xC0000139`
(`STATUS_ENTRYPOINT_NOT_FOUND`).

Stopping the declared services before installing (implemented, `pkg_act_on`
calls `services_stop`) prevents the common case, but a clean directory is the
only way to also drop files that the new version no longer ships.

**Design notes:**

- Opt-in per schema, never a global default: removing an install directory is
  destructive and only safe for packages that keep no state there.
- Derive the directory from the detected `install_location` when available, with
  an explicit schema override for packages that do not register one.
- Skip the removal when the preliminary uninstall did not run or still reports
  the package as present.
- Overlaps with the existing `cleanup_paths` field, which several roles already
  use for the same purpose. Decide whether `clean_install_dir` should be its own
  field or whether `cleanup_paths` should simply be documented as the supported
  way to do this. **This decision is still open and blocks the rest.**

### Kill declared processes before install

**Status:** proposed — still unimplemented, verified 2026-09-11

`pkg_utils` can now stop the services listed under `services:` in the schema,
but user-facing processes still lock their own files. On the teacher station of
the `ario_info` lab the Veyon Master GUI was running during the upgrade, which
is how the stale DLLs got there.

A `kill_processes:` schema field handled by `pkg_utils` would cover this, reusing
the existing `tasks/kill.yaml` implementation. Roles such as chrome, firefox,
edge and libreoffice already call it from their own task files, so the logic is
in place and only needs a declarative entry point in the install workflow.

**Correction (2026-09-11):** "the logic is in place" was too optimistic.
`kill.yaml` parsed its JSON name lists through a pipeline, which does not unroll
a `ConvertFrom-Json` array, so a list of more than one name silently collapsed
into a single bogus entry and killed nothing. Fixed in `0f0ae61`. Anyone
implementing `kill_processes:` before that commit would have shipped a field
that works with exactly one process name.

### Validate the shared uninstall path across roles

**Status:** follow-up to a change already merged — still unverified

The preliminary uninstall of an upgrade now goes through `pkg_act_off` instead
of calling `win_package` directly, so `uninstall_via_helper`, the
`before_uninstall` / `after_uninstall` hooks, `cleanup_registry_key` and
`cleanup_paths` finally apply to upgrades as they already did to explicit
`<role>-off` runs.

Thirteen roles declare `cleanup_paths` or `cleanup_registry_key` (brave, chrome,
embarcadero_devcpp, foxit_pdf_reader, opera, p7zip, vivaldi, winrar and
python310 through python314 — list re-checked 2026-09-11, still exact). Their
upgrade path now performs cleanup steps it previously skipped. Verify each of
them against a test VM before relying on the new behaviour in production.

### Wait mode for the helper uninstall in `pkg_act_off`

**Status:** proposed — deliberately left out of `0f0ae61`

`Start-Process -Wait` does not simply `WaitForExit()` on the process it
launched: it waits for the whole job object, every descendant included. That is
what makes bootstrapper-style installers work, where the parent hands off to a
child and exits at once, and it is also what hangs forever when a program leaves
a stray helper running.

`tasks/start_process.yaml` now exposes the choice: `win_workman_exec_wait_tree`
defaults to `true` (the job-object wait, unchanged behaviour) and can be set to
`false` to wait on the launched process alone, with an optional
`win_workman_exec_timeout`. The same option is **not** available for the helper
uninstall inside `pkg_act_off`, which still hardcodes `-Wait`.

Adding it there means touching the seven roles that declare
`uninstall_via_helper: true` — firefox, vivaldi, veyon, vlc, filezilla,
puredata, winrar. For those the job-object wait is load-bearing, not accidental:
NSIS uninstallers copy themselves to `%TEMP%` and the launched process exits
immediately. Switching them to a process-only wait would report a barely started
uninstall as finished, and nothing downstream fails if the product is still
there — `pkg_act_off` re-detects afterwards only to feed the registry cleanup.

So: add the option with `true` as the default, then enable it per role only
where a hang is actually observed. Do not flip the default.

### `pkg_act_on` reads from `ansible_remote_tmp`

**Status:** proposed — one line, `tasks/pkg_act_on.yaml:408`

`win_copy` puts the installer in `win_workman_remote_tmp` (the collection's own
default, `C:\Windows\Temp\ansible`), but `pkg_act_on:408` reads it back from
`ansible_remote_tmp`, an Ansible connection variable. The two coincide only
because every `win_edulab` inventory happens to set
`ansible_remote_tmp: C:\Windows\Temp\ansible` in `group_vars/windows11/vars.yaml`.

Drop that dependency: a consumer of the collection who does not set the variable
gets either the wrong path or an undefined-variable error. The same coupling was
removed from `autocadlt2026` in `fac39f0`.

---

## AutoCAD roles

### Promote `odis_uninstall` and `find_products` to `pkg_utils`

**Status:** proposed

`roles/autocadlt2023/tasks/` and `roles/autocadlt2026/tasks/` carry byte-identical
copies of `odis_uninstall.yaml` (run an ODIS uninstall waiting on the launched
process alone) and `find_products.yaml` (resolve uninstall-hive entries by
display-name pattern, because Autodesk component GUIDs change with every
release). They were duplicated on purpose, to keep the fix out of the shared
code path while it was unproven.

`find_products.yaml` in particular is not Autodesk-specific and would serve any
role that needs to uninstall something whose GUID is not stable. Once both have
run against real hosts a few times, move them into `pkg_utils` and have the two
roles include them from there.

### End-to-end validation on a real host

**Status:** blocking before lab-wide use

- `autocadlt2026-on` has never been run end to end since `fac39f0` rewrote its
  presence detection. The install path — 2.7 GB per host, the `db-bootstrap`
  polling, the licence registration through `AdskLicensingInstHelper` — is
  unverified.
- `autocadlt2023-off` was validated on PC05 of `ario_info` (2026-09-11); the
  `off-full` variant was not. PC05 is the natural candidate: it still carries
  exactly the leftovers that `off-full` targets (the two Material Library 2023
  packages, the emptied install directory, the ACDLT2023 licensing logs).
- `autocadlt2026-off-full` has never been run since the GUIDs became
  runtime-resolved in `93a26d7`.

---

## Documentation

### Audit the catalog drafts

**Status:** proposed

39 of the 53 files in `docs/roles/catalog/` still open with
`> **Work in progress** — preliminary draft.` The banner says nothing about
whether the content is right, and both cases exist:

- `sketchup2026.md` is accurate and current, `license` and `unlicense` included
   — the banner is simply stale.
- `autocadlt2026_en.md` and `autocadlt2026_it.md` documented two roles that had
  never existed under those names, with the wrong provider and the wrong
  installer filename. Deleted and replaced in `fac39f0`.

A wrong draft is worse than no page, because it reads as documentation. Go
through them against the roles, fix what is wrong, and drop the banner from the
ones that earn it.

### Roles with no documentation at all

**Status:** proposed

Four roles have no page in `docs/roles/`: `googledrive`, `tinycad`, `winmerge`,
`winrar`. (`chkdsk`, `logoff`, `ms_account`, `oobe`, `ping`, `secure_ssh`,
`sfc`, `shutdown`, `widgets`, `wim` and `wol` are covered collectively by
`docs/roles/management/system-tools.md`, which is correct and needs nothing.)
