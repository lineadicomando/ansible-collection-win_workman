# Role: optimize

> **Work in progress** — preliminary draft.

Runs `Optimize-Volume` (the PowerShell equivalent of `defrag /O`) on one or
more drives. Windows picks the operation by media type: retrim on SSDs,
analysis and defragmentation on HDDs, which can take long. The task prints what
`Optimize-Volume` reports for each drive.

---

## Actions

| Action | Description |
|---|---|
| `on` | Optimise all volumes listed in `win_workman_optimize_volumes` |

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_optimize_volumes` | `["C"]` | List of drive letters to optimise (single letters, no colon) |
| `win_workman_optimize_defrag` | `false` | Pass `-Defrag` to `Optimize-Volume`: forces defragmentation whatever the media type, SSDs included (not recommended) |

---

## Usage

```yaml
# Optimise C: and D: with the default operation for each media type
win_workman_tasks:
  - optimize-on
win_workman_optimize_volumes:
  - C
  - D

# Force defragmentation
win_workman_tasks:
  - optimize-on
win_workman_optimize_defrag: true
```
