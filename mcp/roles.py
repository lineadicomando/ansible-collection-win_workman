from pathlib import Path
import re
import yaml

_COLLECTION_ROOT = Path(__file__).parent.parent
_ROLES_DIR = _COLLECTION_ROOT / "roles"
_INTERNAL_ROLES = {"dispatcher", "pkg_utils"}
_PKG_UTILS_VARS = _ROLES_DIR / "pkg_utils" / "vars" / "main.yaml"
_JINJA_VAR = re.compile(r"^\{\{\s*(\w+)\s*\}\}$")


def list_roles() -> list[str]:
    return sorted(
        p.name for p in _ROLES_DIR.iterdir()
        if p.is_dir() and p.name not in _INTERNAL_ROLES
    )


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _action_name(value) -> str:
    """YAML turns unquoted on/off into booleans; map them back to action names."""
    if value is True:
        return "on"
    if value is False:
        return "off"
    return str(value)


def pkg_actions() -> tuple[list[str], str]:
    """Common package actions and the default one, read from pkg_utils vars."""
    data = _load_yaml(_PKG_UTILS_VARS)
    default_action = _action_name(data.get("win_workman_action_default", "on"))
    actions: list[str] = []
    for entry in data.get("win_workman_pkg_actions") or []:
        name = _action_name(entry)
        # The list references the default action as a Jinja var; resolve it.
        match = _JINJA_VAR.match(name)
        if match:
            name = _action_name(data.get(match.group(1), default_action))
        if name not in actions:
            actions.append(name)
    return actions, default_action


def get_role_info(role_name: str) -> dict:
    role_dir = _ROLES_DIR / role_name
    if not role_dir.is_dir():
        raise FileNotFoundError(f"Role not found: {role_name}")
    manifest_path = role_dir / "meta" / "mcp.yaml"
    if manifest_path.exists():
        data = yaml.safe_load(manifest_path.read_text()) or {}
    else:
        data = {}
    data.setdefault("display_name", role_name)
    data.setdefault("defaults", [])

    declared = data.get("custom_actions") or []
    dispatcher = (role_dir / "tasks" / "main.yaml")
    dispatcher_text = dispatcher.read_text() if dispatcher.exists() else ""

    # Roles that never reach pkg_workflow (shutdown, ping, wol...) expose no common actions.
    if "pkg_workflow" not in dispatcher_text:
        data["custom_actions"] = declared
        data["common_actions"] = []
        return data

    actions, default_action = pkg_actions()
    described = {
        _action_name(a.get("name")): a.get("description")
        for a in declared if isinstance(a, dict) and a.get("name") is not None
    }

    common = []
    for action in actions:
        act_file = role_dir / "tasks" / f"act_{action}.yaml"
        overridden = action in described or (
            act_file.exists() and f"act_{action}" in dispatcher_text
        )
        item: dict = {"name": action}
        if action == default_action:
            item["default"] = True
        item["handled_by"] = role_name if overridden else "pkg_utils"
        description = described.get(action)
        if description:
            item["description"] = description
        elif overridden:
            item["description"] = f"Reimplemented by the {role_name} role"
        common.append(item)

    data["custom_actions"] = [
        a for a in declared
        if not (isinstance(a, dict) and _action_name(a.get("name")) in set(actions))
    ]
    data["common_actions"] = common
    return data
