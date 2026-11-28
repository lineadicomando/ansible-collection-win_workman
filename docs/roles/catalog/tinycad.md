# tinycad — TinyCAD

Installs TinyCAD (schematic capture) as a `portable` package: the upstream installer
is extracted with 7-Zip into `<win_workman_portable_path>\TinyCAD`
(`C:\PortableApps\TinyCAD` by default), with a shortcut on the public desktop. No
uninstall entry is registered. Standard package actions only.

## Notes

- The role uses the `-x64` installer: the plain one is universal and carries both
  `app-64.7z` and `app-arm64.7z`, which the extraction lays over each other, at twice
  the download.
- The checksum is the asset digest of the GitHub release.
- Tested 2026-11-25 on a Windows test VM with 4.0.8 installed: `on` replaced it with
  4.1.2 (`TinyCAD.exe` x64, 4.1.2.0), a second `on` was a no-op, is_present and off
  passed, and nothing was left after off.
