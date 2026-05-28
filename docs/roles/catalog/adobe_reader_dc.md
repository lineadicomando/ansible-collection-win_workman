# Role: adobe_reader_dc

> **Work in progress** — preliminary draft.

Manages Adobe Acrobat Reader DC, the free PDF viewer from Adobe. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Adobe Acrobat Reader DC |
| `off` | Uninstall Adobe Acrobat Reader DC |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Adobe Acrobat Reader DC is installed |

---

## Configuration

No variables. Adobe Acrobat Reader DC is installed with default settings and
EULA accepted silently.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - adobe_reader_dc
  - adobe_reader_dc-off
```

---

## Schema details

Software name: `Adobe Acrobat Reader DC`
Provider: `registry`
Installer: `AcroRdrDCx642600121367_MUI.exe` (64-bit MUI)
Homepage: https://www.adobe.com/acrobat/pdf-reader.html

---

## Notes

The installer is the official Adobe bootstrapper EXE that wraps an MSI package.
Silent flags (`/sAll /rs /msi EULA_ACCEPT=YES`) suppress all prompts and reboot
requests.
