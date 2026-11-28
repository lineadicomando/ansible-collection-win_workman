# laragon — Laragon

Laragon (WAMP edition), machine-wide from the Inno Setup installer with `/ALLUSERS`
and a desktop icon (`/MERGETASKS=desktopicon`), `registry` provider. No variables.

## Notes

- `searchName` embeds the short version (`Laragon <short_version>`, both versions set
  at the top of `vars/main.yaml`): `info` and `off` recognise only the release the
  role pins, so an older Laragon reads as absent. `on` then runs the installer anyway,
  which upgrades in place: every release has the same Inno AppId (`Laragon_is1`).
