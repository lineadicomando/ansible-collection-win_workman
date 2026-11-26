#!/usr/bin/env python3
"""Write the catalog of the roles for the skill win-workman of Fleet.

.fleet/skills/win-workman/ is a skill in the format of Claude's skills,
which cockpit-fleet gives its assistant from the collections a project
installs: SKILL.md, written by hand, says how task strings work; the
roles-*.md files beside it, written here from roles/*/meta/mcp.yaml by the
same code as the get_role_info tool of the MCP server, list every role
with its actions and variables. Run it after a change to a meta/mcp.yaml:

    python3 tools/fleet_skills.py           # write the files
    python3 tools/fleet_skills.py --check   # fail if they are not up to date

A file is kept under 60 kB, what Fleet reads of one (64 kB) with room to
spare: a family of roles larger than that is split.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp"))

from roles import get_role_info, list_roles  # noqa: E402

SKILL_DIR = ROOT / ".fleet" / "skills" / "win-workman"
LIMIT = 60 * 1024


def _one_line(text) -> str:
    return " ".join(str(text or "").split())


def render(role: str) -> str:
    info = get_role_info(role)
    lines = [f"### {role}: {_one_line(info.get('display_name', role))}", ""]
    common = info.get("common_actions") or []
    if common:
        names = []
        for action in common:
            name = f"`{action['name']}`" + (" (default)" if action.get("default") else "")
            names.append(name)
        lines.append("Common actions: " + ", ".join(names) + ".")
        for action in common:
            if action.get("handled_by") not in (None, "pkg_utils") and action.get("description"):
                lines.append(f"- `{role}-{action['name']}`: {_one_line(action['description'])}")
    if info.get("install_scopes") and info["install_scopes"] != ["sys"]:
        lines.append("Install scopes: " + ", ".join(info["install_scopes"]) + ".")
    for action in info.get("custom_actions") or []:
        if isinstance(action, dict):
            lines.append(f"- `{role}-{action.get('name')}`: {_one_line(action.get('description'))}")
        else:
            lines.append(f"- `{role}-{action}`")
    defaults = info.get("defaults") or []
    if defaults:
        lines.append("Variables:")
        for item in defaults:
            if not isinstance(item, dict):
                continue
            kind = item.get("type", "")
            default = item.get("default")
            told = f" (default `{default}`)" if default not in (None, "") else ""
            lines.append(f"- `{item.get('var')}` {kind}{told}: {_one_line(item.get('description'))}")
    if info.get("notes"):
        lines.append("Notes: " + _one_line(info["notes"]))
    return "\n".join(lines) + "\n"


def files() -> dict[str, str]:
    # A package role goes through pkg_workflow, and so has the common actions.
    package = {role for role in list_roles() if get_role_info(role).get("common_actions")}
    families = {
        "management": ("Management roles", "the system, sessions, updates, maintenance"),
        "software": ("Software roles", "packages installed, removed and configured"),
    }
    out: dict[str, str] = {}
    for family, (title, what) in families.items():
        roles = [role for role in list_roles()
                 if (role in package) == (family == "software")]
        parts: list[list[str]] = [[]]
        size = 0
        for role in roles:
            text = render(role)
            if parts[-1] and size + len(text) > LIMIT - 1024:
                parts.append([])
                size = 0
            parts[-1].append(text)
            size += len(text) + 1
        for at, chunk in enumerate(parts, 1):
            name = f"roles-{family}.md" if len(parts) == 1 else f"roles-{family}-{at}.md"
            head = (f"# {title} of win_workman{'' if len(parts) == 1 else f' ({at} of {len(parts)})'}\n\n"
                    f"{what.capitalize()}. Written by tools/fleet_skills.py from"
                    " roles/*/meta/mcp.yaml: do not edit by hand.\n\n")
            out[name] = head + "\n".join(chunk)
    return out


def main() -> int:
    check = "--check" in sys.argv[1:]
    wanted = files()
    stale = []
    for name, text in wanted.items():
        path = SKILL_DIR / name
        if path.exists() and path.read_text() == text:
            continue
        stale.append(name)
        if not check:
            path.write_text(text)
    for path in SKILL_DIR.glob("roles-*.md"):
        if path.name not in wanted:
            stale.append(path.name)
            if not check:
                path.unlink()
    if check and stale:
        print("not up to date: " + ", ".join(sorted(stale)) + " (run tools/fleet_skills.py)")
        return 1
    for name, text in sorted(wanted.items()):
        print(f"{name}: {len(text.encode())} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
