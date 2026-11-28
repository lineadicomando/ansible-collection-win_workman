# foxit_pdf_reader — Foxit PDF Reader

Installs Foxit PDF Reader from the 64-bit multilingual (L10N) installer (`/quiet`),
a per-machine WiX Burn bundle wrapping an MSI. Standard package actions only, with a
custom uninstall.

## Notes

- Both the bundle and the MSI register as `Foxit PDF Reader`. Removing the MSI alone
  left the bundle entry behind, so `info` and `is_present` kept reporting Foxit
  installed after `off`, and a later `on` never reinstalled it. `off` therefore runs a
  `before_uninstall_ps_script` (in `vars/main.yaml`) that kills `FoxitPDFReader`, then
  runs the bundle's `QuietUninstallString` (its copy under `ProgramData\Package
  Cache`): Burn removes the MSI, its own registration and the cache. With no bundle
  entry (an MSI installed on its own) it runs `msiexec /x` on the MSI. pkg_utils'
  own uninstall step then finds nothing left; `cleanup_paths` drops the install
  directory.
- The script waits on the uninstaller process only (10 minutes at most), not with
  `Start-Process -Wait`, which waits for the whole job object and can hang on a
  leftover child.
- Foxit publishes no digest: the checksum is computed on the downloaded installer;
  `version` is its ProductVersion.
- Tested 2026-11-25 on a Windows test VM (2026.2.1.39815): download, copy, on, a no-op
  second on, info, is_present, off and info passed; after off no uninstall entry,
  directory, Package Cache copy, service, scheduled task or shortcut was left.
