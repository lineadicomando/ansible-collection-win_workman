# audacity — Audacity 4

Installs Audacity 4.x from the upstream x86_64 MSI (upstream also publishes an arm64
MSI, not covered), under `%ProgramFiles%\Audacity 4` (`bin\Audacity4.exe`), and
removes older releases on the way.

## Actions

| Action | Does |
|---|---|
| `on` | Uninstalls every superseded release (1.x–3.x), then installs or upgrades 4.x |

## Notes

- 4.0 is the first release shipped as an MSI; 3.x and earlier are Inno Setup
  packages, registered as `Audacity_is1` with the version in the DisplayName
  (`Audacity 3.7.9`) under `C:\Program Files\Audacity`. The MSI's DisplayName is its
  ProductName (`Audacity 4.0`), so `searchName` is `Audacity 4*`.
- The MSI carries a WiX `MajorUpgrade`: a newer 4.x build replaces the installed one
  in place. Its `UpgradeCode` supersedes only the 4.x line, so a 3.x install would
  survive and sit side by side. `on` therefore first runs `pkg_utils/pkg_act_off`
  with a throwaway schema for each glob in `win_workman_audacity_superseded_searchnames`
  (`Audacity 1*`, `2*`, `3*`), running the Inno uninstaller with
  `win_workman_audacity_superseded_uninstall_args` (`/VERYSILENT /NORESTART
  /SUPPRESSMSGBOXES`). A glob that matches nothing is a no-op. Both lists are in
  `vars/main.yaml`; add `"Audacity 4*"` there when a 5.x line supersedes this one.
- The Inno uninstaller deletes only what it registered: on a real lab workstation six
  files survived (bundled Nyquist plug-ins carried over from older releases,
  `mod-script-pipe.dll`, `lib-cloud-upload.dll`, `README.txt`), and pkg_utils'
  leftovers pass by design removes a directory only when nothing but `unins*`
  remains. The throwaway schema lists `%ProgramFiles%\Audacity` and
  `%ProgramFiles(x86)%\Audacity` as `cleanup_paths`, run only when an uninstall
  actually happened. That takes the whole directory: a Nyquist plug-in a teacher
  dropped in by hand goes with it and has to be put back under the 4.x tree.
- `off` removes only 4.x and leaves an older release alone: removing those is a
  property of installing.
- The MSI declares no `ALLUSERS`, so on its own it puts the desktop and Start Menu
  shortcuts in the profile of whoever runs it, over SSH the Ansible account. The role
  passes `ALLUSERS=1`, which moves them to `%Public%\Desktop` and `%ProgramData%`
  (verified on a lab VM: without it the only shortcuts were in the Ansible account's
  profile). The schema declares no shortcuts of its own.
- Tested 2026-11-25 on a Windows test VM (4.0.2): download, copy, on, a no-op second
  on, is_present, off and info passed; the install directory, shortcuts and uninstall
  entry were gone after off.
