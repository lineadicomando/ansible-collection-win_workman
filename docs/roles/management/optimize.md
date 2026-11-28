# optimize — Disk optimisation

Runs `Optimize-Volume` (the PowerShell `defrag /O`) on each listed drive and prints
what it reports. Windows picks the operation by media type: retrim on SSDs, analysis
and defragmentation on HDDs, which can take long. There is no `off`.

## Actions

| Action | Does |
|---|---|
| `on` (default) | Optimise every drive in `win_workman_optimize_volumes` |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_optimize_volumes` | `["C"]` | Drive letters, no colon |
| `win_workman_optimize_defrag` | `false` | Pass `-Defrag`: defragment whatever the media type, SSDs included (not recommended) |

## Notes

- `Optimize-Volume` reports only on the verbose stream, with hundreds of progress
  lines (`<step>:  33% ...`): the task captures the stream and drops them.
- Always reports `changed`.
- Planned, not built: an `analyze` action (`Optimize-Volume -Analyze`) that reports
  fragmentation without defragmenting HDDs, see
  [management](../../todo/management.md).
