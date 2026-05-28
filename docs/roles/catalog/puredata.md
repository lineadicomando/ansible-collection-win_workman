# Role: puredata

> **Work in progress** — preliminary draft.

Manages Pure Data (Pd), an open-source visual programming language for audio signal
processing and interactive multimedia. Supports standard package operations: install,
uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Pure Data |
| `off` | Uninstall Pure Data |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Pure Data is installed |

---

## Configuration

No variables. Pure Data is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - puredata
  - puredata-off
```

---

## Schema details

Software name: `Pure Data`  
Provider: `registry`  
Installer: `pd-*.exe` (version varies)  
Homepage: http://puredata.info/

---

## Notes

Pure Data is used for multimedia development, audio synthesis, and interactive art.
Supports real-time audio processing and networked communication via OSC (Open Sound Control).
