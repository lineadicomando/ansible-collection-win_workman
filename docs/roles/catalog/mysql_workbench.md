# Role: mysql_workbench

> **Work in progress** — preliminary draft.

Manages MySQL Workbench, a unified visual tool for database architects, developers,
and DBAs. Supports standard package operations: install, uninstall, download, and
info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade MySQL Workbench |
| `off` | Uninstall MySQL Workbench |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that MySQL Workbench is installed |

---

## Configuration

No variables. MySQL Workbench is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - mysql_workbench
  - mysql_workbench-off
```

---

## Schema details

Software name: `MySQL Workbench`  
Provider: `registry`  
Installer: `mysql-workbench-ce-*.msi` (version varies)  
Homepage: https://www.mysql.com/products/workbench/

---

## Notes

MySQL Workbench requires .NET Framework. Installation includes EER (Entity-Relationship)
diagram design and SQL development tools.
