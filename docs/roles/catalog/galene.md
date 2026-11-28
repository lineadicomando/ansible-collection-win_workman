# galene — Galène teacher screen broadcast

Broadcasts the teacher's screen and system audio to the students' PCs with
[Galène](https://galene.org/), a WebRTC videoconference server (MIT). The **master**
(the teacher PC) runs Galène as a Windows service; the **clients** (the students' PCs)
only get a desktop shortcut that opens the master's room in an Edge app window. Not a
`pkg_utils` package: the role has its own actions only (no `download`, `copy`,
`is_present`, `usr`).

## Actions

| Action | Does |
|---|---|
| `on` *(default)* | Master: build if needed, install the service, open the firewall, write group and tokens, add the teacher shortcut. Client: add the shortcut to the master |
| `off` | Remove service, firewall rules, `win_workman_galene_install_dir` and both shortcuts; the same on master and client |
| `info` | Check without changing anything (below) |
| `build` | Only download the source and WinSW and build `galene.exe` on the controller |

A host is the master with the `master` argument (`galene-on-master`,
`galene-info-master`) or `win_workman_galene_master: true`; any other host is a client.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_galene_master` | `false` | This host is the master (same as the `master` argument) |
| `win_workman_galene_master_host` | first host of `teachers` | Inventory host the client shortcuts point to (its `ansible_host`, else its name) |
| `win_workman_galene_clients_group` | `students` | Group whose hosts get a token on the master |
| `win_workman_galene_group` | `lab` | Galène group (room) |
| `win_workman_galene_group_display_name` | `Ascolto docente` | Room title shown in the client |
| `win_workman_galene_max_clients` | `60` | Maximum clients in the room |
| `win_workman_galene_master_username` | `Docente` | Name the master joins with |
| `win_workman_galene_http_port` | `8443` | TCP port of the web server |
| `win_workman_galene_udp_port` | `8444` | One UDP port for all the media (ICE UDP mux) |
| `win_workman_galene_install_dir` | `C:\Program Files\Galene` | Install directory on the master |
| `win_workman_galene_service_name` | `Galene` | Service name |
| `win_workman_galene_firewall_remoteip` | `LocalSubnet` | Remote addresses allowed: `LocalSubnet`, `Any` or a list |
| `win_workman_galene_firewall_profiles` | `[domain, private, public]` | Firewall profiles of the rules |
| `win_workman_galene_secret_file` | `{{ win_workman_storage_path }}/galene/<inventory>_secret` | Controller file of the token secret |
| `win_workman_galene_token_expires` | `2099-12-31T23:59:59Z` | Token expiry |
| `win_workman_galene_browser` | Edge (`Program Files (x86)`) | Browser the shortcuts open |
| `win_workman_galene_master_shortcut` / `_client_shortcut` | `Ascolto docente - Trasmetti` / `Ascolto docente` | Shortcut names on the Public Desktop, without `.lnk`; `*_description` for their comments |

## Notes

### Master and client

| | Master | Client |
|---|---|---|
| Files | `galene.exe`, `static\`, `groups\<group>.json`, `data\var\tokens.jsonl`, `VERSION`, WinSW wrapper and its XML, `logs\` | none |
| Service | `Galene`, automatic, LocalSystem, restarted by WinSW 10 s after a crash | — |
| Firewall | `Galene HTTP (win_workman)` TCP and `Galene media (win_workman)` UDP | — |
| Shortcut | Edge `--new-window http://localhost:<port>/group/<group>/?token=…` | Edge `--app=http://<master>:<port>/group/<group>/?token=…` |

The master must be the teacher PC. The teacher opens `http://localhost`, which
browsers treat as a secure context, so screen and audio sharing work over plain HTTP
(`-insecure`) without a certificate. In the sharing dialog choose the whole screen and
*Share system audio*. The clients only receive, which needs no secure context. A
master on another PC would need HTTPS with a certificate the teacher's browser trusts,
and the role does not manage that. `-turn ""` disables the built-in TURN server.

Set `win_workman_galene_master_host` in the group_vars of labs without a `teachers`
group: a client fails when it is empty or names the client itself.

### Access tokens

Nobody types a user name or password: each shortcut carries a token, the first 32 hex
digits of SHA-256 of the secret plus `-master` or the host name. The secret is kept on
the controller (one per inventory, 40 characters, created on first use, `run_once` so
parallel hosts cannot create two), so tokens are the same on every run:

- the master's token has `op`, `present` and `message` and joins as
  `win_workman_galene_master_username`;
- each host of `win_workman_galene_clients_group` gets its own token with no
  permissions, so it can only watch and listen, and joins with its host name, which
  the teacher sees in the user list.

The token file on the master lists the clients known to the inventory: **after adding a
client, run `galene-on-master` again**. `info` reports a token count that does not
match the inventory. Galène reloads the token and group files without restarting.

On the client the *Connect* button is still there: that click is the user gesture that
lets the browser play the audio.

### Build

Upstream publishes the source only. `galene.exe` is cross-compiled on the controller,
once per version, into `{{ win_workman_storage_path }}/galene/<version>/` together with
the web client (`static/`) and the licence:

```
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 GOTOOLCHAIN=<pinned> GOFLAGS=-mod=readonly
go build -trimpath -buildvcs=false -ldflags='-s -w'
```

The controller needs Go, any version from 1.21 (`dnf install golang`,
`apt install golang-go`): Go downloads the pinned toolchain itself. `GOPROXY` and
`GOSUMDB` are set explicitly because some distributions default to `GOPROXY=direct`,
with which neither the toolchain nor the modules resolve. With the toolchain pinned
the build is reproducible, so the role pins the sha256 of `galene.exe` as it does for
any installer, and the build fails if the result differs. The source tarball and WinSW
are downloaded and checked like any other package file.

Galène does not implement the Service Control Manager protocol, so it runs under
[WinSW](https://github.com/winsw/winsw) 2.12.0 (MIT), copied next to it as
`galene-service.exe` with its configuration in `galene-service.xml`. WinSW writes
Galène's output to `logs\`.

Upgrade: bump `win_workman_galene_version`, the source checksum and
`win_workman_galene_exe_checksum` together in `vars/main.yaml`; the build prints the
new checksum when it differs from the pinned one. On the master `on` stops the service
only when `galene.exe` has to be replaced (a running one is locked), and restarts it
when the binary or the service configuration changed.

### `info`

On the master, one result with an `issues` list (empty when all is well):

- service installed, `Running`, start mode `Auto`;
- `galene.exe` running, listening on the TCP port and bound to the UDP port;
- `http://localhost:<port>/` answering 200;
- both firewall rules present, enabled, allowing, with their ports, profiles and
  remote addresses;
- no enabled inbound **block** rule on `galene.exe` (the firewall prompt leaves one
  when a standard user dismisses it, and a block rule wins over any allow rule; `on`
  removes them and the "Query User" rules, as `nodejs26` does for `node.exe`);
- installed version (`VERSION`) against the role's version;
- number of tokens against the clients in the inventory;
- link speed against the bandwidth the clients need.

On a client: the shortcut exists and points to the expected URL, and the master
answers on its TCP port within 3 s.

### Bandwidth

Galène is a selective forwarding unit: it sends one copy of the stream to each client.
At about 2.5 Mbit/s per client, 30 students need about 75 Mbit/s from the teacher PC,
at the limit of a 100 Mbit/s port. `info` warns when the estimate exceeds 80% of the
fastest active link.
