# gcpw — Google Credential Provider for Windows

GCPW enterprise MSI (`registry` provider, `/quiet`), Google's current release with no
version or checksum pinned; 64-bit by default, the task argument `32bit` selects the
x86 MSI. Lets users sign in to Windows with a Google Workspace account of the allowed
domains. `on` installs Chrome first and may restart the host.

## Actions

| Action | Does |
|---|---|
| `on[-nodep]` | Fails at once unless `win_workman_gcpw_domains_allowed_to_login` starts with a valid domain; installs `chrome` (skipped with `nodep`), then GCPW; writes `HKLM\SOFTWARE\Google\GCPW\domains_allowed_to_login`; restarts the host when the MSI changed something |
| `off` | Uninstalls GCPW, deletes `HKLM\SOFTWARE\Google\GCPW`, restarts the host when something was removed; Chrome stays |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_gcpw_domains_allowed_to_login` | `""` | **Required for `on`.** Comma-separated Google Workspace domains allowed to sign in (`example.com` or `example.com,staff.example.com`) |

## Notes

- Chrome is installed because it is the only browser that inherits the Google session
  GCPW opens at sign-in, and Google services are used through it. The `32bit` token
  reaches the chrome role too: `gcpw-on-32bit` installs 32-bit Chrome.
- The domain check only matches the start of the value against
  `^[a-zA-Z0-9][a-zA-Z0-9\-]*\.[a-zA-Z]{2,}`: later entries of the list are not
  validated.
- With no version pinned, `on` runs the MSI on every run, which rewrites the registry
  value; `win_package` reports no change for the same MSI, so there is no restart.
  The installer kept in storage is the one downloaded first: delete it to fetch a newer
  release.
- GCPW needs network access to Google's authentication servers at sign-in.
