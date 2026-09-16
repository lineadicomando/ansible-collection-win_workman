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


def usr_verbs() -> list[dict]:
    """Verbs of the usr action (per-user deferred install), read from pkg_utils vars."""
    data = _load_yaml(_PKG_UTILS_VARS)
    verbs = []
    for entry in data.get("win_workman_usr_verbs") or []:
        item = {"name": _action_name(entry.get("name"))}
        if entry.get("default"):
            item["default"] = True
        if entry.get("description"):
            item["description"] = entry["description"]
        verbs.append(item)
    return verbs


def install_scopes(role_dir: Path) -> list[str]:
    """Install scopes a package role supports, from the blocks of its schema.

    A package block means machine-wide install (sys), a usr block per-user
    deferred install (usr). Schemas are found by their <role>_schema name.
    """
    data = _load_yaml(role_dir / "vars" / "main.yaml")
    schema = data.get(f"win_workman_{role_dir.name}_schema")
    if not isinstance(schema, dict):
        return ["sys"]
    scopes = [scope for scope, block in (("sys", "package"), ("usr", "usr")) if block in schema]
    return scopes or ["sys"]


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
    scopes = install_scopes(role_dir)
    schema = _load_yaml(role_dir / "vars" / "main.yaml").get(f"win_workman_{role_name}_schema")
    role_default = default_action
    if isinstance(schema, dict) and schema.get("default_action") is not None:
        role_default = _action_name(schema["default_action"])
    data["install_scopes"] = scopes
    if "usr" not in scopes:
        actions = [a for a in actions if a != "usr"]
    if "sys" not in scopes:
        actions = [a for a in actions if a in ("usr", "download")]
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
        if action == role_default:
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
    if "usr" in scopes:
        data["usr_actions"] = {
            "syntax": "<role>-usr-<verb>[-<target>[+<target>...]]",
            "targets": (
                "Optional account or group names joined by '+' (names may contain '-'). "
                "Without targets, on uses win_workman_usr_targets (default BUILTIN\\Users) "
                "and off applies to every target already in the policy."
            ),
            "verbs": usr_verbs(),
        }
    return data
