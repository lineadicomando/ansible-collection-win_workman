# Role: foxit_pdf_reader

> **Work in progress** — preliminary draft.

Manages Foxit PDF Reader, the lightweight PDF viewer from Foxit Software. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Foxit PDF Reader |
| `off` | Uninstall Foxit PDF Reader |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Foxit PDF Reader is installed |

---

## Configuration

No user-configurable variables. The installer runs silently with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - foxit_pdf_reader
  - foxit_pdf_reader-off
```

---

## Schema details

Software name: `Foxit PDF Reader`
Provider: `registry`
Installer: `FoxitPDFReader202611_L10N_Setup_Prom_x64.exe` (64-bit, multilingual)
Homepage: https://www.foxit.com/pdf-reader/

---

## Notes

The installer is the official L10N promotional EXE from the Foxit CDN. Silent
installation uses the `/S` flag (NSIS). Before uninstalling, the role kills any
running `FoxitPDFReader.exe` processes via a PowerShell hook.

The checksum in `vars/main.yaml` must be verified before production use:

```bash
sha256sum FoxitPDFReader202611_L10N_Setup_Prom_x64.exe
```

Verify that `searchName` matches the `DisplayName` in the Windows Uninstall registry
(`"Foxit PDF Reader"`) before deploying to a new OS version.
