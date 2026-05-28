# Role: postman

> **Work in progress** — preliminary draft.

Manages Postman, a collaboration platform for API development. Supports standard
package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Postman |
| `off` | Uninstall Postman |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Postman is installed |

---

## Configuration

No variables. Postman is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - postman
  - postman-off
```

---

## Schema details

Software name: `Postman`  
Provider: `registry`  
Installer: `Postman-win64-*.exe` (version varies)  
Homepage: https://www.postman.com

---

## Notes

Postman includes tools for designing, building, testing, and monitoring APIs.
Requires internet connection for cloud synchronization features (optional).
