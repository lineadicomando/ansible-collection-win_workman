# powertoys — Microsoft PowerToys

Microsoft PowerToys, per-machine WiX Burn bundle (`registry` provider, `-silent`;
uninstall through the helper with `/quiet`). The schema pins the x64 installer.

## Notes

- The bundle registers two uninstall entries: the MSI, `PowerToys (Preview)`, and the
  bundle, `PowerToys (Preview) x64`, whose uninstaller is its copy under
  `%ProgramData%\Package Cache`. The role detects the bundle and runs that uninstaller,
  so Burn removes the MSI, its own registration and the caches. Detecting the MSI, as
  the role did up to 0.99.1, made `off` remove only the MSI and left PowerToys listed
  under Apps.
- The WebView2 bootstrapper is a shared prerequisite of the bundle: its cached copy
  (`MicrosoftEdgeWebview2Setup.exe`, about 2 MB) stays after `off`, as Burn intends
  for packages other software may depend on.
