# vcredist14 — Visual C++ Redistributable 2015-2022 (x64)

Microsoft Visual C++ v14 Redistributable, x64 only (`registry` provider,
`/quiet /norestart`). Pulled in by the `on` of `goldendict`, `mysql_server`,
`mysql_workbench`, `ntop`, `seb` and `sketchup2026`.

## Notes

- Pinned to a versioned download instead of the evergreen
  `aka.ms/vc14/vc_redist.x64.exe`: with no version the install ran at every play, and
  again for every role depending on this one. To bump, follow the aka.ms redirect and
  read `ProductVersion` from the installer (it is also the `DisplayVersion` of the
  bundle's entry); the permalink path carries the file's sha256.
- `searchName` is `Microsoft Visual C++*Redistributable (x64)*`, x64 only: the x86
  redistributable matched a looser pattern and, picked when its version was higher,
  hid a missing or older x64 one. The pattern also matches the 2012 and 2013 x64
  redistributables, so on a host that has one of those and no v14, `off` removes it.
