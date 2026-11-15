# MCP server

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

This section is about the server in the project repo (`ansible-win_edulab`,
`mcp/`), which provides `run_powershell` and `run_playbook`. The collection has
its own server in `mcp/` (`run_tasks`, `get_role_info`), with a byte-identical
copy of `runlog.py`.

## `run_powershell`: `timeout` is ignored with `background=true`

**Priority:** P3 — no harm observed, but a hung background run is never killed  
**Status:** found 2026-10-08 on a production host; cause read in the code, fix not written (re-checked 2026-11-15: `server.py:410-411` of the project still calls `start_run` without `timeout`)

A `DISM /StartComponentCleanup` started with `background=true` and
`timeout=3600` ran for 65 minutes and ended on its own. The tool schema describes `timeout` as "Seconds
before the run is killed", with no exception for background runs.

The background branch of `run_powershell` (`mcp/server.py:410`) calls
`start_run(cmd, label, env=ADHOC_ENV, redact=redact)` and drops `timeout`. The
fix touches two files: `start_run` in `mcp/ansible_runner.py` takes no
`timeout` either, while `start_logged` in `mcp/runlog.py` accepts one and hands
it to the supervisor. The synchronous branch passes it to `run_raw`.
Re-checked 2026-10-31: unchanged.

To decide before passing it through: the default is 300 seconds, which suits a
synchronous query but would kill most background runs, started in the
background precisely because they are long. Either apply the timeout to a
background run only when the caller sets it explicitly, or say in the schema
that it does not apply there. `run_tasks` and `run_playbook` take no `timeout`
at all, so their background runs are unbounded by design.

Killing `ansible` on the controller does not stop what is already running on
the host: check what happens to a `dism.exe` or an installer left behind before
relying on the timeout to clean up.
