# geogebra — GeoGebra Calculator Suite (Classic 6)

Installs GeoGebra 6 machine-wide from the upstream MSI (`ALLUSERS=2 /qn`); detected
as `GeoGebra Classic`. Standard package actions only. For the legacy Classic 5 see
[geogebra5](geogebra5.md).

## Notes

- The build is the one `download.geogebra.org/package/win-msi6` redirects to.
  GeoGebra publishes no digest: the checksum is computed on the downloaded MSI.
- Tested 2026-11-25 on a Windows test VM (6.0.937.0): download, copy, on, a no-op
  second on, info, is_present, off and info passed, with nothing left on disk, in the
  shortcuts or in the uninstall entries.
