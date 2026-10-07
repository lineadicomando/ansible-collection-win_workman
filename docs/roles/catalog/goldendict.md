# Role: goldendict

> **Work in progress** — preliminary draft.

Manages GoldenDict-ng, an open-source dictionary lookup program that reads many
offline dictionary formats (StarDict, DSL, MDX, …) and online sources. Supports
standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade GoldenDict-ng |
| `off` | Uninstall GoldenDict-ng |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that GoldenDict-ng is installed |

---

## Configuration

No variables. GoldenDict-ng is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - goldendict
  - goldendict-off
```

---

## Dependencies

`on` installs [`vcredist14`](vcredist14.md) first: GoldenDict-ng needs the MSVC
runtime. Use `goldendict-on-nodep` to skip it.

---

## Schema details

Software name: `GoldenDict-ng`  
Provider: `registry`  
Installer: `GoldenDict-ng-26.8.0-Qt6.8.3-Windows-installer.exe`  
Homepage: https://xiaoyifang.github.io/goldendict-ng/

---

## Notes

This is GoldenDict-ng, the maintained fork, not the original GoldenDict. Each
upstream release ships two installers built against different Qt versions; the
role uses the Qt 6.8 one.

The installer ships no offline dictionaries: out of the box only the online
sources (Wikipedia, Wiktionary, web sites) answer. Settings and indexes are
per-user, under `%APPDATA%\GoldenDict`. A `content\defconfig` file in the install
directory is used as the template for users who have no configuration yet; the
role does not manage it.
