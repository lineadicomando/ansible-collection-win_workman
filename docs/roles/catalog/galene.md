# Role: galene

Broadcasts the teacher's screen and system audio to the students' PCs with
[Galène](https://galene.org/), a WebRTC videoconference server (MIT). The
**master** (the teacher PC) runs Galène as a Windows service; the **clients**
(the students' PCs) only get a desktop shortcut that opens the master's room in
an Edge app window. Nothing is installed on the clients.

---

## Actions

| Action | Description |
|---|---|
| `on` *(default)* | Master: build if needed, install the service, open the firewall, write group and tokens, add the teacher shortcut. Client: add the shortcut to the master |
| `off` | Remove service, firewall rules, `C:\Program Files\Galene` and both shortcuts; the same on master and client |
| `info` | Check without changing anything (below) |
| `build` | Only download the source and WinSW and build `galene.exe` on the controller |

```yaml
# Teacher PC
- galene-on-master          # or win_workman_galene_master: true in host_vars, then just "galene"
# Student PCs
- galene
# Checks
- galene-info-master        # on the teacher
- galene-info               # on the students
```

---

## Master and client

| | Master | Client |
|---|---|---|
| Selected by | the `master` task argument or `win_workman_galene_master: true` | any other host |
| Files | `C:\Program Files\Galene`: `galene.exe`, `static\`, `groups\`, `data\var\tokens.jsonl`, WinSW wrapper and its XML, `logs\` | none |
| Service | `Galene`, automatic, LocalSystem, restarted by WinSW 10 s after a crash | — |
| Firewall | `Galene HTTP (win_workman)` TCP 8443 and `Galene media (win_workman)` UDP 8444, from `LocalSubnet` | — |
| Shortcut (`%PUBLIC%\Desktop`) | *Ascolto docente - Trasmetti*: Edge on `http://localhost:8443/group/lab/?token=…` | *Ascolto docente*: Edge `--app=http://<master>:8443/group/lab/?token=…` |

The master must be the teacher PC. The teacher opens `http://localhost`, which
browsers treat as a secure context, so screen and audio sharing work over plain
HTTP (`-insecure`) without a certificate. In the sharing dialog choose the whole
screen and *Share system audio*. The clients only receive, which needs no secure
context. A master on another PC would need HTTPS with a certificate the
teacher's browser trusts, and the role does not manage that.

The client URL uses the master's `ansible_host`. The master is
`win_workman_galene_master_host`, by default the first host of `teachers`; set
it in the group_vars of labs without that group.

### Access tokens

Nobody types a user name or password: each shortcut carries a token. The
tokens are derived from a secret kept on the controller
(`win_workman_galene_secret_file`, one per inventory, created on first use), so
they are the same on every run:

- the master's token has `op`, `present` and `message` and joins as
  `win_workman_galene_master_username`;
- each host of `win_workman_galene_clients_group` gets its own token with no
  permissions, so it can only watch and listen, and joins with its host name,
  which the teacher sees in the user list.

The token file on the master lists the clients known to the inventory: **after
adding a client, run `galene-on-master` again**. `info` reports a token count
that does not match the inventory. Galène reloads the file without restarting.

On the client the *Connect* button is still there: that click is the user
gesture that lets the browser play the audio.

---

## Build

Upstream publishes the source only. `galene.exe` is cross-compiled on the
controller, once per version, into `{{ win_workman_storage_path }}/galene/<version>/`
together with the web client (`static/`) and the licence:

```
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 GOTOOLCHAIN=<pinned>
go build -trimpath -buildvcs=false -ldflags='-s -w'
```

The controller needs Go, any version from 1.21 (`dnf install golang`,
`apt install golang-go`): Go downloads the pinned toolchain itself. With the
toolchain pinned the build is reproducible, so the role pins the sha256 of
`galene.exe` as it does for any installer, and the build fails if the result
differs. The source tarball and WinSW are downloaded and checked like any other
package file.

Galène does not implement the Service Control Manager protocol, so it runs
under [WinSW](https://github.com/winsw/winsw) 2.12.0 (MIT), copied next to it as
`galene-service.exe` with its configuration in `galene-service.xml`. WinSW
writes Galène's output to `logs\`.

### Upgrade

Bump `win_workman_galene_version`, the source checksum and
`win_workman_galene_exe_checksum` together in `vars/main.yaml`; the build prints
the new checksum when it differs from the pinned one. On the master `on` stops
the service only when `galene.exe` has to be replaced, and restarts it when the
binary or the service configuration changed.

---

## `info`

On the master, one result with an `issues` list (empty when all is well):

- service installed, `Running`, start mode `Auto`;
- `galene.exe` running, listening on the TCP port and bound to the UDP port;
- `http://localhost:<port>/` answering 200;
- both firewall rules present, enabled, allowing, with their ports, profiles and
  remote addresses;
- no enabled inbound **block** rule on `galene.exe` (the firewall prompt leaves
  one when a standard user dismisses it, and a block rule wins over any allow
  rule; `on` removes them);
- installed version against the role's version;
- number of tokens against the clients in the inventory;
- link speed against the bandwidth the clients need.

On a client: the shortcut exists and points to the expected URL, and the master
answers on its TCP port.

---

## Bandwidth

Galène is a selective forwarding unit: it sends one copy of the stream to each
client. At about 2.5 Mbit/s per client, 30 students need about 75 Mbit/s from
the teacher PC, at the limit of a 100 Mbit/s port. `info` warns when the
estimate exceeds 80% of the fastest active link.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_galene_master` | `false` | This host is the master (same as the `master` task argument) |
| `win_workman_galene_master_host` | first host of `teachers` | Inventory host the client shortcuts point to |
| `win_workman_galene_clients_group` | `students` | Group whose hosts get a token on the master |
| `win_workman_galene_group` | `lab` | Galène group (room) |
| `win_workman_galene_group_display_name` | `Ascolto docente` | Room title shown in the client |
| `win_workman_galene_max_clients` | `60` | Maximum clients in the room |
| `win_workman_galene_master_username` | `Docente` | Name the master joins with |
| `win_workman_galene_http_port` | `8443` | TCP port of the web server |
| `win_workman_galene_udp_port` | `8444` | UDP port for all the media |
| `win_workman_galene_install_dir` | `C:\Program Files\Galene` | Install directory on the master |
| `win_workman_galene_service_name` | `Galene` | Service name |
| `win_workman_galene_firewall_remoteip` | `LocalSubnet` | Remote addresses allowed: `LocalSubnet`, `Any` or a list |
| `win_workman_galene_firewall_profiles` | `[domain, private, public]` | Firewall profiles of the rules |
| `win_workman_galene_secret_file` | `{{ win_workman_storage_path }}/galene/<inventory>_secret` | Controller file of the token secret |
| `win_workman_galene_token_expires` | `2099-12-31T23:59:59Z` | Token expiry |
| `win_workman_galene_browser` | Edge | Browser the shortcuts open |
| `win_workman_galene_master_shortcut` / `_client_shortcut` | `Ascolto docente - Trasmetti` / `Ascolto docente` | Shortcut names, without `.lnk` |

---

## Schema details

Software name: `Galène`  
Provider: custom (built on the controller, run by WinSW)  
Version: `1.2.2`, built with `go1.26.11`  
Files: `galene-1.2.2.tar.gz` (source), `WinSW-2.12.0.NET461.exe`  
Homepage: https://galene.org
