# ntop — NTop

NTop, a `top`-like process viewer for the Windows console (not ntopng). `portable`
provider: one `NTop.exe` into `C:\PortableApps\NTop`, added to the system `PATH`.
`on` installs [`vcredist14`](vcredist14.md) first.

## Notes

- No checksum is pinned, so the portable marker records the URL: a bump of the URL
  reinstalls. But the stored filename `NTop.exe` carries no version and `download`
  does not overwrite an existing file without a checksum, so the controller's storage
  keeps serving the old binary until `NTop.exe` is deleted from
  `win_workman_storage_path`.
