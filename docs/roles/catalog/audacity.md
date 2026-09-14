# Role: audacity

> **Work in progress** — preliminary draft.

Manages Audacity, a free and open-source multi-track audio editor and recorder.
Supports standard package operations: install, uninstall, download, and info
queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Audacity |
| `off` | Uninstall Audacity |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Audacity is installed |

---

## Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `win_workman_audacity_superseded_searchnames` | list | `["Audacity 1*", "Audacity 2*", "Audacity 3*"]` | Registry `DisplayName` globs of the releases `on` uninstalls before installing |
| `win_workman_audacity_superseded_uninstall_args` | list | `[/VERYSILENT, /NORESTART, /SUPPRESSMSGBOXES]` | Silent switches passed to the Inno Setup uninstaller of those releases |

Otherwise Audacity is installed with default settings.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - audacity
  - audacity-off
```

---

## Schema details

Software name: `Audacity`  
Provider: `msi`  
Installer: `audacity-win-4.0.0-x86_64.msi`  
Homepage: https://www.audacityteam.org

---

## Notes

Audacity 4.0 is the first release of the new major line and the first shipped as an
MSI; 3.x and earlier are Inno Setup packages. Only the x86_64 package is covered —
upstream also publishes an arm64 MSI.

The MSI carries a WiX `MajorUpgrade`, so a newer 4.x build replaces the installed one
in place and `uninstall_before_upgrade` is not needed.

### Superseded releases

`searchName` is scoped to `Audacity 4*`, because the registry `DisplayName` is the MSI
`ProductName`, `Audacity 4.0`. The 4.x MSI also carries its own `UpgradeCode` and
supersedes only itself, so an Audacity 3.x install would survive the upgrade and the
two would sit side by side — the old one registered as `Audacity_is1` under
`C:\Program Files\Audacity`, the new one under `C:\Program Files\Audacity 4`.

`on` therefore removes them first: for every glob in
`win_workman_audacity_superseded_searchnames` it runs `pkg_utils/pkg_act_off` with a
throwaway schema, which detects the entry, reads its `UninstallString` and runs it
with the Inno Setup silent switches. A glob that matches nothing is a no-op, so the
action stays idempotent on a machine that only ever had 4.x.

The Inno uninstaller only deletes what it registered, so anything added to the install
tree afterwards survives it — bundled plug-ins carried over from an older release,
`mod-script-pipe.dll`, language files — and `pkg_utils`' own leftovers pass refuses, by
design, to remove a directory holding anything but `unins*`. The throwaway schema
therefore lists `%ProgramFiles%\Audacity` and `%ProgramFiles(x86)%\Audacity` as
`cleanup_paths`. That takes the whole directory: a Nyquist plug-in a teacher dropped in
by hand goes with it and has to be put back under the 4.x install tree. The cleanup runs
only when an uninstall actually happened, so a machine that never had a superseded
release is untouched.

When a 5.x line eventually supersedes this one, add `"Audacity 4*"` to that list.

Note that `off` removes only what `searchName` matches, so it uninstalls 4.x and
leaves an older release alone. Removing everything is a property of installing, not of
uninstalling.

The MSI creates the desktop and Start Menu shortcuts itself, so the schema declares
none — but it ships without an `ALLUSERS` property, so on its own it puts them in the
profile of whichever user runs the installer, which over SSH is the Ansible account and
not the people using the machine. The role therefore passes `ALLUSERS=1`, which moves
them to `%Public%\Desktop` and `%ProgramData%`. Verified on a lab VM: without the
argument the only shortcuts created were under `C:\Users\maint`.

The application lands in `%ProgramFiles%\Audacity 4\bin\Audacity4.exe`.
