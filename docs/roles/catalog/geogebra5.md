# geogebra5 — GeoGebra Classic 5

Installs the legacy GeoGebra Classic 5 machine-wide from the upstream MSI
(`ALLUSERS=2 /qn`); detected as `GeoGebra 5`. Standard package actions only. For
GeoGebra 6 see [geogebra](geogebra.md).

## Notes

- The build is the one `download.geogebra.org/package/win-msi` redirects to.
  GeoGebra publishes no digest: the checksum is computed on the downloaded MSI.
- Tested 2026-11-25 on a Windows test VM (5.4.937.0): download, copy, on, a no-op
  second on, info, is_present, off and info passed, with nothing left on disk, in the
  shortcuts or in the uninstall entries.
