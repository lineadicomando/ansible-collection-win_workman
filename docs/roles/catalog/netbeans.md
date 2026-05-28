# Role: netbeans

> **Work in progress** — preliminary draft.

Manages Apache NetBeans, a free and open-source IDE for Java, PHP, HTML5, and
other languages. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Apache NetBeans |
| `off` | Uninstall Apache NetBeans |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Apache NetBeans is installed |

---

## Configuration

No variables. Apache NetBeans is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - netbeans
  - netbeans-off
```

---

## Schema details

Software name: `Apache NetBeans`  
Provider: `registry`  
Installer: `Apache-NetBeans-30.exe`  
Homepage: https://netbeans.apache.org/

---

## Notes

This role uses the [codelerity](https://github.com/codelerity/netbeans-packages)
distribution of Apache NetBeans, which bundles a compatible JDK — no separate
Java installation required.
