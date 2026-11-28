# vivaldi — Vivaldi

Vivaldi, 64-bit system-level install (`registry` provider) with the Chromium
mini-installer.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_vivaldi_shortcuts` | `false` | Create the Public Desktop and Start Menu shortcuts |
| `win_workman_vivaldi_shortcut_url` | `""` | URL appended to the shortcut arguments |
| `win_workman_vivaldi_shortcut_no_first_run` | `true` | Add `--no-default-browser-check --no-first-run` to the shortcut |

## Notes

- Silent system-wide install needs `--vivaldi-silent --do-not-launch-chrome
  --system-level`; NSIS-style flags (`/silent /allusers`) are accepted by the outer
  wrapper but not forwarded correctly to the inner `setup.exe`.
- Uninstall runs through `uninstall_via_helper` with `--force-uninstall`: the
  uninstaller returns rc 19 in non-interactive sessions even on success, so
  `uninstall_valid_rc` is `[0, 19]`. `vivaldi.exe` is killed first, and
  `%ProgramFiles%\Vivaldi` is deleted afterwards (`cleanup_paths`).
