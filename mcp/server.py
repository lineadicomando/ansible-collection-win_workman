import asyncio
import json

from mcp.server import Server
from mcp.server.context import ServerRequestContext
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, CallToolResult, ListToolsResult, PaginatedRequestParams, CallToolRequestParams

from roles import get_role_info, list_roles
from runner import build_wm_command, format_command, run_command

app = Server("win-workman")


def _get_tools() -> list[Tool]:
    return [
        Tool(
            name="get_role_info",
            description=(
                "Returns display name, custom actions, configurable defaults, and notes "
                "for a single win_workman role. Call this before run_tasks when you need "
                "to know what actions a role supports or which extra vars it accepts."
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
                "Common actions: on (default/install), off (remove), info, download, is_present."
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
                },
                "required": ["t"],
            },
        ),
    ]


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

        output = await asyncio.to_thread(run_command, cmd)
        return CallToolResult(content=[TextContent(type="text", text=output)])

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
