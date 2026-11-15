# AutoCAD roles

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## Promote `odis_uninstall` and `find_products` to `pkg_utils`

**Priority:** P3 — refactoring; waits for the end-to-end validation below  
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

## End-to-end validation on a real host

**Priority:** P1 if AutoCAD LT 2026 is to be rolled out to a lab, P3 otherwise  
**Status:** blocking before lab-wide use — no run found in the project logs as
of 2026-10-31

- `autocadlt2026-on` has never been run end to end since `9304d43` rewrote its
  presence detection. The install path — 2.7 GB per host, the `db-bootstrap`
  polling, the licence registration through `AdskLicensingInstHelper` — is
  unverified.
- `autocadlt2023-off` was validated on one production host (2026-09-11); the
  `off-full` variant was not. That host is the natural candidate: it still carries
  exactly the leftovers that `off-full` targets (the two Material Library 2023
  packages, the emptied install directory, the ACDLT2023 licensing logs).
- `autocadlt2026-off-full` has never been run since the GUIDs became
  runtime-resolved in `65baf6b`.
