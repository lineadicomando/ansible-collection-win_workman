# python314 — Python 3.14

Python 3.14 for all users from the python.org installer (a WiX Burn bundle), in
`%ProgramFiles%\Python314`, on the system PATH, without the `py` launcher
(`InstallAllUsers=1 PrependPath=1 Include_launcher=0`), with public desktop shortcuts
to the interpreter and IDLE. No variables. `python310` … `python315` share this page's
design; their pages say only what differs.

## Notes

- **Detection.** The bundle registers its `Python 3.14.x (64-bit)` entry only in HKCU
  of the account that ran it, even for an all-users install. The role detects the
  machine-wide `Python 3.14.* Core Interpreter (64-bit)` MSI instead, so `info`, `on`
  and `off` work from any account.
- **Removal.** `off` also removes the bundle's other MSIs, `Executables` last (the
  others locate their directory through its `python.exe`), the bundle registration of
  the connecting account, `HKLM:\SOFTWARE\Python\PythonCore\3.14\InstalledFeatures`
  and the orphaned Package Cache copies of 3.14 MSIs: see
  [pkg_utils](../core/pkg_utils.md#burn-bundles-registered-per-user-bundle_parts). A
  registration left in another profile points at packages that are gone.
- `cleanup_paths` removes the install directory, the Start Menu folder and the two
  desktop links.
- The IDLE shortcut's icon is the MSI's cached `idle.exe` under
  `%SystemRoot%\Installer\{ProductCode}`: check the GUID at each bump.
