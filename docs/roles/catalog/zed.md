# Role: zed

> **Work in progress** — preliminary draft.

Manages Zed, a fast code editor with built-in collaboration and AI features.
Zed ships only a per-user installer, so the role supports the per-user
deferred install scope (`usr`) alone: each targeted user gets Zed in their own
profile at their next logon.

---

## Actions

| Action | Description |
|---|---|
| `usr-on` *(default)* | Stage the installer and mark the targets present |
| `usr-off` | Mark the targets absent; they uninstall at next logon |
| `usr-info` | Policy and per-user installed version and last outcome |
| `usr-apply` | Install or uninstall now for users already logged on |
| `usr-purge` | Remove the policy and the staged installer |
| `download` | Download installer to storage |

Targets go after the verb, joined by `+`: `zed-usr-on-alunno1+mario-rossi`.
Without targets, `usr-on` applies to `win_workman_usr_targets` (default
`BUILTIN\Users`). `zed` alone means `zed-usr-on`. `zed-on`, `zed-off` and the other
machine-wide actions are refused: run elevated, the installer would still install
into the Ansible user's profile.

Full mechanism, rule resolution and variables: [pkg_utils](../core/pkg_utils.md#per-user-deferred-install-usr).

Example:

```yaml
# group_vars/lab_coding.yml
win_workman_tasks:
  - zed-usr-on                 # every user, at next logon
  - zed-usr-off-docente        # except this one
```

---

## Schema details

Software name: `Zed`  
Scope: `usr`  
Installer: `Zed-x86_64-1.19.2.exe` (Inno Setup, `PrivilegesRequired=lowest`)  
Homepage: https://zed.dev/

---

## Notes

- Installs to `%LOCALAPPDATA%\Programs\Zed`, adds `bin` to the user PATH, and on
  Windows 11 registers a sparse Appx package for the Explorer context menu; all
  of these work from the logon task, and the uninstaller removes them.
- Zed updates itself inside each profile. The agent never downgrades, so a user
  ahead of the role's version is left as is.
- On a version bump the release asset keeps its name (`Zed-x86_64.exe`): the
  versioned `filename` keeps the controller cache and the staged payload apart.
