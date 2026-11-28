# Changelog

Releases are the `v*` tags, made by `tools/release.sh`; what each contains is
`git log --oneline <previous-tag>..<tag>`. Only what a user must act on is noted here.

## Upgrade notes

- **v0.7.0** — `secure_ssh` became a deprecated alias of `openssh-harden` /
  `openssh-unharden`. Hosts hardened by `secure_ssh` before it need one
  `openssh-harden`: the old role never restarted sshd (so `PasswordAuthentication no`
  waited for the next reboot) and put `AllowUsers` inside `Match Group administrators`.
