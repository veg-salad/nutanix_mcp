"""PE networking tools — VLANs and network configuration."""

from app import mcp
from client import pe_get
from registry import json_response, resolve_host


@mcp.tool()
def list_subnets(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all networks (VLANs) configured on a Prism Element cluster.

    Returns each network's UUID, name, VLAN ID, and IP configuration.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return json_response(pe_get("/networks/", {"count": limit, "page": page}, host=resolve_host(cluster_name)))
