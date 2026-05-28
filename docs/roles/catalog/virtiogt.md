# Role: virtiogt

> **Work in progress** — preliminary draft.

Manages VirtIO Guest Tools, drivers and utilities for Windows virtual machines
running on KVM/QEMU hypervisors. Supports standard package operations: install,
uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade VirtIO Guest Tools |
| `off` | Uninstall VirtIO Guest Tools |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that VirtIO Guest Tools is installed |

---

## Configuration

No variables. VirtIO Guest Tools are installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - virtiogt
  - virtiogt-off
```

---

## Schema details

Software name: `VirtIO Guest Tools`  
Provider: `registry`  
Installer: `virtio-win*.exe` (version varies)  
Homepage: https://github.com/virtio-win/virtio-win-pkg-scripts

---

## Notes

VirtIO Guest Tools optimize performance of Windows VMs running on open-source
hypervisors (KVM, QEMU). Required for optimal I/O performance in virtualized environments.
