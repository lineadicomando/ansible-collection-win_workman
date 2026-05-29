import json
import os
import subprocess
from pathlib import Path


def _project_root() -> Path:
    root = os.environ.get("ANSIBLE_PROJECT_ROOT")
    if not root:
        raise RuntimeError("ANSIBLE_PROJECT_ROOT environment variable is not set")
    return Path(root)


def build_wm_command(t: list[str], l: str = "all", inventory: str = "school") -> list[str]:
    root = _project_root()
    cmd = ["ansible-playbook", "lineadicomando.win_workman.win_workman"]
    cmd += ["-i", str(root / "inventories" / inventory / "hosts.yaml")]
    if l and l != "all":
        cmd += ["-l", l]
    cmd += ["-e", json.dumps({"t": ",".join(t)})]
    return cmd


def run_command(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(_project_root()),
    )
    output = result.stdout
    if result.returncode != 0:
        output += f"\nSTDERR:\n{result.stderr}"
    return output


def format_command(cmd: list[str]) -> str:
    parts = []
    i = 0
    while i < len(cmd):
        token = cmd[i]
        if token in ("-e", "-i", "-l") and i + 1 < len(cmd):
            parts.append(f"{token} '{cmd[i + 1]}'")
            i += 2
        else:
            parts.append(token)
            i += 1
    return " \\\n  ".join(parts)
