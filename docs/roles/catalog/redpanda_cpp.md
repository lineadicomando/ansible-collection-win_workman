# redpanda_cpp — Red Panda C++

Red Panda C++, a maintained Dev-C++ successor, 64-bit build with the bundled MinGW64
GCC 15.3.0, installed for all users under `%ProgramFiles%\RedPanda-Cpp`, `registry`
provider. No variables.

## Notes

- Proposed as the replacement for `orwell_devcpp` (last released in 2015) and
  `embarcadero_devcpp`: same Dev-C++ workflow and project format, same `.dev`, `.c`,
  `.cpp` and header associations. Install them side by side only for comparison:
  whichever is installed last owns the associations.
- NSIS with the MultiUser extension: `/AllUsers` makes the install, the shortcuts and
  the file associations machine-wide. The installer creates the all-users desktop and
  Start Menu shortcuts and its uninstaller removes them, so the schema declares none.
- `DisplayName` is `<app name> (<arch>)`, hence `searchName: "Red Panda C++*"`.
- The upstream uninstaller removes the `DevCpp.*` ProgID keys but leaves the eight
  extension keys under `HKLM:\Software\Classes` pointing at them. `off` runs an
  `after_uninstall_ps_script` that drops the extensions whose ProgID is really gone,
  so an `orwell_devcpp` or `embarcadero_devcpp` still owning `DevCpp.*` keeps its
  associations.
- Upstream's 32-bit, portable and `NoCompiler` variants are not covered.
