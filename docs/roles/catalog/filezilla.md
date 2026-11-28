# filezilla — FileZilla Client

FileZilla Client, 64-bit NSIS installer (`registry` provider, `/S`, uninstall through
the helper), taken from the Chocolatey package.

## Notes

- The vendor publishes no stable installer URL (its CDN links are signed and expire
  after one hour) and asks package managers not to download from its servers. The
  role downloads the `.nupkg` from Chocolatey instead, the source Scoop uses too: a
  plain zip with a versioned permalink holding the untouched vendor installers under
  `tools/`. It is extracted on the target, hence the `tools\` prefix in `setup_file`.
  Sources, checksums and the bump procedure: header of `roles/filezilla/vars/main.yaml`.
