# How to Use Software Role Documentation Templates

This guide explains how to use the templates for documenting software roles in the collection.

---

## Quick Reference

| Template | When to Use | Examples |
|---|---|---|
| **TEMPLATE-software-simple.md** | Standard install/uninstall only, no custom actions | Python, VSCode, Brave, Gimp, Inkscape |
| **TEMPLATE-software-custom.md** | Has extra actions beyond on/off/download/info | Chrome (privacy-on, privacy-off, rm-profile), Firefox (same) |

---

## TEMPLATE-software-simple.md

Use this for software roles that:
- ✓ Support only standard `pkg_utils` actions: `on`, `off`, `download`, `copy`, `info`, `is_present`
- ✓ Have no special variables or flags
- ✓ Need minimal documentation (install/uninstall behavior)

### Placeholders to Replace

| Placeholder | Example | Notes |
|---|---|---|
| `{ROLE_NAME}` | `python312`, `vscode`, `gimp` | Matches role directory name |
| `{SOFTWARE_NAME}` | `Python 3.12`, `Visual Studio Code` | Full software name |
| `{ONE_LINE_DESCRIPTION}` | `Manages Python 3.12, a general-purpose programming language` | Concise description |
| `{PROVIDER_TYPE}` | `registry` (or `portable`, `msi`, `exe`) | From role `vars/main.yaml` → `package.provider` |
| `{INSTALLER_FILENAME}` | `python-3.12.8-amd64.exe` | From role `vars/main.yaml` → `package.setup_file` |
| `{HOMEPAGE_URL}` | `https://www.python.org/` | Upstream project link |
| `{NO_VARIABLES_IF_NONE_OR_TABLE}` | Delete section or list vars | If no variables, delete this section entirely |

### Example: Brave Browser

```markdown
# Role: brave

> **Work in progress** — preliminary draft.

Manages Brave Browser, a privacy-focused Chromium-based web browser.
Supports standard package operations: install, uninstall, download, and info queries.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Brave |
| `off` | Uninstall Brave |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Brave is installed |

---

## Variables

No variables. Brave is installed with default system-level configuration.

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - brave
  - brave-off
```

---

## Schema details

Software name: `Brave Browser`
Provider: `registry`
Installer: `brave_installer-x64.exe`
Homepage: https://brave.com/

---

## Notes

No special configuration or behavior.
```

---

## TEMPLATE-software-custom.md

Use this for software roles that:
- ✓ Have custom actions beyond standard `on`/`off`/`download`/`info`
- ✓ Custom feature explains the extra actions (e.g., privacy settings, data removal)
- ✓ May have configuration variables for shortcuts, URLs, modes

### Placeholders to Replace

| Placeholder | Example | Notes |
|---|---|---|
| `{ROLE_NAME}` | `chrome`, `firefox` | Matches role directory name |
| `{SOFTWARE_NAME}` | `Google Chrome`, `Mozilla Firefox` | Full software name |
| `{FULL_DESCRIPTION}` | `Manages Google Chrome (Enterprise MSI). Supports 32-bit and 64-bit variants, shortcut customisation, privacy policy enforcement, and user-data removal.` | Detailed, multi-sentence description |
| `{CUSTOM_FEATURE_BRIEF}` | `architecture selection, privacy policies, and user-data removal` | Brief summary of custom features |
| `{CUSTOM_ACTION_1}`, `{CUSTOM_ACTION_2}` | `privacy-on`, `privacy-off`, `rm-profile` | From role tasks |
| `{FEATURE_SECTION_TITLE}` | `Architecture selection`, `Locale detection`, `Privacy Policy` | Descriptive section title |
| `{DETAILED_EXPLANATION_OF_CUSTOM_FEATURE}` | Paragraph explaining how it works | ~5-10 sentences |
| `{PROVIDER_TYPE}`, `{INSTALLER_FILENAME}`, `{HOMEPAGE_URL}` | Same as simple template | From role vars |
| `{IMPLEMENTATION_NOTES}` | List of important behaviors | Any quirks, side effects, or requirements |

### Example: Chrome Browser

```markdown
# Role: chrome

> **Work in progress** — preliminary draft.

Manages Google Chrome (Enterprise MSI). Supports 32-bit and 64-bit variants,
shortcut customisation, privacy policy enforcement, and user-data removal.

---

## Actions

