# puredata — Pure Data

Installs Pure Data (Pd vanilla) from the upstream NSIS installer (`/S`). Standard
package actions only.

## Notes

- `off` runs the registered uninstaller directly (`uninstall_via_helper`).
- The download sets `validate_certs: false` for msp.ucsd.edu. The host publishes no
  digest: the checksum comes from hashing the downloaded installer (size matching the
  server's content-length).
- `version` keeps upstream's dash form (`0.57-0`), which is also the DisplayVersion.
- Tested 2026-11-25 on a Windows test VM (0.57-0): download, copy, on, a no-op second
  on, info, is_present, off and info passed, with nothing left on disk, in the
  shortcuts or in the uninstall entries.
