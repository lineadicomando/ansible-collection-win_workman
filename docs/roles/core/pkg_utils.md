# Role: pkg_utils

> **Work in progress** — preliminary draft.

Low-level package operations shared by all software roles. Not called directly
by playbooks — schema roles delegate to it via `include_role tasks_from: pkg_workflow`.

---

## Package schema format

Each software role exposes a `win_workman_<schema>_schema` variable in
`vars/main.yaml` with the following structure:

```yaml
win_workman_<schema>_schema:
  name: "Human-readable name"

  package:
    setup_file: installer.exe       # filename expected in storage/remote_tmp
    searchName: "Registry display name"
    version: "1.2.3"
    provider: registry              # registry | portable
    install_args:
      - /VERYSILENT
    uninstall_args:
      - /VERYSILENT
    uninstall_before_upgrade: false # uninstall old version before installing new

  files:                            # list of downloadable assets
    - filename: installer.exe
      url: https://…
      checksum: sha256:…
      extract: 7z                   # optional: extract after download
      dest_dir: SubDir              # optional: destination under portable_path

  shortcuts:                        # optional: shortcuts to create/remove
    - description: "App Name"
      dest: "%PUBLIC%\\Desktop\\App.lnk"
      target: "C:\\Program Files\\App\\app.exe"
```

For the difference between `registry` and `portable` providers see
[architecture.md](../architecture.md#package-providers).

---

## Actions (`pkg_workflow`)

| Action | Task file | Description |
|---|---|---|
| `on` | `pkg_act_on` | Install or upgrade |
| `off` | `pkg_act_off` | Uninstall |
| `download` | `pkg_act_download` → `download` | Download to `win_workman_storage_path` |
| `copy` | `pkg_act_copy` | Copy from storage to remote temp |
| `info` | `pkg_act_info` | Report installation state |
| `is_present` | `pkg_act_is_present` | Assert package is installed |

---

## Key variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_storage_path` | `~/win_workman_storage` | Controller-side installer storage |
| `win_workman_remote_tmp` | `C:\Windows\Temp\ansible` | Temp dir on target |
| `win_workman_portable_path` | `C:\PortableApps` | Root for portable apps |
| `win_workman_restart` | `true` | Allow reboot after install if needed |
| `win_workman_restart_timeout` | `180` | Seconds to wait after reboot |
| `win_workman_default_lang` | `en_US` | Locale hint for multi-locale roles |

### Available actions list

`pkg_utils` also exposes `win_workman_pkg_actions` (defined in `vars/main.yaml`)
as the canonical list of valid action strings. Schema roles can use it for
validation or branching.

---

## Calling pkg_utils from a schema role

```yaml
# roles/myrole/tasks/main.yaml
- name: Run package workflow
  ansible.builtin.include_role:
    name: lineadicomando.win_workman.pkg_utils
    tasks_from: pkg_workflow
  vars:
    win_workman_schema: "{{ win_workman_myrole_schema }}"
```
