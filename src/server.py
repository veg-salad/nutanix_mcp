"""Nutanix Prism MCP Server — entry point.

Imports all tool modules (which register their @mcp.tool() decorators on the
shared FastMCP instance in app.py) then starts the server over stdio.

See available_tools.md for the full tool reference.
"""

# Tool modules — imported for side-effects (decorator registration only)
import tools.inventory
import tools.pe_cluster
import tools.pe_hosts
import tools.pe_vms
import tools.pe_storage
import tools.pe_networking
import tools.pe_images
import tools.pe_alerts
import tools.pe_ops
import tools.pe_stats
import tools.pc_clusters
import tools.pc_vms
import tools.pc_hosts
import tools.pc_networking
import tools.pc_images
import tools.pc_storage
import tools.pc_alerts
import tools.pc_tasks
import tools.pc_categories

from app import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
