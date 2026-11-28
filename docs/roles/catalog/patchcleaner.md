# patchcleaner — PatchCleaner

Installs PatchCleaner, the tool that finds orphaned `.msi`/`.msp` files in
`C:\Windows\Installer`; the role only installs it, it does not clean anything.
The vendor ships an `.exe` wrapper: `on` extracts `PatchCleaner.msi` from it with 7-Zip
and installs that (`msi` provider, `/qn /norestart`).
