# Role: optimize

> **Work in progress** — preliminary draft.

Runs `Optimize-Volume` (the PowerShell equivalent of `defrag /O`) on one or
more drives. On SSDs this performs TRIM; on HDDs it performs analysis and,
optionally, full defragmentation.

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
| `win_workman_optimize_defrag` | `false` | Pass `-Defrag` to `Optimize-Volume` (full defrag on HDDs; ignored on SSDs) |

---

## Usage

```yaml
# Optimise C: and D: with TRIM only (SSD-safe default)
win_workman_tasks:
  - optimize-on
win_workman_optimize_volumes:
  - C
  - D

# Full defrag on an HDD
win_workman_tasks:
  - optimize-on
win_workman_optimize_defrag: true
```
