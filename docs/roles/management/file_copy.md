# Role: file_copy

Copies files and folders between the controller and the hosts, in both
directions: material handed out to a lab (exercises on every student's Desktop,
a dataset in `C:\Lab`), backups and collected work brought back.

It adds three things to a bare `win_copy`/`fetch`:

- **per-user folders**: a destination can be "the Desktop of `docente`" or "the
  Documents of every profile" instead of a path; the folder is read from the
  user's own registry, so a Desktop redirected to OneDrive is followed;
- **one interface for both directions**, `status` and `remove`, so what was
  handed out can be checked and taken back with the same item list;
- **a confined source**: a push can only read below its own controller folder.

---

## Actions

| Action | Description |
|---|---|
| `push` | Copy the items from the controller to the host *(default action)* |
| `pull` | Fetch the items from the host to the controller |
| `status` | Compare each destination with the controller copy, change nothing |
| `remove` | Delete from the host what `push` created |
| `on` | Alias for `push` |
| `off` | Alias for `remove` |

---

## Items

Everything is described by `win_workman_file_copy_items`, a list of dicts (a
single dict is accepted too). The same item list serves `push`, `status` and
`remove`; `pull` reads `src` and `dest` the other way round.

| Field | push / status / remove | pull |
|---|---|---|
| `src` | Controller path relative to `win_workman_file_copy_root`. A trailing `/` copies the **contents** of a directory, without the directory itself | Host path: absolute, or relative to the profile folder when `profile` is set |
| `dest` | Host folder that receives `src`: absolute, or relative to the profile folder when `profile` is set | Controller subfolder of `win_workman_file_copy_pull_root` (optional) |
| `profile` | A profile name, a list of names, a wildcard (`stud*`) or `all`. `DOMAIN\name` patterns work as in `pkg_utils/profiles` | same |
| `folder` | Profile folder the relative path starts from: `desktop` *(default)*, `documents`, `downloads`, `pictures`, `music`, `videos`, `profile` (the profile root) | same |
| `include_default` | Also the Default profile, so users created later find the files | same |
| `archive` | Transfer a directory as a single zip | Fetch a directory as `<name>.zip` |

Without `profile`, the host path must be absolute (`C:\Lab\Dati`). With
`profile`, it must be relative and may not contain `..`.

A profile named explicitly that does not exist on a host fails that host with
the list of its profiles. A wildcard that matches nothing is not an error, and
skips the profiles in `win_workman_file_copy_profiles_exclude`.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_file_copy_items` | `[]` | The items, see above |
| `win_workman_file_copy_root` | `{{ win_workman_storage_path }}/file_copy` | Controller folder push sources are relative to |
| `win_workman_file_copy_pull_root` | `{{ win_workman_storage_path }}/file_copy_pull` | Controller folder pull writes to |
| `win_workman_file_copy_profiles_exclude` | `[]` | Profiles skipped by wildcards and `all`, e.g. `[maint, admin]` |

---

## Usage

```yaml
# Exercises on every student's Desktop, also for users created later
win_workman_file_copy_items:
  - src: esercizi/verifica_3B/        # contents of the folder...
    profile: all
    dest: Verifica                    # ...into Desktop\Verifica
    include_default: true
win_workman_file_copy_profiles_exclude: [maint, admin]
win_workman_tasks:
  - file_copy-push

# Same items, other actions
win_workman_tasks:
  - file_copy-status    # who has the current version
  - file_copy-remove    # take it back after the test
```

```yaml
# Collect the work: <pull_root>/verifica_3B/<host>/<profile>/Verifica.zip
win_workman_file_copy_items:
  - src: Verifica
    profile: all
    dest: verifica_3B
    archive: true
win_workman_tasks:
  - file_copy-pull
```

Through the MCP server, the items go in `extra_vars`:

```
run_tasks(t=["file_copy-push"], l="DOC", inventory="spalla_info1",
          extra_vars={"win_workman_file_copy_items": [
            {"src": "backup_mysql/", "profile": "docente", "dest": "Backup"}]})
```

---

## How it works

### The controller side

`push`, `status` and `remove` start with the `file_copy_manifest` lookup
plugin, which reads every `src` once for the whole play (`run_once`): the list
of files with their path on the host, size and SHA1, and the top-level names
`remove` deletes. The items are therefore expected to be the same for every
host of the run, as they are when passed as extra vars.

The lookup is also the security boundary. `win_workman_storage_path` holds
secrets — the Veyon private keys among them — and anyone able to call
`run_tasks` could otherwise push them to every lab PC. So every `src` must
resolve inside `win_workman_file_copy_root`, a dedicated folder: an absolute
path, a `..` segment, a symbolic link pointing outside, or a symbolic link
anywhere inside a pushed directory fails the run before any host is touched.

### Resolving the host paths

`pkg_utils/profiles` lists the profiles; the role then reads each user's
`Explorer\User Shell Folders` value for the requested folder — from `HKU\<SID>`
when the hive is loaded, from `NTUSER.DAT` mounted for the occasion otherwise —
and expands `%USERPROFILE%` to that user's profile path, not to the account
running the task. A value that still holds an unknown variable, or a hive that
cannot be opened, falls back to `<profile>\<Desktop|Documents|...>`.

No logoff is needed: the role only reads the registry and writes files.

### push

Plain items go through `win_copy`, which compares checksums and sends only what
differs. `archive` items are compared first (`status` logic); only the hosts
and profiles whose files differ receive the zip, built once on the controller,
extracted in place with overwrite. Neither path deletes files that exist on the
host but not on the controller.

### status

Size first, SHA1 when the size matches. Each destination is `match`, `differ`
(some files missing or different, with counts) or `missing` (none there). The
result is also published as the `win_workman_file_copy_status` fact.

### remove

Deletes the file, the directory, or — for a `dir/` source — the top-level
entries of that directory as they are on the controller now. A destination
relative to a profile folder is removed too once empty, up to but never
including the profile folder; an absolute destination is always left in place.

### pull

Writes to `<pull_root>/<dest>/<host>/[<profile>/]<name>`. Files are fetched one
by one, so a second pull only transfers what changed; `archive` zips the
directory on the host (entry names with `/`, readable by any unzip) and fetches
one file, which is always transferred again. A source missing on a host is
reported, not an error: a student may simply not have saved the file.

The relative names come from the host, which is trusted less than the
controller: any name that could climb out of the pull root fails the run.
