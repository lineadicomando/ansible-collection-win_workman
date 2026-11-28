# postman — Postman

Postman, `portable` provider under `<win_workman_portable_path>\Postman`, with a public
desktop shortcut to `lib\net45\Postman.exe`. No variables.

## Notes

- The download is upstream's unversioned "latest" URL with no checksum: the version
  is whatever Postman serves that day, and with `uninstall_before_upgrade: true`
  every `on` removes and re-extracts it (see
  [architecture](../../architecture.md#providers)).
- `Postman_64bit.exe` is a Squirrel setup: 7-Zip extracts it, then an
  `after_copy_ps_script` extracts the `Postman-*-full.nupkg` it contains into the same
  directory with the `7za.exe` staged in the remote temp directory.
