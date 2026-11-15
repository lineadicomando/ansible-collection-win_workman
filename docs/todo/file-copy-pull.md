# `file_copy-pull` on large directories

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## `file_copy-pull`: large directories lose files and flood the output

**Priority:** P2 — the action had only been run on small folders; on a large one it silently drops files and can bring down the MCP client  
**Status:** found 2026-11-05 on a production host; cause read in the log and in `tasks/act_pull.yaml`, fix not written

A `file_copy-pull` of three directories of about 550–575 files each, plus
three single files (1702 files, 36 MB in all), without `archive`, run through
`run_tasks` of the collection MCP server.

What happened:

- 1662 files arrived, 40 did not. The 40 are consecutive items of the
  `Fetch the files` loop: the host stopped answering for a while (SSH
  "connection refused", then "timed out", then "no route to host") and came
  back for the remaining items. The outage itself was outside the role.
- The play ended with the host `unreachable=1`, `failed=0`, and the loop
  result `"msg": "All items completed"`. `Report what was pulled` never ran,
  so nothing said which files were missing; they were found only by
  comparing the result list with the tree on the controller.
- The run log was **~380 MB**, almost all on the one line of the final loop
  result. Every item of the `subelements('Files')` loop carries `item.0`,
  the whole target **with its `Files` list**, so each per-item result is
  ~230 KB on a 575-file directory and the total grows with the square of the
  number of files. The MCP client lost the connection to the server while
  the run was still going (`Connection closed`); the run itself finished and
  its `.done` sentinel was written.

### What to change

1. Loop over a flat list of `{Index, Profile, Path, Rel}` built once
   (for instance with `subelements` followed by a `map` that drops `Files`),
   so that a per-item result no longer embeds the listing. Or pass only the
   fields `fetch` needs through `loop_control.label` and a slim loop var.
2. Retry a fetch on a transient SSH error (`retries`/`until` on the item, or
   `ignore_unreachable: true` on the task and a summary of what failed), and
   make the final report list the files that did not arrive, per item, with
   a non-zero count failing the host.
3. Consider switching to the archive path automatically above a file count
   threshold (one zip, one `fetch`). The role notes already recommend `archive`
   for many small files (`roles/file_copy/meta/mcp.yaml`, since `03660be`).
4. MCP server: check what the server does with a 380 MB run output and why
   the client connection dropped; the summary returned by `run_tasks` should
   stay small whatever the play prints (see also the server section below).

### How to reproduce without the original host

On a test VM:

1. Create a directory with ~600 small files in three subfolders, for
   instance by copying any `C:\Windows\WinSxS\amd64_*` component folder of
   that size, or with a PowerShell loop writing 600 small text files.
2. `run_tasks(["file_copy-pull"], extra_vars={"win_workman_file_copy_items":
   [{"src": "C:\\Temp\\pulltest", "dest": "pulltest"}]})` with three such
   items. Measure the run log size: it should grow roughly with the square of
   the files per item.
3. For the lost files: while the loop runs, block port 22 on the VM for a
   minute (`New-NetFirewallRule -Direction Inbound -LocalPort 22 -Protocol TCP
   -Action Block`, then remove it), or `virsh suspend`/`resume` the domain.
   Expect `unreachable=1`, `failed=0`, no report, and missing files on the
   controller.
4. After the fix: the same test must end with a list of the missing files
   (or none, after retries) and a log of a few MB at most.
