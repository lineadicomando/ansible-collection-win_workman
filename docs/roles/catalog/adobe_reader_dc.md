# adobe_reader_dc — Adobe Acrobat Reader DC

Installs the 64-bit MUI Acrobat Reader (continuous track) from Adobe's bootstrapper
EXE, which wraps an MSI (`/sAll /rs /msi EULA_ACCEPT=YES`: no prompts, no reboot).
Detected as `Adobe Acrobat (64-bit)`. Standard package actions only.

## Notes

- The download directory is not listable (403): the URL is built from the version.
  The update check is described at the top of `vars/main.yaml`.
- Adobe publishes no digest: the checksum comes from hashing the downloaded installer
  (size matching the server's content-length).
- Tested 2026-11-25 on a Windows test VM (26.003.22110): download, copy, on, a no-op
  second on, is_present, off and info passed; after off the install directory, the
  shortcuts and the ARM (update) service were gone.
