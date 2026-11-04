# Role: scoobe

Suppresses SCOOBE ("Second Chance OOBE"), the full-screen page Windows 11 shows
at logon after a cumulative or a feature update: "Let's finish setting up your
device" (Italian: "La configurazione del PC è quasi completata"), with OneDrive,
Outlook, Copilot and Phone Link promotions and the buttons *Continue* /
*Remind me in 3 days*. Students have to dismiss it before using the PC.

It is not the first-boot OOBE: that is the [`oobe`](system-tools.md#oobe) role.

---

## Actions

| Action | Description |
|---|---|
| `info` *(default)* | Report the three values in every profile, read-only |
| `off` | Write the values that suppress the page into every profile and the Default profile |
| `on` | Remove those values, giving Windows back its default behaviour |

---

## Registry values

All per user (HKCU), because the machine-wide switch,
`HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent\DisableWindowsConsumerFeatures`,
is honoured on Enterprise and Education only.

| Key under HKCU | Value | `off` writes | Settings equivalent |
|---|---|---|---|
| `Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement` | `ScoobeSystemSettingEnabled` | `0` | System → Notifications → *Suggest ways to finish setting up my device* |
| `Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager` | `SubscribedContent-310093Enabled` | `0` | System → Notifications → *Show the Windows welcome experience after updates* |
| `Software\Policies\Microsoft\Windows\CloudContent` | `DisableWindowsSpotlightWindowsWelcomeExperience` | `1` | User policy *Turn off the Windows Welcome Experience* |

The list is `win_workman_scoobe_entries` in `vars/main.yaml`.

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_scoobe_profiles_include_default` | `true` | Also write the Default profile, template for accounts created later |

---

## How profiles are reached

Every non-special local or domain profile (`Win32_UserProfile`, SID
`S-1-5-21-*`) plus the Default profile. A hive already loaded under `HKU\<SID>`
(the logged-on user, the SSH user) is written in place; the others are loaded
from `NTUSER.DAT` under a temporary name and unloaded afterwards. No logoff and
no reboot: Windows reads the values when it decides whether to show the page at
the next logon. A hive held by another process is reported as `unavailable`.

Domain users who have never logged on to the PC get the values from the Default
profile when their profile is created.

---

## Examples

```bash
# Suppress on the whole lab
ansible-playbook lineadicomando.win_workman.win_workman -i <inventory> -l win_managed -e t=scoobe-off

# Check what each profile has
ansible-playbook lineadicomando.win_workman.win_workman -i <inventory> -l student01 -e t=scoobe-info
```
