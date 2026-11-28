# zed — Zed

Zed ships only a per-user Inno Setup installer (`PrivilegesRequired=lowest`, no
override): run elevated it still installs into the calling user's profile. The schema
therefore has a `usr` block and no `package` block, and supports only the per-user
deferred install: each target gets Zed in their own profile at their next logon.

## Actions

| Action | Does |
|---|---|
| `usr-<verb>[-<targets>]` *(default `usr-on`)* | Standard per-user verbs, see [pkg_utils](../core/pkg_utils.md#per-user-deferred-install-usr) |
| `download` | Standard |

Every other action (`on`, `off`, `info`, `copy`, …) fails and points to
`zed-usr-on`. Targets are joined by `+` (`zed-usr-off-teacher-carol`); without them
`usr-on` uses `win_workman_usr_targets` (default `BUILTIN\Users`).

## Notes

- Installs to `%LOCALAPPDATA%\Programs\Zed`, adds `bin` to the user PATH and, on
  Windows 11, registers a sparse Appx package for the Explorer context menu; all of
  these work from the logon task, and the uninstaller removes them.
- Zed updates itself inside each profile. The agent never downgrades, so a user ahead
  of the role's version is left as is.
- The release asset keeps the same name at every version (`Zed-x86_64.exe`): the
  versioned `filename` keeps the controller cache and the staged payload apart.
