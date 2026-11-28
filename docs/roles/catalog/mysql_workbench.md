# mysql_workbench — MySQL Workbench

MySQL Workbench 8.0 CE from the Oracle MSI (`ALLUSERS=1`), `msi` provider. No
variables.

## Notes

- `on` installs [`vcredist14`](vcredist14.md) first (runtime requirement).
- The schema's public desktop shortcut takes its icon from the MSI's cached
  `WBIcon.exe` under `%SystemRoot%\Installer\{ProductCode}`: check the GUID at each
  bump. `searchName` (`MySQL Workbench 8.0 CE`) changes with the major line.
