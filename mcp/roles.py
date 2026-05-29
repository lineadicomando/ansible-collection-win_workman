from pathlib import Path
import yaml

_COLLECTION_ROOT = Path(__file__).parent.parent
_ROLES_DIR = _COLLECTION_ROOT / "roles"
_INTERNAL_ROLES = {"dispatcher", "pkg_utils"}


def list_roles() -> list[str]:
    return sorted(
        p.name for p in _ROLES_DIR.iterdir()
        if p.is_dir() and p.name not in _INTERNAL_ROLES
    )


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
    data.setdefault("custom_actions", [])
    data.setdefault("defaults", [])
    return data
