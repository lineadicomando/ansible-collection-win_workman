import asyncio
import json

from mcp.server import Server
from mcp.server.context import ServerRequestContext
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, CallToolResult, ListToolsResult, PaginatedRequestParams, CallToolRequestParams

from roles import get_role_info, list_roles, pkg_actions
from runlog import NotifyFn, format_status
from runner import build_wm_command, format_command, run_command, run_status, start_run

app = Server("win-workman")


def _get_tools() -> list[Tool]:
    actions, default_action = pkg_actions()
    common_actions = ", ".join(
        f"{a} (default)" if a == default_action else a for a in actions
    )
    return [
        Tool(
            name="get_role_info",
            description=(
                "Returns display name, common package actions, custom actions, configurable "
                "defaults, and notes for a single win_workman role. Call this before run_tasks "
                "when you need to know what actions a role supports or which extra vars it "
                "accepts. Common actions carry 'handled_by': 'pkg_utils' for the shared "
                "implementation, or the role name when the role reimplements that action."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": f"Role name. Available: {', '.join(list_roles())}.",
                    }
                },
                "required": ["role"],
            },
        ),
        Tool(
            name="run_tasks",
            description=(
                "Run one or more win_workman tasks on an Ansible host or group "
                "via playbooks/win_wm.yaml. "
                f"Available roles: {', '.join(list_roles())}. "
                "Task format: <role> or <role>-<action> (e.g. chrome, chrome-off, chkdsk). "
                f"Common actions for package roles: {common_actions}. "
                "Roles may add custom actions or reimplement a common one: "
                "call get_role_info for the full list of a given role."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "t": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "List of tasks to run. "
                            "E.g. [\"chrome\"] or [\"chrome-info\", \"chrome-on\"]"
                        ),
                    },
                    "l": {
                        "type": "string",
                        "description": (
                            "Ansible limit: single hostname or group name. "
                            "E.g. 'teacher', 'students', 'lab_win'. "
                            "Default 'all': every host in the inventory."
                        ),
                        "default": "all",
                    },
                    "inventory": {
                        "type": "string",
                        "description": "Inventory name under inventories/.",
                        "default": "school",
                    },
                    "preview": {
                        "type": "boolean",
                        "description": (
                            "If true, returns the Ansible command without executing it. "
                            "Use this to show the user what will run and ask for confirmation."
                        ),
                        "default": False,
                    },
                    "background": {
                        "type": "boolean",
                        "description": (
                            "If true, start the run and return its run id immediately "
                            "instead of waiting for it to finish, then follow it with "
                            "run_status. Use this for runs over a whole lab, which take "
                            "minutes, so their output can be reported as it arrives."
                        ),
                        "default": False,
                    },
                },
                "required": ["t"],
            },
        ),
        Tool(
            name="run_status",
            description=(
                "Read the log of a run started with background=true: the new output "
                "since a given line, and whether the run is still going. "
                "Poll this to follow a lab-wide run while it runs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "run": {
                        "type": "string",
                        "description": (
                            "Run id, as returned by a background run. "
                            "'latest' (the default) is the most recent run."
                        ),
                        "default": "latest",
                    },
                    "since_line": {
                        "type": "integer",
                        "description": (
                            "Line to resume from: pass the since_line the previous "
                            "call reported, to get only what is new."
                        ),
                        "default": 0,
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "Most lines to return in one call.",
                        "default": 200,
                    },
                },
            },
        ),
    ]


def _progress_notifier(ctx: ServerRequestContext) -> NotifyFn | None:
    """Relay a run's output as progress notifications, if the client wants them.

    Clients opt in per request by sending a progress token; without one there
    is nobody to notify and the run streams to its log file only.
    """
    token = (ctx.meta or {}).get("progress_token")
    if token is None:
        return None

    async def notify(progress: int, message: str) -> None:
        await ctx.session.send_progress_notification(
            progress_token=token,
            progress=progress,
            message=message,
            related_request_id=ctx.request_id,
        )

    return notify


async def handle_list_tools(ctx: ServerRequestContext, params: PaginatedRequestParams) -> ListToolsResult:
    return ListToolsResult(tools=_get_tools())


async def handle_call_tool(ctx: ServerRequestContext, params: CallToolRequestParams) -> CallToolResult:
    name = params.name
    arguments = params.arguments or {}

    if name == "get_role_info":
        role = arguments.get("role", "")
        try:
            data = get_role_info(role)
        except FileNotFoundError as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error: {e}")])
        return CallToolResult(content=[TextContent(type="text", text=json.dumps(data, indent=2))])

    if name == "run_tasks":
        t: list[str] = arguments.get("t", [])
        if not t:
            return CallToolResult(content=[TextContent(type="text", text="Error: t (tasks) is required")])
        l: str = arguments.get("l", "all")
        inventory: str = arguments.get("inventory", "school")
        preview: bool = arguments.get("preview", False)

        cmd = build_wm_command(t, l, inventory)

        if preview:
            return CallToolResult(content=[TextContent(
                type="text",
                text=f"Command to run:\n\n  {format_command(cmd)}\n\nNo command executed.",
            )])

        label = f"win_wm-{'_'.join(t)}-{l}"

        if arguments.get("background", False):
            path = start_run(cmd, label)
            return CallToolResult(content=[TextContent(
                type="text",
                text=(
                    f"Started run {path.name}\n"
                    f"[log] {path}\n\n"
                    f'Follow it with run_status(run="{path.name}", since_line=0).'
                ),
            )])

        output = await run_command(cmd, label, _progress_notifier(ctx))
        return CallToolResult(content=[TextContent(type="text", text=output)])

    if name == "run_status":
        try:
            status = run_status(
                arguments.get("run", "latest"),
                int(arguments.get("since_line", 0)),
                int(arguments.get("max_lines", 200)),
            )
        except FileNotFoundError as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error: {e}")])
        return CallToolResult(content=[TextContent(type="text", text=format_status(status))])

    return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])


app.add_request_handler("tools/list", PaginatedRequestParams, handle_list_tools)
app.add_request_handler("tools/call", CallToolRequestParams, handle_call_tool)


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def cli():
    asyncio.run(main())


if __name__ == "__main__":
    cli()
