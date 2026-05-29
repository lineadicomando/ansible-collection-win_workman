import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from roles import get_role_info, list_roles
from runner import build_wm_command, format_command, run_command

app = Server("win-workman")


@app.list_tools()
async def list_tools() -> list[Tool]:
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


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_role_info":
        role = arguments.get("role", "")
        try:
            data = get_role_info(role)
        except FileNotFoundError as e:
            return [TextContent(type="text", text=f"Error: {e}")]
        return [TextContent(type="text", text=json.dumps(data, indent=2))]

    if name == "run_tasks":
        t: list[str] = arguments["t"]
        l: str = arguments.get("l", "all")
        inventory: str = arguments.get("inventory", "school")
        preview: bool = arguments.get("preview", False)

        cmd = build_wm_command(t, l, inventory)

        if preview:
            return [TextContent(
                type="text",
                text=f"Command to run:\n\n  {format_command(cmd)}\n\nNo command executed.",
            )]

        output = await asyncio.to_thread(run_command, cmd)
        return [TextContent(type="text", text=output)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def cli():
    asyncio.run(main())


if __name__ == "__main__":
    cli()
