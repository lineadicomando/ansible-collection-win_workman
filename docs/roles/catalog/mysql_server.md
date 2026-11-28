# mysql_server — MySQL Server

MySQL Server 9.x from the Oracle MSI, `msi` provider, detected as `MySQL Server 9*`.
No variables. The role installs the files only: no instance, service or data
directory is configured.

## Notes

- `on` installs [`vcredist14`](vcredist14.md) first (runtime requirement).
- `uninstall_before_upgrade: true`: the MSIs do not upgrade in place across versions,
  so the old one is removed before the new one is installed.