| Action | Description |
|---|---|
| `on` | Install or upgrade Chrome |
| `off` | Uninstall Chrome |
| `download` | Download installer to storage |
| `copy` | Copy installer to remote temp (no install) |
| `info` | Report installation state |
| `is_present` | Assert that Chrome is installed |
| `privacy-on` | Apply privacy Group Policy (disables telemetry, syncing, etc.) |
| `privacy-off` | Remove privacy Group Policy |
| `rm-profile` | Force-close Chrome and delete all user profile folders |

---

## Architecture Selection

The installer architecture is resolved from the task string argument:

| Task string | Architecture | Installer |
|---|---|---|
| `chrome-on` *(default)* | 64-bit | `googlechromestandaloneenterprise64.msi` |
| `chrome-on-32bit` | 32-bit | `googlechromestandaloneenterprise.msi` |

The token `32bit` must appear anywhere in the task string (position 2+).

---

## Variables

| Variable | Default | Description |
|---|---|---|
| `win_workman_chrome_shortcut_url` | `""` | URL appended to desktop shortcut arguments |
| `win_workman_chrome_shortcut_no_first_run` | `true` | Disables first-run prompts on shortcut launch |

Example:

```yaml
# group_vars/lab_pcs.yml
win_workman_tasks:
  - chrome-on-32bit
  - chrome-privacy-on
  - chrome-rm-profile
```

---

## Schema details

Software name: `Google Chrome`
Provider: `registry`
Installer: `googlechromestandaloneenterprise64.msi`
Homepage: https://www.google.com/chrome/

---

## Notes

- Before install and before uninstall, any running `chrome.exe` process is
  force-killed via a PowerShell pre-action script.
- `rm_data` removes `%LOCALAPPDATA%\Google\Chrome` for every local user profile.
- No checksum is defined for the installer: Chrome Enterprise is fetched
  directly from Google's CDN at the URL in `vars/main.yaml`.
```

---

## Workflow

1. **Identify the role**: Look at `roles/{role_name}/vars/main.yaml`
2. **Check for custom actions**: Read `roles/{role_name}/tasks/main.yaml` — if it only dispatches to `pkg_workflow`, use **simple template**; if it has `act_*` files, use **custom template**
3. **Gather metadata**:
   - Role name, software name, description
   - Provider type, installer filename, homepage
   - Custom actions (if any), variables, special behaviors
4. **Fill in the template** with gathered metadata
5. **Create the file**: Save as `docs/roles/{role_name}.md`
6. **Update docs/index.md**: Add link to the new documentation file in the appropriate category

---

## Common Patterns

### No Variables Section

If a software role has no configurable variables (like `geogebra`), delete the entire "Variables" section and replace with:

```markdown
## Configuration

No variables. {ROLE_NAME} is installed with default settings.
```

### Multiple Custom Actions

If there are 3+ custom actions, keep the Actions table but expand the Feature Sections. For example, Chrome has both architecture selection AND privacy, so it has two sections.

### Locale-Aware Software

If software detects system locale (like Firefox), create a dedicated section:

```markdown
## Locale Detection

Before running any action, the role queries the target host for its system
locale (`Get-WinSystemLocale`, `Get-SystemPreferredUILanguage`) and uses the
correct language-specific installer from the schema.

Set `win_workman_default_lang` explicitly to override auto-detection.
```

---

## Quick Validation Checklist

Before committing a new `.md` file:

- [ ] File is saved as `docs/roles/{role_name}.md`
- [ ] All placeholders are replaced with actual values
- [ ] Actions table matches role's `tasks/` structure
- [ ] Variables table matches role's `defaults/` or `vars/`
- [ ] Examples use correct task string syntax
- [ ] Homepage URL is valid and current
- [ ] No placeholder text remains (`{...}`)
- [ ] Markdown formatting is valid (test with `md` preview)
- [ ] File is added to `docs/index.md` in the appropriate category

---

## Questions?

- **How do I know if a role is "simple" or "custom"?** Look at `roles/{role_name}/tasks/` — if only `main.yaml` calls `pkg_workflow`, it's simple. If there are `act_*.yaml` files or multiple task includes, it's custom.
- **What if my role has very few variables?** That's fine — list them in the Variables section even if there's only one.
- **Can I add sections beyond the template?** Yes! If your role has unique behavior (like locale detection in Firefox), add a feature-specific section between Actions and Variables.
- **Should I document all actions from pkg_utils?** Yes — include the standard actions (`on`, `off`, `download`, `copy`, `info`, `is_present`) even if the user won't use all of them.
