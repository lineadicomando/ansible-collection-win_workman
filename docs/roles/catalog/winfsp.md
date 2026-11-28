# winfsp — WinFsp

WinFsp (Windows File System Proxy), MSI (`registry` provider), set up here for
virtiofs shares on KVM/QEMU guests: `on` installs [`virtiogt`](virtiogt.md) first and
sets the `VirtioFsSvc` service (from the guest tools) to automatic and started.

## Notes

- The role is for virtual machines: on a physical PC `winfsp` also installs the VirtIO
  guest tools, and `VirtioFsSvc` has no virtiofs device to serve.
- WinFsp names its entry after the release year (`WinFsp 20xx`): `searchName` is
  `WinFsp 20*`.
