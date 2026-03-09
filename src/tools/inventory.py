"""Inventory tool — list all registered PE clusters and PC instances."""

from app import mcp
from registry import json_response, INVENTORY, PC_INVENTORY


@mcp.tool()
def list_inventory() -> str:
    """
    List all Prism Central instances and Prism Element clusters in inventory.yaml.

    Returns prism_central entries (pass name as pc_name to PC tools) and
    cluster entries (pass name as cluster_name to PE tools).
    Single entries are selected automatically; multiple entries require an explicit name.
    """
    return json_response({"prism_central": PC_INVENTORY, "clusters": INVENTORY})
