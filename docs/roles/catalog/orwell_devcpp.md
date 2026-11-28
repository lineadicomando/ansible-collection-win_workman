# orwell_devcpp — Orwell Dev-C++

Orwell Dev-C++ 5.11 with TDM-GCC 4.9.2, from the NSIS installer on SourceForge,
`registry` provider. No variables. Upstream's last release (2015); maintained
alternative: [redpanda_cpp](redpanda_cpp.md).

## Notes

- Detected as `Dev-C++`; `off` uninstalls through the NSIS helper
  (`uninstall_via_helper`).
- Shares the `DevCpp.*` file associations with `embarcadero_devcpp` and
  `redpanda_cpp`: whichever is installed last owns them.
