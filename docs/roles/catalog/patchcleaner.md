# patchcleaner

> **Work in progress** — preliminary draft.

Cleans up superseded Windows updates from the WinSxS component store,
recovering disk space.

| Action | Description |
|---|---|
| `on` | Install PatchCleaner |
| `off` | Uninstall PatchCleaner |
| `download` | Download PatchCleaner installer only |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |

PatchCleaner is a software package managed via `pkg_utils`.
See [`pkg_utils.md`](../core/pkg_utils.md) for schema details.
