# embarcadero_devcpp — Embarcadero Dev-C++

Embarcadero Dev-C++ 6.3 with TDM-GCC 9.2, from the NSIS installer, `registry`
provider. No variables. Maintained alternative: [redpanda_cpp](redpanda_cpp.md).

## Notes

- The installer is 32-bit NSIS: on x64 it lands in `%ProgramFiles(x86)%\Embarcadero\Dev-Cpp`,
  which the schema's shortcut points at.
- After install, the desktop link the installer puts in the connecting account's
  profile is deleted; the schema creates `%Public%\Desktop\Embarcadero Dev-C++.lnk`
  for everyone instead.
- `off` uninstalls through the NSIS helper (`uninstall_via_helper`), then removes the
  uninstall key (`cleanup_registry_key`), the public desktop link, the Start Menu
  folder and the install directory under both Program Files paths.
- Shares the `DevCpp.*` file associations with `orwell_devcpp` and `redpanda_cpp`:
  whichever is installed last owns them.
