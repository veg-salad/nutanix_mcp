"""Nutanix MCP Server — kept for direct execution compatibility.

The primary entry point is the 'nutanix-mcp' CLI command (nutanix_mcp.cli:main).
This module can still be run directly: python -m nutanix_mcp.server

See available_tools.md for the full tool reference.
"""

from nutanix_mcp.cli import main

if __name__ == "__main__":
    main()
