"""Shared FastMCP application instance.

Import this module wherever @mcp.tool() decorators are needed.
"""

import logging

from mcp.server.fastmcp import FastMCP

logging.getLogger("mcp").setLevel(logging.WARNING)

mcp = FastMCP(
    "Nutanix Prism MCP Server",
    instructions=(
        "Provides read-only access to Nutanix Prism Element (PE) clusters via the v2.0 REST API "
        "and Nutanix Prism Central (PC) via the v4.0 REST API. "
        "Call list_inventory first to see available PC instances and PE clusters, "
        "then pass pc_name to PC tools (prefixed pc_) or cluster_name to PE tools. "
        "If only one entry is defined, it is selected automatically. "
        "PC tool responses use extId (not uuid) as the unique identifier for each entity. "
        "Use extId values returned by list_* tools as input for get_* tools. "
        "PC tools operate across all clusters managed by that Prism Central instance."
    ),
)
