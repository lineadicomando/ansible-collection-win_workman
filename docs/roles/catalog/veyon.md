# Role: veyon

Manages the [Veyon](https://veyon.io/) classroom management agent on Windows
workstations. Handles installation, RSA key-pair management, authentication
configuration, and network object reconciliation for master (teacher) and
agent (student) machines.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install Veyon via the standard package workflow |
| `off` | Uninstall Veyon |
| `config` | Configure keys and network objects (does not install) |
| `download` | Download installer only |
| `info` | Report installation state |

An upgrade uninstalls the previous release first (`uninstall_before_upgrade`)
and then deletes `%ProgramFiles%\Veyon` (`cleanup_paths`), as `off` does.
Normally there is nothing left to delete: the Veyon uninstaller removes the whole
directory, unknown and read-only files included. It cannot remove files that a
running process holds open, and an installer laid over those mixes two releases:
4.10.0 → 4.11.2 left stale DLLs that failed every binary with `0xC0000139` and
took the service down. With `cleanup_paths` the same situation stops the run at
the cleanup step, with Veyon uninstalled and the locked file named in the error.
Close whatever holds it (typically a Veyon Master left open) and run `veyon`
again. Configuration (registry) and keys (`%ProgramData%\Veyon`) are outside the
directory and survive both the upgrade and `off`.

---

## Master vs agent distinction

The `config` action behaves differently depending on whether the target host
is a **master** (teacher station) or an **agent** (student/lab workstation).
The distinction is controlled exclusively by `win_workman_veyon_master`:

| `win_workman_veyon_master` | Key imported | Role in topology |
|---|---|---|
| `false` (default) | Public key | Agent (student workstation) |
| `true` | Private key | Master (teacher station) |

Setting `win_workman_veyon_master: true` on a host also enables network object
reconciliation when `win_workman_veyon_labs` is non-empty.

---

## Variables

### Installation

| Variable | Default | Description |
|---|---|---|
| `win_workman_veyon_keypairs_dir` | `{{ win_workman_storage_path }}/veyon` | Controller path where RSA key pairs are stored |
| `win_workman_veyon_remote_key_dir` | `{{ win_workman_remote_tmp }}\veyon\keys` | Temp path on the Windows target for key staging |
| `win_workman_veyon_no_log` | `true` | Suppress logging of key material |
| `win_workman_veyon_cli_path` | *(auto-detected)* | Explicit path to `veyon-cli.exe`; auto-detected if unset |

### Role in topology

| Variable | Default | Description |
|---|---|---|
| `win_workman_veyon_master` | `false` | `true` → import private key (teacher); `false` → import public key (student) |

### Lab network objects (master only)

| Variable | Default | Description |
|---|---|---|
| `win_workman_veyon_labs` | `[]` | List of inventory group names to configure as Veyon network object locations |
| `win_workman_veyon_lab_force_replace` | `false` | Remove and recreate the location entry before importing, instead of reconciling in place |

Network object reconciliation runs on master hosts only when
`win_workman_veyon_labs` is non-empty. Each group listed becomes a location
in Veyon; every non-master host in the group is added as a computer. The
hosts in those groups must have `ansible_host` (IP/FQDN) and `ansible_mac`
(MAC address) set in their inventory variables.

---

## Usage examples

```yaml
# Install Veyon on all hosts
win_workman_tasks:
  - veyon-on

# Configure as agent (student workstation) — master is false by default
win_workman_tasks:
  - veyon-config

# group_vars/students/vars.yaml — no extra variable needed
# (win_workman_veyon_master defaults to false)
```

```yaml
# Configure as master (teacher station) with lab network objects
win_workman_tasks:
  - veyon-config

# group_vars/teachers/vars.yaml
win_workman_veyon_master: true
win_workman_veyon_labs:
  - lab_students        # inventory group whose hosts become network objects
```

```yaml
# inventory/host_vars/pc01.yaml — required for lab hosts
ansible_host: 192.168.1.101
ansible_mac: "aa:bb:cc:dd:ee:01"
```

---

## What config does, step by step

1. **Generate keypair on controller** (once, idempotent) — RSA 2048-bit key
   pair stored under `win_workman_veyon_keypairs_dir/{private,public}/key.pem`.
2. **Stage keys on target** — copies the appropriate key (public for agents,
   private for masters) to `win_workman_veyon_remote_key_dir`.
3. **Set authentication method** — configures Veyon to use key-based
   authentication via `veyon-cli config set`.
4. **Import key** — fingerprint-compares the staged key against the installed
   key; imports only if absent or mismatched.
5. **Reconcile network objects** (master only, when `win_workman_veyon_labs`
   is set) — exports the current location from Veyon, diffs against the
   inventory, and imports the desired state.
6. **Clean up** — removes staged key files from the Windows target.
