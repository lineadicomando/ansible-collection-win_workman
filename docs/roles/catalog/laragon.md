# Role: laragon

> **Work in progress** — preliminary draft.

Manages Laragon, a portable development environment for PHP, Node.js, Python,
Java, Go, and other languages. Includes Apache, Nginx, MySQL, and other services.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Laragon |
| `off` | Uninstall Laragon |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Laragon is installed |

---

## Configuration

No variables. Laragon is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - laragon
  - laragon-off
```

---

## Schema details

Software name: `Laragon`  
Provider: `registry`  
Installer: `laragon-wamp-*.exe` (version varies)  
Homepage: https://laragon.org/

---

## Notes

Laragon is portable and includes support for multiple web server stacks.
Installation location is configurable during setup.
