"""PC image tools — disk and ISO images via Prism Central v4.0 API."""

from app import mcp
from client import pc_v4_get
from registry import json_response, resolve_pc_host

_PC_IMAGES = "/api/vmm/v4.0/content/images"


@mcp.tool()
def list_pc_images(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all images managed by a Prism Central instance.

    Returns each image's extId, name, image type (DISK_IMAGE or ISO_IMAGE),
    size in bytes, and current availability state.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(pc_v4_get(_PC_IMAGES, params=params, host=resolve_pc_host(pc_name)))
