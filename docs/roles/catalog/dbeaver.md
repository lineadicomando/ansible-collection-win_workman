# Role: dbeaver

> **Work in progress** — preliminary draft.

Manages DBeaver, a free and open-source universal database tool. Supports standard
package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade DBeaver |
| `off` | Uninstall DBeaver |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that DBeaver is installed |

---

## Configuration

No variables. DBeaver is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - dbeaver
  - dbeaver-off
```

---

## Schema details

Software name: `DBeaver`  
Provider: `registry`  
Installer: `dbeaver-ce-26.0.4-windows-x86_64.exe`  
Homepage: https://dbeaver.io

---

## Notes

DBeaver supports over 80 database types including PostgreSQL, MySQL, SQLite,
Oracle, SQL Server, and NoSQL databases. Community Edition (CE) is feature-rich
and sufficient for most use cases.
