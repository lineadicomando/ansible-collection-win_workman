# nircmd — NirCmd

NirSoft NirCmd, `portable` provider: `nircmd-x64.zip` extracted with 7-Zip into
`C:\PortableApps\NirCmd`, added to the system `PATH`.

## Notes

- The URL is the vendor's unversioned "latest" link and no checksum is pinned: the
  first download stays in storage (`download` does not overwrite it) and the portable
  marker (filename and URL) never changes, so `on` never upgrades a host. To move to a
  new release: delete `nircmd-x64.zip` from `win_workman_storage_path`, then
  `nircmd-off` and `nircmd`.
