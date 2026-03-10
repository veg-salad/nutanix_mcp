"""PC category tools — categories and values via Prism Central v4.0 API."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pc_v4_get
from nutanix_mcp.registry import json_response, resolve_pc_instance

_PC_CATEGORIES = "/api/prism/v4.0/config/categories"


@mcp.tool()
def list_pc_categories(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all category keys defined on a Prism Central instance.

    Categories are key–value pairs used to tag and group entities such as VMs,
    hosts, and clusters for policy assignment and filtering.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(pc_v4_get(_PC_CATEGORIES, params=params, **resolve_pc_instance(pc_name)))


@mcp.tool()
def get_pc_category(category_id: str, pc_name=None) -> str:
    """
    Retrieve full details for a single category key by its extId.

    Args:
        category_id: The extId of the category key as returned by list_pc_categories.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"{_PC_CATEGORIES}/{category_id}", **resolve_pc_instance(pc_name)))


@mcp.tool()
def list_pc_category_values(category_id: str, pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all values defined under a specific category key.

    Args:
        category_id: The extId of the category key as returned by list_pc_categories.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(
        pc_v4_get(f"{_PC_CATEGORIES}/{category_id}/values", params=params, **resolve_pc_instance(pc_name))
    )
