# blender — Blender

Installs Blender from the upstream x64 MSI, one minor series at a time. Standard
package actions only.

## Notes

- Every Blender MSI registers as `Blender`, but its `UpgradeCode` changes with each
  minor series (5.2.1 and 5.3.0 differ). A patch release replaces the installed one in
  place; a new series installs side by side, in its own
  `Blender Foundation\Blender 5.x` directory.
- The schema therefore sets `version_like: "5.3*"` and `exclusive: true` (see
  [pkg_utils](../core/pkg_utils.md)): `on` uninstalls every machine-wide `Blender`
  entry of another series first, and `info`, `is_present` and `off` see only the
  current series. At every series bump update `version_like` together with `version`
  and `product_id` (the MSI's ProductCode, new at every release).
- The checksum is the `blender-<version>.sha256` published with the release.
- Tested 2026-11-25 on a Windows test VM with 5.2.1 installed: `on` removed 5.2.1 and
  installed 5.3.0, a second `on` was a no-op, is_present, off and info passed, and
  nothing was left under `Blender Foundation`, in the shortcuts or in the uninstall
  entries.
