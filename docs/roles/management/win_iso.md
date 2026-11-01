# Role: win_iso

Builds, on the controller, a Windows installation ISO ready for Ansible from a
Microsoft ISO kept in the storage. Setup then runs unattended, creates the local
administrator Ansible uses for the target host, and the PC answers on SSH from
its first boot, before anyone logs on.

The Microsoft ISO is downloaded by hand: the Microsoft download page hands out a
link valid for 24 hours that cannot be obtained by a script, and building the
same release from Windows Update packages needs DISM to integrate the updates.

What the output ISO adds to the Microsoft one:

- **only the chosen editions** (by default Home, Pro, Education and Pro
  Education), so a PC with a key in the firmware installs its own edition and the
  edition menu stays short;
- **an answer file** (`autounattend.xml`): language, time zone, no Microsoft
  account or network in OOBE, the TPM, Secure Boot and RAM checks lifted, no
  automatic BitLocker encryption, the local administrator;
- **OpenSSH Server**, with PowerShell as its shell, port 22 open on every
  profile and the controller's key in `administrators_authorized_keys`, set up
  by a script that runs as SYSTEM in the specialize pass.

---

## Actions

| Action | Description |
|---|---|
| `build` | Build the ISO *(default action)* |
| `info` | List the ISOs in the root, or the editions of the source and those `build` keeps. Changes nothing |
| `on` | Alias for `build` |

`build` takes an argument choosing how OpenSSH Server gets on the PCs, which
wins over `win_workman_win_iso_ssh`:

| Task | OpenSSH Server |
|---|---|
| `win_iso-build-msi` *(default)* | The Win32-OpenSSH MSI, carried on the ISO and installed during Setup. Nothing but the controller is involved; Windows Update does not update it afterwards |
| `win_iso-build-dism` | The Windows capability, added to every edition of the image by DISM on the target host. Windows Update keeps it updated like any other component |
| `win_iso-build-none` | No SSH: the answer file and the other settings only |

---

## How it runs

Everything happens on the controller (`delegate_to: localhost`), except DISM.
A run targets **exactly one host**, which plays two parts:

- its `ansible_user` and `ansible_password` become the account created by
  Setup, so running it against a host of another inventory makes the ISO of
  that lab;
- with `dism` it is the Windows PC that runs DISM. With `msi` or `none` nothing
  connects to it (the playbook has `gather_facts: false`), so it may be off.

```bash
# MSI, credentials of the lab of host01
ansible-playbook lineadicomando.win_workman.win_workman -l host01 \
  -e '{"t": "win_iso-build", "win_workman_win_iso_source": "Win11_25H2_Italian_x64.iso"}'

# Capability integrated by DISM on a Windows host
ansible-playbook lineadicomando.win_workman.win_workman -l teacher \
  -e '{"t": "win_iso-build-dism",
       "win_workman_win_iso_source": "Win11_25H2_Italian_x64.iso",
       "win_workman_win_iso_fod_source": "26100.1.240331-1435.ge_release_amd64fre_CLIENT_LOF_PACKAGES_OEM.iso"}'
```

Steps of `build`:

1. extract the source ISO into a private directory next to the output;
2. keep the chosen editions with `wimlib-imagex export` (an `install.esd` is
   converted to `install.wim` here, recompressed, which is slow);
3. with `dism`: copy `install.wim` and the OpenSSH Server package to the host,
   then for each edition `/Mount-Image`, `/Add-Package`, `/Unmount-Image
   /Commit`, and fetch `install.wim` back;
4. write the answer file and the setup script, add the MSI (`msi`) and the key;
5. pack the ISO with `genisoimage` (UDF, BIOS and UEFI boot) and move it in
   place, mode `0600`.

The private directory, which holds the password in clear, is removed at the end
whatever happens; with `dism` the working folder on the host is removed too,
after discarding any image left mounted.

---

## The DISM variant

The OpenSSH Server package (`OpenSSH-Server-Package~31bf3856ad364e35~amd64~~.cab`)
comes from the **Languages and Optional Features ISO**, downloaded by hand like
the Windows ISO and named by `win_workman_win_iso_fod_source`. It must belong to
the servicing branch of the image: 24H2, 25H2 and 26H2 are all branch 26100
(their packages are `10.0.26100.x`), so the 26100 Features ISO serves all three.
Until the first cumulative update, `sshd` stays at the version of that ISO.

