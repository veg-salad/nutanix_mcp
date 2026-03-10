"""Shared FastMCP application instance.

Import this module wherever @mcp.tool() decorators are needed.
"""

import logging

from mcp.server.fastmcp import FastMCP

logging.getLogger("mcp").setLevel(logging.WARNING)

mcp = FastMCP(
    "Nutanix MCP",
    instructions=(
        "Provides read-only access to Nutanix infrastructure: "
        "Prism Element (PE) clusters via the v2.0 REST API, "
        "Prism Central (PC) via the v4.0 REST API, "
        "and Nutanix Move migration appliances via the v2 REST API. "
        "Call list_inventory first to see available PC instances, PE clusters, and Move appliances, "
        "then pass pc_name to PC tools (prefixed pc_), cluster_name to PE tools, "
        "or move_name to Move tools (prefixed move_). "
        "If only one entry is defined for a type, it is selected automatically. "
        "PC tool responses use extId (not uuid) as the unique identifier for each entity. "
        "Use extId values returned by list_* tools as input for get_* tools. "
        "PC tools operate across all clusters managed by that Prism Central instance."
    ),
)
