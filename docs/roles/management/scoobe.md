# scoobe — "Let's finish setting up your device"

Suppresses SCOOBE ("Second Chance OOBE"), the full-screen page Windows 11 shows at
logon after a cumulative or feature update ("Let's finish setting up your device",
Italian "La configurazione del PC è quasi completata"), with OneDrive, Outlook,
Copilot and Phone Link promotions that students must dismiss before using the PC. Not
the first-boot OOBE: that is the [`oobe`](system-tools.md#oobe) role.

## Actions

| Action | Does |
|---|---|
| `info` (default) | Report the three values in every profile, read-only |
| `off` | Write the values that suppress the page into every profile and the Default profile |
| `on` | Remove those values: Windows' default behaviour |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_scoobe_profiles_include_default` | `true` (inline default, no `defaults/`) | Also write the Default profile, template for accounts created later |

## Notes

- The values (`win_workman_scoobe_entries` in `vars/main.yaml`), all under HKCU:

  | Key | Value | `off` writes | Settings equivalent |
  |---|---|---|---|
  | `Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement` | `ScoobeSystemSettingEnabled` | `0` | Notifications > Suggest ways to finish setting up my device |
  | `Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager` | `SubscribedContent-310093Enabled` | `0` | Notifications > Show the Windows welcome experience after updates |
  | `Software\Policies\Microsoft\Windows\CloudContent` | `DisableWindowsSpotlightWindowsWelcomeExperience` | `1` | User policy "Turn off the Windows Welcome Experience" |

- Per user because the machine-wide `HKLM\...\CloudContent\DisableWindowsConsumerFeatures`
  is honoured on Enterprise and Education only.
- Profiles: every non-special `Win32_UserProfile` with SID `S-1-5-21-*` (local or
  domain) plus Default. A hive already loaded (logged-on user, SSH user) is written in
  place, the others loaded from `NTUSER.DAT` and unloaded. No logoff, no reboot:
  Windows reads the values when deciding whether to show the page at the next logon.
  A hive held by another process is reported `unavailable`.
- Domain users who never logged on get the values from the Default profile.
- Open: that `off` keeps the page away after a real cumulative update is not yet
  confirmed on a lab PC, see [management](../../todo/management.md).
