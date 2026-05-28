# Role: rustdesk

RustDesk open-source remote desktop software. Supports standard package operations:
install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade RustDesk |
| `off` | Uninstall RustDesk |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that RustDesk is installed |

---

## Variables

No role-specific variables.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - rustdesk
  - rustdesk-off
```

---

## Schema details

Software name: `RustDesk`
Provider: `registry` (MSI)
Installer: `rustdesk-1.4.6-x86_64.msi`
Homepage: https://rustdesk.com

---

## Notes

No special configuration or behavior.
