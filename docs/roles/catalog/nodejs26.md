# Role: nodejs26

> **Work in progress** — preliminary draft.

Manages Node.js 26 LTS ("Lithium") with npm, machine-wide, from the official MSI.
One role per LTS major line: when a new line becomes LTS, a new role is added
(`nodejs27`, …) and this one stays until its end of life, 2029-04-30.

---

## Actions

| Action | Description |
|---|---|
| `on` | Make Node.js 26 the version on the host: remove any other Node.js, install or upgrade 26, set the PowerShell execution policy |
| `on-nodep` | Same, without touching the execution policy |
| `off` | Uninstall Node.js 26; another major line, if present, is left alone |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state of Node.js 26 |
| `is_present` | Assert that Node.js 26 is installed |

---

## One major line per host

Every Node.js MSI has `DisplayName` "Node.js" and the same `UpgradeCode`, so two
major lines cannot be installed together. The schema sets
`version_like: "26.*"` and `exclusive: true` (see
[pkg_utils](../core/pkg_utils.md#one-role-per-major-line-version_like-exclusive)):
`nodejs26-on` removes a Node.js 24 or 27 first, and `nodejs26-off` removes only 26.
Moving a lab from one line to the next is changing the role name in its task
list; moving back works the same way. Never list two `nodejs*` roles for the same
hosts: they would replace each other at every run.

---

## Configuration

- **Features** (`ADDLOCAL`): `NodeRuntime`, `npm`, `EnvironmentPath`,
  `EnvironmentPathNode`. Left out:
  - `EnvironmentPathNpmModules`, which adds `%APPDATA%\npm` to the PATH of the
    account running the install only: global npm packages (`npm i -g`) are not
    on the users' PATH; `npx` works.
  - `DocumentationShortcuts`.
- **PATH**: `%ProgramFiles%\nodejs` in the system PATH.
- **Execution policy**: `on` runs [`ps_policy-on`](../management/ps_policy.md)
  first. npm and npx come with `.ps1` shims, which PowerShell prefers to the
  `.cmd` ones and the Windows client default `Restricted` refuses to run
  ("running scripts is disabled on this system"). `off` does not reset the
  policy, which other tools may rely on.
- Corepack is no longer shipped from Node.js 25 on.

No user-configurable variables; `ps_policy`'s own variables apply.

---

## Changing major line

A new major breaks the native modules (`.node` files) that projects compiled for
the previous one: `require()` fails with "was compiled against a different
Node.js version using NODE_MODULE_VERSION". Modules built on Node-API are not
affected. The remedy is `npm rebuild`, or deleting `node_modules` and running
`npm install`; it works when the package publishes prebuilt binaries for the new
major, since the hosts have no C++ build tools. Change line between school years,
and tell the teachers.

---

## Schema details

Software name: `Node.js 26`  
Provider: MSI (`registry` detection)  
Installer: `node-v26.13.0-x64.msi`  
Homepage: https://nodejs.org/

---

## Notes

- Installation location: `%ProgramFiles%\nodejs`, removed by `off`
- Start menu: "Node.js", "Node.js command prompt", "Install Additional Tools for
  Node.js" (needs an administrator), "Uninstall Node.js"
- Release schedule: https://github.com/nodejs/Release — from Node.js 27 every
  major becomes LTS each October
