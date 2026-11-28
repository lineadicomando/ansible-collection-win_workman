# nodejs26 — Node.js 26 LTS

Node.js 26 LTS ("Lithium") with npm, machine-wide from the official MSI, in
`%ProgramFiles%\nodejs` on the system PATH. One role per LTS major line: a new line
gets a new role (`nodejs27`, …) and this one stays until its end of life, 2029-04-30.

## Actions

| Action | Does |
|---|---|
| `on` | Make 26 the line on the host: run `ps_policy-on`, remove any other Node.js, install or upgrade 26, then the firewall rule if `win_workman_nodejs26_firewall` |
| `on-nodep` | Same, without `ps_policy-on` |
| `off` | Uninstall 26 only and always remove its firewall rule; another major line is left alone |

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_nodejs26_firewall` | `false` | On `on`, add the inbound rule for `node.exe` and remove the prompt and block rules |
| `win_workman_nodejs26_firewall_profiles` | `[domain, private, public]` | Profiles the rule applies to |
| `win_workman_nodejs26_firewall_remoteip` | `LocalSubnet` | Allowed sources: `LocalSubnet`, `Any`, or a list of addresses/ranges |

`ps_policy`'s own variables apply.

## Notes

- **One major line per host.** Every Node.js MSI has `DisplayName` "Node.js" and the
  same `UpgradeCode`, so two lines cannot coexist. The schema sets
  `version_like: "26.*"` and `exclusive: true`
  ([pkg_utils](../core/pkg_utils.md#one-role-per-major-line-version_like-exclusive)).
  Moving a lab to another line, in either direction, is changing the role name in its
  task list. Never list two `nodejs*` roles for the same hosts: they replace each
  other at every run.
- **Features** (`ADDLOCAL=NodeRuntime,npm,EnvironmentPath,EnvironmentPathNode`).
  Left out: `DocumentationShortcuts`, and `EnvironmentPathNpmModules`, which adds
  `%APPDATA%\npm` to the PATH of the installing account only: global npm packages
  (`npm i -g`) are not on the users' PATH; `npx` works. Corepack is not shipped from
  Node.js 25 on.
- **Execution policy.** npm and npx come with `.ps1` shims, which PowerShell prefers to
  the `.cmd` ones and the Windows client default `Restricted` refuses ("running
  scripts is disabled on this system"), hence [`ps_policy-on`](../management/ps_policy.md)
  (RemoteSigned, LocalMachine). `off` does not reset the policy, which other tools may
  rely on.
- **Firewall.** The first time `node.exe` listens, Windows turns the "has blocked some
  features of this app" prompt into inbound rules `TCP/UDP Query User{GUID}…\node.exe`.
  Dismissed by a student without admin rights they **block**, and a block rule wins
  over any allow: a dev server is then unreachable from the other PCs and the prompt
  never returns. Accepted by an admin they allow from **any** address, current profile
  only. With the variable true, `on` adds "Node.js 26 (win_workman)" (program
  `%ProgramFiles%\nodejs\node.exe`, any protocol and port, from the allowed sources) and
  removes from the local store the prompt rules on `node.exe`, block or allow, and any
  other inbound block rule on it. Allow rules added by hand under another name stay;
  GPO rules are not touched.
- The firewall step runs outside the package workflow, whose after-install hook fires
  only on install or upgrade: re-running `nodejs26-on` applies it to hosts that already
  have 26. A GPO with "Apply local firewall rules: No" makes Windows ignore the rule;
  Node.js installed elsewhere (nvm, portable) is not covered.
- **Changing major line** breaks native modules (`.node`) compiled for the previous
  one ("compiled against a different Node.js version using NODE_MODULE_VERSION");
  Node-API modules are fine. Remedy: `npm rebuild`, or delete `node_modules` and
  `npm install`; it works only when the package publishes prebuilt binaries, since
  the hosts have no C++ build tools. Change line between school years and tell the
  teachers.
- `off` also removes `%ProgramFiles%\nodejs` (`cleanup_paths`).
- Start Menu: "Node.js", "Node.js command prompt", "Install Additional Tools for
  Node.js" (needs an administrator), "Uninstall Node.js".
- From Node.js 27 every major becomes LTS each October
  ([schedule](https://github.com/nodejs/Release)).
