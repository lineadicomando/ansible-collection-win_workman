# goldendict — GoldenDict-ng

Installs GoldenDict-ng, the maintained fork of GoldenDict, from the upstream NSIS
installer (`/S`), plus a shortcut on the public desktop (the installer creates only a
Start Menu one).

## Actions

| Action | Does |
|---|---|
| `on[-nodep]` | Installs [vcredist14](vcredist14.md) first (the program needs the MSVC runtime), then GoldenDict-ng; `nodep` skips the dependency |

## Notes

- Each upstream release ships two installers built against different Qt versions;
  the role uses the Qt 6.8 one.
- `off` runs the registered uninstaller directly (`uninstall_via_helper`); the
  uninstaller leaves its Start Menu folder behind, so that folder is in
  `cleanup_paths`.
- No offline dictionaries are shipped: out of the box only the online sources
  (Wikipedia, Wiktionary, web sites) answer. Settings and indexes are per-user, under
  `%APPDATA%\GoldenDict`. A `content\defconfig` file in the install directory is the
  template for users with no configuration yet; the role does not manage it.
- The checksum is the asset digest of the GitHub release.
- Tested 2026-11-25 on a Windows test VM (26.11.0): download, copy, on (dependency
  included), a no-op second on, info, is_present, off and info passed, with nothing
  left on disk, in the shortcuts or in the uninstall entries.
