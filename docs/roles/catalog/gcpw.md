# Role: gcpw

> **Work in progress** — preliminary draft.

Installs Google Credential Provider for Windows (GCPW) and configures the
`domains_allowed_to_login` registry key. Supports 32-bit and 64-bit variants.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade GCPW and set `domains_allowed_to_login` |
| `off` | Uninstall GCPW |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that GCPW is installed |

---

## Architecture selection

| Task string | Arch | Installer |
|---|---|---|
| `gcpw-on` *(default)* | `64bit` | `gcpwstandaloneenterprise64.msi` |
| `gcpw-on-32bit` | `32bit` | `gcpwstandaloneenterprise.msi` |

The token `32bit` must appear anywhere in `argv` (position 2+).

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_gcpw_domains_allowed_to_login` | `""` | **Required for `on`.** Comma-separated list of Google Workspace domains allowed to sign in (e.g. `school.edu` or `school.edu,other.edu`) |

The role **fails immediately** if `win_workman_gcpw_domains_allowed_to_login` is
empty or does not contain a valid domain name when action is `on`.

---

## Post-install and post-uninstall behaviour

### After install (`on`)

1. Registry key `HKLM\SOFTWARE\Google\GCPW\domains_allowed_to_login` is set to
   `win_workman_gcpw_domains_allowed_to_login` (key path created if absent).
2. The target is **rebooted** if the package was actually installed or upgraded
   (`win_workman_install_result.changed`).

### After uninstall (`off`)

1. The registry key `HKLM:\SOFTWARE\Google\GCPW` is removed entirely.
2. The target is **rebooted** if the package was actually removed
   (`win_workman_uninstall_result.changed` or `win_workman_uninstall_via_helper_result.changed`).

---

## Example

```yaml
# group_vars/lab_pcs.yml
win_workman_gcpw_domains_allowed_to_login: "school.edu"

win_workman_tasks:
  - gcpw
```

Multiple domains:

```yaml
win_workman_gcpw_domains_allowed_to_login: "school.edu,staff.school.edu"
```

---

## Schema details

Software name: `Google Credential Provider for Windows`  
Provider: `registry` (MSI)  
Installer (64-bit): `gcpwstandaloneenterprise64.msi`  
Installer (32-bit): `gcpwstandaloneenterprise.msi`  
Homepage: https://tools.google.com/dlpage/gcpw

---

## Notes

- The `searchName` is `Google Credential Provider for Windows` — verify with
  `Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' | Select DisplayName`
  on a target host after first install.
- GCPW requires an active Google Workspace account and network connectivity to
  Google's authentication servers.
- Chrome is installed automatically as part of the `on` action: Google services
  (Drive, Classroom, Gmail, etc.) are accessed through the browser, and Chrome
  is the only browser that natively inherits the Google session established by
  GCPW at sign-in. Chrome installation is skipped for all other actions (`off`,
  `info`, `download`, etc.).
