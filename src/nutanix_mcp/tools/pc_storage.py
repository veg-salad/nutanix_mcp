"""PC storage tools — storage containers via Prism Central v4.0 API."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pc_v4_get
from nutanix_mcp.registry import json_response, resolve_pc_instance

_PC_STORAGE_CONTAINERS = "/api/clustermgmt/v4.0/config/storage-containers"


@mcp.tool()
def list_pc_storage_containers(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List storage containers across all clusters managed by a Prism Central instance.

    Returns each container's name, capacity, usage, and data-efficiency settings
    (compression, dedup, erasure coding). Note: the unique identifier field is
    'containerExtId' (not 'extId') in the response objects.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(pc_v4_get(_PC_STORAGE_CONTAINERS, params=params, **resolve_pc_instance(pc_name)))
