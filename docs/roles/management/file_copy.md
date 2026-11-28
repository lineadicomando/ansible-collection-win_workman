# file_copy — Files between controller and hosts

Copies files and folders between the controller and the hosts, both ways: material
handed out to a lab (exercises on every student's Desktop, a dataset in `C:\Lab`),
work and backups brought back. Over a bare `win_copy`/`fetch` it adds per-user
folders read from each user's registry (a Desktop redirected to OneDrive is
followed), one item list for `push`, `status`, `remove` and `pull`, and a push
source confined to its own controller folder. No logoff needed.

## Actions

| Action | Does |
|---|---|
| `push` (default) | Copy the items to the host; files equal to the controller copy are not sent again |
| `pull` | Fetch the items into `<pull_root>/<dest>/<host>/[<profile>/]<name>`; a source missing on a host is reported, not an error (a student may not have saved the file) |
| `status` | Compare each destination with the controller copy: `match`, `differ` (with counts of missing/different files) or `missing`; published as the `win_workman_file_copy_status` fact; changes nothing |
| `remove` | Delete what `push` created (below) |
| `on` / `off` | Aliases of `push` / `remove` |

## Items

`win_workman_file_copy_items`: a list of dicts (a single dict is accepted); each needs
`src`. `pull` reads `src` and `dest` the other way round.

| Field | push / status / remove | pull |
|---|---|---|
| `src` | Controller path relative to `win_workman_file_copy_root`; a trailing `/` copies the contents of a directory, not the directory | Host path: absolute, or relative to the profile folder with `profile` |
| `dest` | Host folder receiving `src`: absolute, or relative to the profile folder with `profile` | Controller subfolder of the pull root (optional) |
| `profile` | A name, a list, a wildcard (`stud*`) or `all`; `DOMAIN\name` patterns as in `pkg_utils` `profiles` | same |
| `folder` | Where a relative path starts: `desktop` (default), `documents`, `downloads`, `pictures`, `music`, `videos`, `profile` (the profile root) | same |
| `include_default` | Also the Default profile, for users created later | same |
| `archive` | Transfer a directory as one zip | Fetch a directory as `<name>.zip` |

Without `profile` the host path must be absolute; with it, relative and without
`..`. An explicitly named profile missing on a host fails that host, listing its
profiles; a wildcard matching nothing is not an error and skips
`win_workman_file_copy_profiles_exclude` (an explicit name is never excluded).

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_file_copy_items` | `[]` | The items, above |
| `win_workman_file_copy_root` | `{{ win_workman_storage_path }}/file_copy` | Controller folder push sources are relative to |
| `win_workman_file_copy_pull_root` | `{{ win_workman_storage_path }}/file_copy_pull` | Controller folder pull writes to |
| `win_workman_file_copy_profiles_exclude` | `[]` | Profiles skipped by wildcards and `all`, e.g. `[maint, admin]` |

```yaml
win_workman_file_copy_items:
  - src: exercises/test_3B/     # contents of the folder...
    profile: all
    dest: Test                  # ...into Desktop\Test
    include_default: true
```

Through MCP the items go in `extra_vars` of `run_tasks`
(`{"win_workman_file_copy_items": [...]}` with `t=["file_copy-push"]`).

## Notes

- Controller side: `push`, `status`, `remove` start with the `file_copy_manifest`
  lookup, run once for the play (`run_once`): files with host path, size and SHA1,
  and the top-level names `remove` deletes. The items must therefore be the same for
  every host of the run, as they are in extra vars.
- The lookup is the security boundary: `win_workman_storage_path` holds secrets (the
  Veyon private keys among them), which anyone able to call `run_tasks` could
  otherwise push to every lab PC. An absolute `src`, a `..` segment, a symlink
  pointing outside, or any symlink inside a pushed directory fails the run before a
  host is touched.
- Host paths: the folder is read from `Explorer\User Shell Folders` of each user
  (`HKU\<SID>` if loaded, else `NTUSER.DAT` loaded for the occasion), with
  `%USERPROFILE%` expanded to that user's path, not the running account's. An unknown
  variable left in the value, or an unreadable hive, falls back to
  `<profile>\<Desktop|Documents|...>`. `reg.exe` writes to stderr when a hive is in
  use, which `Stop` would make terminating: it runs under `Continue`, judged by exit
  code.
- `push`: plain items through `win_copy` (checksums, only what differs). `archive`
  items are compared first; only the destinations that differ get the zip, built once
  on the controller and extracted with overwrite. Neither deletes files present on the
  host but not on the controller. Use `archive` for directories with many small files.
- `status`: size first, SHA1 only when sizes match.
- `remove`: the file, the directory, or for a `dir/` source the top-level entries as
  they are on the controller now. A destination relative to a profile folder is
  removed once empty, up to but never including the profile folder; an absolute one
  always stays.
- `pull`: files fetched one by one, so a second pull transfers only what changed;
  `archive` zips on the host, entry by entry with `/` separators
  (`ZipFile.CreateFromDirectory` on .NET Framework writes backslashes, which unzip
  turns into file names) and is always transferred again. Names coming from the host
  are trusted less: any that could climb out of the pull root fails the run.
- Known issue (P2): `pull` of large directories without `archive` can lose files on a
  transient SSH outage without saying which, and its loop output grows with the square
  of the file count (a 1700-file pull logged ~380 MB). See
  [file-copy-pull](../../todo/file-copy-pull.md); use `archive` meanwhile.
