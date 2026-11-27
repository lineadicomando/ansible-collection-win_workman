# TODO

Backlog of the `lineadicomando.win_workman` collection. This file is the index: one
row per entry, with what to do next. The full entry (cause, evidence, what to change,
how to test) is in the linked file under `docs/todo/`; open only the one you work on.

Every entry was re-checked against the tree on 2026-11-15 at `22ec497` (earlier checks:
2026-09-28, 2026-10-01, 2026-10-31). When an entry is done, delete its row and its
section; when you touch one, update its **Status** line with the date.

- **P1** — affects the labs in production or is a correctness bug; do next.
- **P2** — merged or written code that has never been exercised; do before relying on it.
- **P3** — improvements, refactoring, work that waits on something else.

| P | Entry | File | Next step |
|---|---|---|---|
| P1 | Kill declared processes before install | [package-workflow](docs/todo/package-workflow.md) | `kill_processes:` schema field in `pkg_utils`, then fold the role-local kills into it |
| P1 | `wu`: a feature update that does not apply is reported as installed | [wu-feature-update](docs/todo/wu-feature-update.md) | Compare build before/after each round; stop retrying and report it as failed |
| P1 | `lock-off` leaves the logon screen without the user list until a restart | [lock-off](docs/todo/lock-off.md) | In `act_off`/`act_reset`, restart the logon screen of sessions with no user when `DontDisplayLastUserName` changed (candidates in the entry) |
| P1 | `sfc`: repairs are reported as "no integrity violation" | [sfc](docs/todo/sfc.md) | Parse repaired / pending-reboot lines of CBS.log; report them and `RestartRequired` |
| P1/P3 | AutoCAD: end-to-end validation on a real host (P1 only before a rollout) | [autocad](docs/todo/autocad.md) | `autocadlt2026-on`, `autocadlt2023-off-full`, `autocadlt2026-off-full` on a real host |
| P2 | Verify the upgrade path of the `uninstall_before_upgrade` roles | [package-workflow](docs/todo/package-workflow.md) | Upgrade from the previous release on a VM: postman, winscp, inkscape, putty, mysql_server (veyon done) |
| P2 | `ansible_user` read without a default: warning in `ping` under cockpit-fleet (`--user`), possible failure in `openssh`, `win_iso` | [ansible-user](docs/todo/ansible-user.md) | Default in `ping`'s task name; `AllowUsers` from the connected user or a clear failure; assert in `win_iso` |
| P2 | `pkg_act_off` does not stop declared services | [package-workflow](docs/todo/package-workflow.md) | Call `services_stop` in `pkg_act_off` as `pkg_act_on` does |
| P2 | Remote tmp ACL: exercise the paths not run yet | [package-workflow](docs/todo/package-workflow.md) | One `wu` optional-update run, one `win_iso` build |
| P2 | `openssh-update`: first run on a production host | [openssh](docs/todo/openssh.md) | At the next Win32-OpenSSH release: VM, one PC, then the lab |
| P2 | `usr`: test a version upgrade | [usr](docs/todo/usr.md) | Bump `zed` and run `tests/usr_zed.yaml` over an older install |
| P2 | `file_copy-pull`: large directories lose files and flood the output | [file-copy-pull](docs/todo/file-copy-pull.md) | Slim the loop items, retry fetch, list missing files |
| P2 | Audit the catalog drafts | [documentation](docs/todo/documentation.md) | Check the 45 + 7 draft pages against the roles, drop the banner where earned |
| P3 | Wait mode for the helper uninstall in `pkg_act_off` | [package-workflow](docs/todo/package-workflow.md) | Only when a hang is observed |
| P3 | veyon `config`: a crashing `veyon-cli` export reads as a missing key | [package-workflow](docs/todo/package-workflow.md) | Check the exported file, not `$LASTEXITCODE`, in `import_keys.yaml`; only if a 4.10.x lab needs it |
| P3 | `version_file`: a program found only that way cannot be removed | [package-workflow](docs/todo/package-workflow.md) | No fix designed |
| P3 | `usr`: fewer round trips in `usr-on` | [usr](docs/todo/usr.md) | Fewer remote tasks: agent as a parameter with a hash check, no payload `win_file` (list in the entry) |
| P3 | `usr`: test several policies at once | [usr](docs/todo/usr.md) | Blocked on a second `usr` role |
| P3 | `usr`: a role with both scopes | [usr](docs/todo/usr.md) | When a dual-scope package is needed |
| P3 | `usr`: `usr-purge` with copies still installed | [usr](docs/todo/usr.md) | Refuse while profiles still hold the package; `win_workman_usr_purge_force` to override |
| P3 | `usr`: agent log rotation | [usr](docs/todo/usr.md) | Small; not urgent |
| P3 | `usr`: adopt more per-user packages | [usr](docs/todo/usr.md) | On demand |
| P3 | AutoCAD: promote `odis_uninstall` and `find_products` to `pkg_utils` | [autocad](docs/todo/autocad.md) | After the end-to-end validation |
| P3 | `autoshutdown`: implement the `nouser` mode | [management](docs/todo/management.md) | Session check on the host, inside the scheduled task |
| P3 | `optimize`: an analysis alone, without defragmenting HDDs | [management](docs/todo/management.md) | An action `optimize-analyze` (`Optimize-Volume -Analyze`), then the skills of win_edulab |
| P3 | `scoobe`: confirm that `off` keeps the page away after a cumulative | [management](docs/todo/management.md) | Observe a lab PC after the next cumulative update |
| P3 | `wim-repair`: the folder form of the source, only partly exercised | [management](docs/todo/management.md) | Document it as the way to repair cumulative payloads |
| P3 | `w32time`: a role for the Windows time service | [management](docs/todo/management.md) | Proposed role, design in the entry |
| P3 | `veyon`: manage the predefined applications and websites | [management](docs/todo/management.md) | Variables for both lists, written to the global configuration by `veyon-config` |
| P3 | Remove the `secure_ssh` alias | [openssh](docs/todo/openssh.md) | At the next release, with the variable fallbacks |
| P3 | Roles with no documentation at all | [documentation](docs/todo/documentation.md) | Pages for `googledrive`, `tinycad`, `winmerge`, `winrar` |
| P3 | `run_powershell`: `timeout` is ignored with `background=true` | [mcp-server](docs/todo/mcp-server.md) | Pass `timeout` to `start_run` (project repo `mcp/`) |