Only the package goes into the image. The service start type, the default
shell, the firewall rule and the key are set by the same setup script as with
the MSI, minus `msiexec`.

The host needs about 40 GB free on the drive of `win_workman_win_iso_dism_dir`:
`install.wim` (6–8 GB) plus the space to mount an edition. The role checks it
before copying. DISM services an image best from the same build or a newer one;
when the host is older than the image the role warns and goes on.

`install.wim` travels to the host and back over SSH, and each edition takes a
few minutes: fewer editions mean a shorter run. Each edition is a separate
async task, so the SSH session does not have to stay busy for the whole job.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_win_iso_root` | `{{ win_workman_storage_path }}/win_iso` | Controller folder of the ISOs |
| `win_workman_win_iso_source` | `""` | The Microsoft ISO, relative to the root or absolute. Required by `build` |
| `win_workman_win_iso_output` | `""` | Output ISO, relative to the root or absolute. Empty: `<source>-unattended.iso` |
| `win_workman_win_iso_ssh` | `msi` | `msi`, `dism` or `none`; a task argument wins |
| `win_workman_win_iso_fod_source` | `""` | `dism`: the Languages and Optional Features ISO, relative to the root or absolute |
| `win_workman_win_iso_dism_dir` | `C:\win_iso` | `dism`: working folder on the host, removed at the end |
| `win_workman_win_iso_dism_min_free_gib` | `30` | `dism`: free space needed beyond the size of `install.wim` |
| `win_workman_win_iso_dism_timeout` | `3600` | `dism`: seconds allowed to each edition |
| `win_workman_win_iso_editions` | `[Core, Professional, Education, ProfessionalEducation]` | Editions kept, by edition ID, name or index of the source. Empty keeps all |
| `win_workman_win_iso_image` | `""` | Edition installed without asking: index in the output, name or edition ID. Empty: Setup asks, or uses the edition of the key in the firmware |
| `win_workman_win_iso_product_key` | `""` | Product key, for PCs without one in the firmware |
| `win_workman_win_iso_wipe_disk` | `false` | Erase disk 0 without asking |
| `win_workman_win_iso_bypass_requirements` | `true` | Lift the TPM, Secure Boot and RAM checks |
| `win_workman_win_iso_prevent_bitlocker` | `true` | No automatic device encryption |
| `win_workman_win_iso_computer_name` | `*` | Computer name; `*` is random |
| `win_workman_win_iso_setup_language` | `""` | Language of Setup and of the UI. Empty: the one of the ISO |
| `win_workman_win_iso_locale` | `it-IT` | System and user locale |
| `win_workman_win_iso_input_locale` | `0410:00000410` | Keyboard |
| `win_workman_win_iso_timezone` | `W. Europe Standard Time` | Time zone |
| `win_workman_win_iso_organization` | `win_workman` | Registered organisation |
| `win_workman_win_iso_user` | `{{ ansible_user }}` | Local administrator created by Setup |
| `win_workman_win_iso_password` | `{{ ansible_password }}` | Its password |
| `win_workman_win_iso_authorized_key_file` | `{{ ansible_ssh_pub_key_path }}` | Public key for `administrators_authorized_keys`, when the file exists |

---

## Requirements and cautions

- Controller: `7z`, `genisoimage`, `wimlib-imagex` (Fedora: `dnf install 7zip
  genisoimage wimlib-utils`; Debian: `apt install 7zip genisoimage wimtools`),
  and twice the size of the ISO free next to the output. With `msi`, network
  access to GitHub the first time: the MSI is downloaded into the storage by
  `pkg_utils/download` and verified against its sha256.
- The ISO holds the account password in clear in `autounattend.xml`: it is
  written readable by its owner only. Keep it, and the USB sticks made from it,
  out of reach of students.
- `win_workman_win_iso_wipe_disk: true` also means that a PC booting from a
  forgotten stick reinstalls itself.
- Write the ISO to a stick with Rufus leaving its customisations unticked (they
  would replace the answer file), or copy it to a Ventoy stick.
- On the installed PC the setup script logs to
  `C:\Windows\Temp\win_workman-setup.log` and leaves `win_workman-setup.done`
  or `.failed` next to it. A failure does not stop Setup: it shows as no SSH.
