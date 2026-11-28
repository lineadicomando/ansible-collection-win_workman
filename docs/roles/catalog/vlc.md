# vlc — VLC media player

Installs VLC from the upstream NSIS installer (`/S`). Standard package actions only.

## Notes

- `off` runs the registered uninstaller directly (`uninstall_via_helper`), as for
  every NSIS installer in the collection.
- The sha256 is the videolan.org sidecar, checked against the mirror download.
- Tested 2026-11-17 on a real host: upgrade from 3.0.23, `info` then reported 3.0.24
  with a single uninstall entry.
