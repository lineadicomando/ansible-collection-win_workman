# gimp — GIMP

Installs GIMP 3 machine-wide from the upstream Inno Setup installer (`registry`
provider, `/ALLUSERS`, desktop icon). Standard package actions only.

## Notes

- download.gimp.org has no checksum file next to the installer: the sha256 comes
  from `gimp_versions.json` in the gimp-web repository.
- Tested 2026-11-25 on a Windows test VM (3.2.8): download, copy, on, a no-op second
  on, info (DisplayVersion `3.2.8.0`), is_present, off and info passed, with nothing
  left on disk, in the shortcuts or in the uninstall entries.
