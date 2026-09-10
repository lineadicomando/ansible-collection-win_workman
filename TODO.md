# TODO

Planned improvements for the `lineadicomando.win_workman` collection.

## Opt-in clean install directory (`clean_install_dir`)

**Status:** proposed

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

Stopping the declared services before installing (implemented) prevents the
common case, but a clean directory is the only way to also drop files that the
new version no longer ships.

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
  way to do this.

## Kill declared processes before install

**Status:** proposed

`pkg_utils` can now stop the services listed under `services:` in the schema,
but user-facing processes still lock their own files. On the teacher station of
the `ario_info` lab the Veyon Master GUI was running during the upgrade, which
is how the stale DLLs got there.

A `kill_processes:` schema field handled by `pkg_utils` would cover this, reusing
the existing `tasks/kill.yaml` implementation. Roles such as chrome, firefox,
edge and libreoffice already call it from their own task files, so the logic is
in place and only needs a declarative entry point in the install workflow.

## Validate the shared uninstall path across roles

**Status:** follow-up to a change already merged

The preliminary uninstall of an upgrade now goes through `pkg_act_off` instead
of calling `win_package` directly, so `uninstall_via_helper`, the
`before_uninstall` / `after_uninstall` hooks, `cleanup_registry_key` and
`cleanup_paths` finally apply to upgrades as they already did to explicit
`<role>-off` runs.

Thirteen roles declare `cleanup_paths` or `cleanup_registry_key`
(foxit_pdf_reader, opera, brave, chrome, vivaldi, p7zip, winrar,
embarcadero_devcpp and python310 through python314). Their upgrade path now
performs cleanup steps it previously skipped. Verify each of them against a test
VM before relying on the new behaviour in production.
