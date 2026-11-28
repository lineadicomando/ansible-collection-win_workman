# veyon — Veyon

[Veyon](https://veyon.io/) classroom management, NSIS installer (`registry`
provider, `VeyonService` automatic and started). Agents (student PCs) get the service
only (`/NoMaster`); the master (teacher PC) also gets Veyon Master. `config` manages
the RSA key pair, key-file authentication and, on the master, the lab locations built
from the inventory.

## Actions

| Action | Does |
|---|---|
| `on[-master]` | Installs or upgrades; the Master component only with the `master` argument or `win_workman_veyon_master: true` |
| `config` | Key pair on the controller, key import, `Authentication/Method` key file, lab locations on the master (below); does not install |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_veyon_master` | `false` | Teacher station: install Master, import the private key, reconcile `win_workman_veyon_labs`; `false` imports the public key |
| `win_workman_veyon_labs` | `[]` | Master only: inventory groups that become Veyon locations, a group name or `{group, name}` |
| `win_workman_veyon_lab_force_replace` | `false` | Remove and recreate each location instead of reconciling it in place |
| `win_workman_veyon_lab_prune` | `false` | Also remove computers of the location that are not in the group (default: kept, reported as `unmanaged`) |
| `win_workman_veyon_keypairs_dir` | `{{ win_workman_storage_path }}/veyon` | Controller directory of `private/key.pem` and `public/key.pem`; its basename is also the Veyon key name (`veyon/private`, `veyon/public`) |
| `win_workman_veyon_remote_key_dir` | `{{ win_workman_remote_tmp }}\veyon\keys` | Staging directory on the target, emptied at the end |
| `win_workman_veyon_no_log` | `true` | Hide key material and fingerprints in the log |
| `win_workman_veyon_cli_path` | unset | Path of `veyon-cli.exe`; otherwise found on `PATH` or under `Program Files` |

## Notes

### Upgrade

An upgrade uninstalls the previous release first (`uninstall_before_upgrade`) and then
deletes `%ProgramFiles%\Veyon` (`cleanup_paths`), as `off` does. Normally there is
nothing left to delete: the Veyon uninstaller removes the whole directory, unknown and
read-only files included. It cannot remove files that a running process holds open,
and an installer laid over those mixes two releases: 4.10.0 → 4.11.2 left stale DLLs
that failed every binary with `0xC0000139` and took the service down. With
`cleanup_paths` the same situation stops the run at the cleanup step, with Veyon
uninstalled and the locked file named in the error. Close whatever holds it (typically
a Veyon Master left open) and run `veyon` again. Configuration (registry) and keys
(`%ProgramData%\Veyon`) are outside the directory and survive both the upgrade and
`off`.

Keep Veyon at 4.11.4 or later. Microsoft Defender platform 4.18.26090 (October 2026)
starts a protected `DefenderSessionHelper.exe` in every user session. Up to 4.11.3 the
service starts its feature workers from the first process of the session user, and
when that process is `DefenderSessionHelper.exe` it fails with
`WindowsCoreFunctions: OpenProcess() 5` (`0` in 4.8.x): text messages and starting
programs stop working, while screen lock and monitoring still do. Whether a host is hit
depends on the order in which the user's processes start, so it looks random across a
lab. Fixed upstream in 4.11.4 (veyon/veyon#1184, #1189, #1195).

### What `config` does

1. **Key pair on the controller** (`run_once`): RSA 2048 under
   `win_workman_veyon_keypairs_dir`, generated only when neither file exists; fails
   when only one exists (remove it to regenerate); checks that the two match.
2. **Stage** the public key (agent) or private key (master) on the target.
3. **Authentication method**: `veyon-cli config set Authentication/Method` to key
   file, unless already set.
4. **Import**: exports the installed key, compares SHA-256 fingerprints on the
   controller and deletes and re-imports only when missing or different.
5. **Lab locations** (master with `win_workman_veyon_labs` set), below.
6. **Clean up** the staged key files. A changed method, key or location restarts
   `VeyonService`.

The master/agent split in `config` follows `win_workman_veyon_master` only, not the
`master` task argument: set the variable on the teacher PC.

### Lab locations

Each group becomes a location; every host of the group that is not itself a master is
a computer, and must have `ansible_host` and `ansible_mac`. The run fails when a group
is missing or empty, has no agent host, or two entries share a location name.

A plain group name is also the name of the location. When the master already has the
lab under another name (created in the Configurator, say), give it explicitly, or the
role creates a second location named after the group:

```yaml
win_workman_veyon_labs:
  - group: win_managed
    name: Lab A
```

The location is reconciled field by field, not re-imported wholesale. Veyon derives
the UUID of an imported object from all its fields, and gives objects made in the
Configurator a random one, so a plain import would add a second computer with the same
name whenever its address changed, or next to one created by hand. Instead:

- a computer whose name, address and MAC match the inventory is kept as it is,
  whoever created it;
- a computer with an inventory name but another address or MAC, and any duplicate, is
  removed by UUID;
- the computers missing from the location are imported;
- a computer whose name is not in the group is left alone and reported as
  `unmanaged`, unless `win_workman_veyon_lab_prune` is true.

The run reports, per location, what it created, added, removed and left unmanaged. Two
locations with the same name on the master stop the run: fix them in the Configurator.
