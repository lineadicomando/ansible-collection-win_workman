# p7zip — 7-Zip

7-Zip, official MSI (`msi` provider). 64-bit by default; the task argument `32bit`
selects the x86 MSI, installed under `%ProgramFiles(x86)%`.

## Actions

| Action | Does |
|---|---|
| `on-32bit`, `off-32bit`, ... | Any standard action takes `32bit` to pick the x86 MSI and its install directory: `p7zip-on-32bit` |

## Notes

- `off` also deletes the install directory of the selected architecture
  (`cleanup_paths`).
- `searchName` is `7-Zip *`, so it matches the 64-bit and the 32-bit entries alike:
  the `32bit` token does not change what `info` and `off` find.
