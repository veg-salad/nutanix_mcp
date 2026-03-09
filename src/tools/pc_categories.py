"""PC category tools — key/value metadata tags via Prism Central v4.0 API."""

from app import mcp
from client import pc_v4_get
from registry import json_response, resolve_pc_host

_PC_CATEGORIES = "/api/prism/v4.0/config/categories"


@mcp.tool()
def list_pc_categories(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List Prism Central categories (key/value metadata tags applied to entities).

    Returns each category's extId, key, value, and description.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(pc_v4_get(_PC_CATEGORIES, params=params, host=resolve_pc_host(pc_name)))


@mcp.tool()
def get_pc_category(category_extid: str, pc_name=None) -> str:
    """
    Get full details of a Prism Central category by extId.

    Returns the category key, value, description, and associated entity count.

    Args:
        category_extid: extId of the category. Obtain from list_pc_categories.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"{_PC_CATEGORIES}/{category_extid}", host=resolve_pc_host(pc_name)))
