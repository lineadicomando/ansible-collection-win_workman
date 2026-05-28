# Role: {ROLE_NAME}

> **Work in progress** — preliminary draft.

{FULL_DESCRIPTION}. Supports standard package operations plus role-specific
actions for {CUSTOM_FEATURE_BRIEF}.

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
| `{CUSTOM_ACTION_1}` | {DESCRIPTION} |
| `{CUSTOM_ACTION_2}` | {DESCRIPTION} |

---

## {FEATURE_SECTION_TITLE}

{DETAILED_EXPLANATION_OF_CUSTOM_FEATURE}

| {COLUMN_1} | {COLUMN_2} |
|---|---|
| {VALUE_1} | {DESCRIPTION_1} |
| {VALUE_2} | {DESCRIPTION_2} |

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_{role}_var1` | `default_value` | Description |
| `win_workman_{role}_var2` | `default_value` | Description |

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - {ROLE_NAME}
  - {ROLE_NAME}-{CUSTOM_ACTION_1}
```

---

## Schema details

Software name: `{SOFTWARE_NAME}`  
Provider: `{PROVIDER_TYPE}` (registry | portable | msi | exe)  
Installer: `{INSTALLER_FILENAME}`  
Homepage: {HOMEPAGE_URL}

---

## Notes

{IMPLEMENTATION_NOTES}

Example:
- Before install, any running process is force-killed
- {CUSTOM_ACTION_1} removes user data from: {LOCATIONS}
- Requires internet access for: {RESOURCE}
