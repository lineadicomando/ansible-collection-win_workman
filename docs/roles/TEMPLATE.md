# Role page template

One page per role in `docs/roles/{catalog,management,core}/<role>.md`. A page holds
what the code does not say at a glance: what the role is for, the actions and
variables a user chooses between, and the behaviour that surprised someone. It does
not repeat what has one home elsewhere:

- the standard package actions (`on`, `off`, `info`, `download`, `copy`,
  `shortcuts`, `is_present`, `usr-*`): [architecture](../architecture.md#actions);
- the installer filename, version, URL and checksum: `roles/<role>/vars/main.yaml`,
  which changes at every bump;
- the manifest the MCP server reads: `roles/<role>/meta/mcp.yaml` (keep its actions
  and defaults in step with the page).

Omit a section that would be empty. No "Work in progress" banner: a page is either
checked against the role or fixed.

```markdown
# <role> — <Software or purpose>

<One to three sentences: what it installs or manages, provider (`registry` or
`portable`) for a package, anything a user must know before running it.>

## Actions

<Package roles: only the actions beyond the standard ones, or a standard one the
role reimplements. Management roles: all of them, default marked.>

| Action | Does |
|---|---|
| `<action>[-<arg>]` | ... |

## Variables

<From `defaults/main.yaml`; computed ones in `vars/` only when a user must know them.>

| Variable | Default | Meaning |
|---|---|---|
| `win_workman_<role>_<name>` | `...` | ... |

## Notes

- <Why the role does something non-obvious; traps already paid for; how to test it.>
```
