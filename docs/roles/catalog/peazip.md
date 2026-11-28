# peazip — PeaZip

PeaZip archiver, Inno Setup installer, 64-bit (`registry` provider,
`/VERYSILENT /SUPPRESSMSGBOXES /NORESTART` for install and uninstall).

## Notes

- Inno registers the entry as `PeaZip <version> (WIN64)`: an exact `PeaZip`
  `searchName` never matched, hence `PeaZip * (WIN64)`.
