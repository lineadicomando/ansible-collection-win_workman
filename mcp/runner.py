import json
import os
import re
from pathlib import Path

from runlog import NotifyFn, RunStatus, await_run, read_log, redactor, run_logged_async, secret_strings, start_logged


def _project_root() -> Path:
    root = os.environ.get("ANSIBLE_PROJECT_ROOT")
    if not root:
        raise RuntimeError("ANSIBLE_PROJECT_ROOT environment variable is not set")
    return Path(root)


_EXTRA_VAR_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_extra_vars(extra_vars) -> str | None:
    """Return an error message if extra_vars cannot be passed to the playbook, else None.

    Extra vars sit at the top of Ansible's precedence, so they are limited to
    what a task needs: role variables. 't' is the task list itself, and
    ansible_* would let a caller swap the connection user, password, or become
    settings of every host in the run.
    """
    if extra_vars is None:
        return None
    if not isinstance(extra_vars, dict):
        return "extra_vars must be an object of variable names to values"
    for name in extra_vars:
        if not isinstance(name, str) or not _EXTRA_VAR_NAME.match(name):
            return f"invalid variable name in extra_vars: {name!r}"
        if name == "t":
            return "extra_vars cannot set 't': pass the tasks in the t parameter"
        if name.startswith("ansible_"):
            return f"extra_vars cannot set connection variables ({name})"
    try:
        json.dumps(extra_vars)
    except (TypeError, ValueError) as e:
        return f"extra_vars is not JSON-serialisable: {e}"
    return None


def merge_sensitive_vars(
    extra_vars: dict | None, sensitive_vars: dict | None
) -> tuple[dict | None, list[str]]:
    """Extra vars with the sensitive ones folded in, and the values to mask."""
    if not sensitive_vars:
        return extra_vars, []
    return {**(extra_vars or {}), **sensitive_vars}, secret_strings(sensitive_vars)


# Each fork is a Python process on the controller holding a connection open.
MAX_FORKS = 100


def validate_forks(forks) -> str | None:
    """Return an error message if forks is not a usable -f value, else None."""
    if forks is None:
        return None
    if isinstance(forks, bool) or not isinstance(forks, int):
        return "forks must be an integer"
    if not 1 <= forks <= MAX_FORKS:
        return f"forks must be between 1 and {MAX_FORKS}"
    return None


def build_wm_command(
    t: list[str],
    l: str = "lab_win",
    inventory: str = "school",
    extra_vars: dict | None = None,
    forks: int | None = None,
) -> list[str]:
    root = _project_root()
    cmd = ["ansible-playbook", "lineadicomando.win_workman.win_workman"]
    cmd += ["-i", str(root / "inventories" / inventory / "hosts.yaml")]
    if l and l != "all":
        cmd += ["-l", l]
    if forks is not None:
        cmd += ["-f", str(forks)]
    cmd += ["-e", json.dumps({**(extra_vars or {}), "t": ",".join(t)})]
    return cmd


async def run_command(
    cmd: list[str],
    label: str = "win_wm",
    notify: NotifyFn | None = None,
    redact: list[str] | None = None,
) -> str:
    """Run an ansible-playbook command, streaming its output to a log file.

    With redact, the extra vars go to ansible-playbook through a private file
    and the values listed are masked in the log and in the returned output.
    """
    result = await run_logged_async(cmd, _project_root(), label, notify, redact=redact)
    output = result.output
    if result.returncode != 0:
        output += f"\n[exit code {result.returncode}]"
    return f"{output}\n[log] {result.log_path}"


def start_run(cmd: list[str], label: str = "win_wm", redact: list[str] | None = None) -> Path:
    """Start an ansible-playbook command in the background; return its log path."""
    return start_logged(cmd, _project_root(), label, redact=redact)


def run_status(run: str = "latest", since_line: int = 0, max_lines: int = 200) -> RunStatus:
    """Read a run's log, whether it is still going or already finished."""
    return read_log(_project_root(), run, since_line, max_lines)


async def wait_run(
    run: str = "latest",
    timeout: float = 900.0,
    since_line: int = 0,
    max_lines: int = 200,
    notify: NotifyFn | None = None,
) -> RunStatus:
    """Block until a background run ends, then read its log."""
    return await await_run(_project_root(), run, timeout, since_line, max_lines, notify)


def format_command(cmd: list[str], redact: list[str] | None = None) -> str:
    hide = redactor(redact)
    cmd = [hide(token) for token in cmd]
    parts = []
    i = 0
    while i < len(cmd):
        token = cmd[i]
        if token in ("-e", "-i", "-l", "-f") and i + 1 < len(cmd):
            parts.append(f"{token} '{cmd[i + 1]}'")
            i += 2
        else:
            parts.append(token)
            i += 1
    return " \\\n  ".join(parts)
