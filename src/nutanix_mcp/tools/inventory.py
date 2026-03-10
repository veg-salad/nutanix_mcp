"""Inventory tool — list all registered PE clusters, PC instances, and Move appliances."""

from nutanix_mcp.app import mcp
from nutanix_mcp.registry import json_response, INVENTORY, PC_INVENTORY, MOVE_INVENTORY


@mcp.tool()
def list_inventory() -> str:
    """
    List all Prism Central instances, Prism Element clusters, and Move appliances in inventory.yaml.

    Returns prism_central entries (pass name as pc_name to PC tools),
    cluster entries (pass name as cluster_name to PE tools), and
    move_instances entries (pass name as move_name to Move tools).
    Single entries of each type are selected automatically; multiple entries require an explicit name.
    """
    return json_response({
        "prism_central": PC_INVENTORY,
        "clusters": INVENTORY,
        "move_instances": MOVE_INVENTORY,
    })
