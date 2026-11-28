# zoom — Zoom Workplace

Installs the Zoom Workplace 64-bit machine-wide MSI. Standard package actions only.

## Notes

- Upstream serves the same filename, `ZoomInstallerFull.msi`, for every release: the
  stored filename carries the version so two releases never share one.
- `version` and `product_id` are the MSI's ProductVersion (`7.2.51704`, three parts,
  not the four-part release number in the URL) and ProductCode, which changes with
  every release: update both at every bump.
- Zoom publishes no digest: the checksum is computed on the downloaded MSI.
- Tested 2026-11-25 on a Windows test VM with 7.2.1 installed: info saw it, on
  upgraded it in place, a second on was a no-op, is_present, off and info passed, and
  no directory, service, shortcut or uninstall entry was left.
