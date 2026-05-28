# Role: {ROLE_NAME}

> **Work in progress** — preliminary draft.

{ONE_LINE_DESCRIPTION}. Supports standard package operations: install, uninstall,
download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade {SOFTWARE_NAME} |
| `off` | Uninstall {SOFTWARE_NAME} |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that {SOFTWARE_NAME} is installed |

---

## Variables

{NO_VARIABLES_IF_NONE_OR_TABLE}

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - {ROLE_NAME}
  - {ROLE_NAME}-off
```

---

## Schema details

Software name: `{SOFTWARE_NAME}`  
Provider: `{PROVIDER_TYPE}` (registry | portable | msi | exe)  
Installer: `{INSTALLER_FILENAME}`  
Homepage: {HOMEPAGE_URL}

---

## Notes

{ANY_SPECIAL_NOTES_OR_CONSTRAINTS}

Example: If no special behavior, write:
"No special configuration or behavior."
