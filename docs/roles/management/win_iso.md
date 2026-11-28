# win_iso — Unattended Windows installation ISO

Builds on the controller, from a Microsoft ISO in the storage, an ISO whose Setup runs
unattended, creates the local administrator Ansible uses for the target host, and leaves
the PC answering on SSH from its first boot, before anyone logs on. The Microsoft ISO is
downloaded by hand: the download page hands out a 24-hour link no script can obtain, and
building the release from Windows Update packages would need DISM to integrate them.

What the output adds to the Microsoft ISO:

- **only the chosen editions** (default Home, Pro, Education, Pro Education): a PC with a
  key in the firmware installs its own edition, and the menu stays short;
- **`autounattend.xml`**: language, time zone, no Microsoft account or network in OOBE,
  TPM/Secure Boot/RAM checks lifted, no automatic BitLocker, the local administrator;
- **OpenSSH Server**, PowerShell as its shell, port 22 open on every profile, the
  controller's key in `administrators_authorized_keys` (ACL by SID: group names are
  localised), set up by a script running as SYSTEM in the specialize pass;
- **the remote temporary directory** (`win_workman_remote_tmp`, and `ansible_remote_tmp`
  when different) with the ACL the dispatcher expects, SYSTEM and Administrators only
  ([pkg_utils](../core/pkg_utils.md#remote-temporary-directory));
- **hibernation off**, so fast startup does not turn a shutdown into hibernation, which
  makes Wake-on-LAN and disk maintenance less reliable;
- **no leftover OOBE account**: OOBE works as `defaultuser0`, a passwordless local
  administrator Windows deletes only at the first interactive logon, which a PC managed
  over SSH may never see. A SYSTEM task (at boot and every 5 minutes) removes the account
  and its profile, clears the Winlogon automatic sign-in OOBE left for it (otherwise
  every boot shows "Nome utente o password non corretta"), then removes itself. It acts
  only after OOBE has signed `defaultuser0` in and out again (profile present, unloaded,
  no process), on two runs in a row: `OOBEInProgress`, `SystemSetupInProgress` and
  `ImageState` reach their final values while OOBE still runs, and deleting the account
  then stops OOBE with "Si è verificato un errore - REBOOT". Log
  `C:\Windows\Temp\win_workman-defaultuser0.log`.

## Actions

| Action | Does |
|---|---|
| `build[-msi\|dism\|none]` *(default)* | build the ISO; the argument (wins over `win_workman_win_iso_ssh`) picks how OpenSSH gets there |
| `on` | alias for `build` |
| `info` | without a source, list the ISOs in the root; with one, its editions and those `build` keeps; changes nothing |

| SSH mode | OpenSSH Server |
|---|---|
| `msi` *(default)* | the Win32-OpenSSH MSI of the `openssh` role (`roles/openssh/vars/main/msi.yaml`), downloaded into the storage, verified, carried on the ISO and installed during Setup. Only the controller is involved; Windows Update never updates it, `openssh-update` does |
| `dism` | the Windows capability, added to every edition by DISM on the target host; Windows Update keeps it updated |
| `none` | no SSH: the answer file and the other settings only |

## How it runs

Everything runs on the controller except DISM. A run targets **exactly one host**
(checked): its `ansible_user`/`ansible_password` become the account Setup creates, so
the ISO belongs to that host's lab; with `dism` it is also the PC running DISM. With
`msi` or `none` nothing connects to it, so it may be off.

```bash
ansible-playbook lineadicomando.win_workman.win_workman -l PC01 \
  -e '{"todo": "win_iso-build", "win_workman_win_iso_source": "Win11_25H2_Italian_x64.iso"}'

ansible-playbook lineadicomando.win_workman.win_workman -l PC01 \
  -e '{"todo": "win_iso-build-dism",
       "win_workman_win_iso_source": "Win11_25H2_Italian_x64.iso",
       "win_workman_win_iso_fod_source": "26100.1.240331-1435.ge_release_amd64fre_CLIENT_LOF_PACKAGES_OEM.iso"}'
```

1. extract the source into a private directory under `win_workman_win_iso_work_dir`
   (default: the folder of the output);
2. keep the chosen editions with `wimlib-imagex export` (an `install.esd` becomes a
   recompressed `install.wim`: slow);
3. `dism`: copy `install.wim` and the package to the host; per edition, as a separate
   async task, `/Mount-Image`, `/Add-Package`, `/Unmount-Image /Commit`; fetch it back;
4. write answer file and setup script, add the MSI (`msi`) and the key;
5. pack with `genisoimage` (UDF, BIOS and UEFI boot) and move into place, mode `0600`.

The private directory holds the password in clear and is removed at the end whatever
happens; with `dism` the host's working folder too, after discarding any mounted image.
A run killed outright (SIGKILL, power loss) cannot remove it: if the output folder is
shared or collected as is, point `win_workman_win_iso_work_dir` to a private folder on
the same file system, so the output is only renamed into place.

**DISM variant.** `OpenSSH-Server-Package~31bf3856ad364e35~amd64~~.cab` comes from the
**Languages and Optional Features ISO** (downloaded by hand, `win_workman_win_iso_fod_source`)
of the image's servicing branch: 24H2, 25H2 and 26H2 are all 26100 (`10.0.26100.x`), so
one Features ISO serves the three. Until the first cumulative, `sshd` stays at that ISO's
version. Only the package goes into the image; start type, shell, firewall and key come
from the same setup script, minus `msiexec`. The host needs free space for `install.wim`
(6–8 GB) plus `win_workman_win_iso_dism_min_free_gib` (about 40 GB in all), checked before
copying. When the host's build is older than the image the role warns and goes on. The
WIM travels over SSH both ways and each edition takes minutes: fewer editions, shorter
run.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_win_iso_root` | `{{ win_workman_storage_path }}/win_iso` | controller folder of the ISOs |
| `win_workman_win_iso_source` | `""` | Microsoft ISO, relative to the root or absolute; required by `build` |
| `win_workman_win_iso_output` | `""` | output ISO; empty: `<source>-unattended.iso` |
| `win_workman_win_iso_work_dir` | `""` | absolute folder of the private build directory (about twice the ISO); empty: the output's folder |
| `win_workman_win_iso_ssh` | `msi` | `msi`, `dism`, `none`; a task argument wins |
| `win_workman_win_iso_fod_source` | `""` | `dism`: the Features ISO, relative to the root or absolute |
| `win_workman_win_iso_dism_dir` | `C:\win_iso` | `dism`: working folder on the host |
| `win_workman_win_iso_dism_min_free_gib` | `30` | `dism`: free GiB needed beyond `install.wim` |
| `win_workman_win_iso_dism_timeout` | `3600` | `dism`: seconds per edition |
| `win_workman_win_iso_editions` | `[Core, Professional, Education, ProfessionalEducation]` | editions kept (edition ID, name or index); empty keeps all |
| `win_workman_win_iso_image` | `""` | edition installed without asking (index in the output, name or ID); empty: Setup asks or uses the firmware key's |
| `win_workman_win_iso_product_key` | `""` | key for PCs without one in the firmware |
| `win_workman_win_iso_wipe_disk` | `false` | erase disk 0 without asking |
| `win_workman_win_iso_bypass_requirements` | `true` | lift the TPM, Secure Boot and RAM checks |
| `win_workman_win_iso_prevent_bitlocker` | `true` | no automatic device encryption |
| `win_workman_win_iso_computer_name` | `*` | `*` is random |
| `win_workman_win_iso_setup_language` | `""` | Setup and UI language; empty: the ISO's |
| `win_workman_win_iso_locale` / `_input_locale` / `_timezone` | `it-IT` / `0410:00000410` / `W. Europe Standard Time` | locale, keyboard, time zone |
| `win_workman_win_iso_organization` | `win_workman` | registered organisation |
| `win_workman_win_iso_user` / `_password` | `{{ ansible_user }}` / `{{ ansible_password }}` | local administrator created by Setup |
| `win_workman_win_iso_authorized_key_file` | `{{ ansible_ssh_pub_key_path \| default('') }}` | public key installed when the file exists |

## Notes

- Controller: `7z`, `genisoimage`, `wimlib-imagex` (Fedora `dnf install 7zip genisoimage
  wimlib-utils`; Debian `apt install 7zip genisoimage wimtools`), twice the ISO free in
  the work directory; with `msi`, GitHub reachable the first time.
- The ISO holds the password in clear in `autounattend.xml`: keep it and the sticks made
  from it away from students. `wipe_disk: true` also means a PC booting from a forgotten
  stick reinstalls itself.
- Rufus: leave its customisations unticked (they replace the answer file); Ventoy works.
- On the PC the setup script logs to `C:\Windows\Temp\win_workman-setup.log` (MSI log
  `win_workman-setup-msi.log`) and leaves `win_workman-setup.done` or `.failed`. A failure
  does not stop Setup: it shows as no SSH.
- SSH answers while OOBE still runs (about 7 minutes after Setup starts in a VM): wait for
  the logon screen before restarting the PC or running long tasks, or OOBE is interrupted.
