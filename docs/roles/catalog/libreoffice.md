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
Installer: `LibreOffice_<version>_Win_x86-64.msi`  
Homepage: https://www.libreoffice.org/

---

## Notes

- Installation location: `%ProgramFiles%\LibreOffice`
- Supports all standard Microsoft Office file formats (.docx, .xlsx, .pptx)
- First launch may take longer due to component registration
- Compatible with Microsoft Office templates and macros (with limitations)
- `searchName` matches any release (`LibreOffice [0-9]*.[0-9]*.[0-9]*.[0-9]*`): every
  LibreOffice MSI shares one UpgradeCode, so a new version replaces the installed one and
  `on` has to see that one to upgrade it. Help packs (`LibreOffice 26.2 Help Pack (...)`)
  do not match
- The Online Update feature installs the *LibreOffice Maintenance Service*
  (`update_service.exe`), which the MSI never removes: its `uninstall_updateservice` action
  cannot run under `REMOVE=ALL`. `off` deletes the service, its
  `HKLM\SOFTWARE\LibreOffice\MaintenanceService` key and the `program\logs` leftover. The
  feature is not left out at install time: `REMOVE=gm_o_Onlineupdate` alone makes the MSI
  install nothing on a new product, and `ADDLOCAL=ALL` would add every optional feature
