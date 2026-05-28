# Role: libreoffice

> **Work in progress** — preliminary draft.

Manages LibreOffice, a free and open-source office productivity suite. Supports
standard package operations: install, uninstall, download, and info queries.
LibreOffice includes Writer (word processor), Calc (spreadsheet), Impress (presentations),
and Draw (vector graphics).

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade LibreOffice |
| `off` | Uninstall LibreOffice |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that LibreOffice is installed |

---

## Configuration

No variables. LibreOffice is installed with default settings and all components
(Writer, Calc, Impress, Draw, Math, Base).

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - libreoffice
  - libreoffice-off
```

---

## Schema details

Software name: `LibreOffice`  
Provider: `registry`  
Installer: `LibreOffice_Windows_Installer.exe`  
Homepage: https://www.libreoffice.org/

---

## Notes

- Installation location: `%ProgramFiles%\LibreOffice`
- Supports all standard Microsoft Office file formats (.docx, .xlsx, .pptx)
- First launch may take longer due to component registration
- Compatible with Microsoft Office templates and macros (with limitations)
