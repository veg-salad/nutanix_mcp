"""PE host tools — list and inspect nodes."""

from app import mcp
from client import pe_get
from registry import json_response, resolve_host


@mcp.tool()
def list_hosts(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all hosts (nodes) in a Prism Element cluster.

    Returns host summaries including name, UUID, IP addresses, CPU/memory
    capacity, hypervisor version, and current node status.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return json_response(pe_get("/hosts/", {"count": limit, "page": page}, host=resolve_host(cluster_name)))


@mcp.tool()
def get_host(host_uuid: str, cluster_name=None) -> str:
    """
    Get full details of a specific host (node) by its UUID.

    Returns hardware details, CPU/memory capacity and usage, network interfaces,
    disk inventory, and current operational status.

    Args:
        host_uuid: The UUID of the host. Obtain from list_hosts.
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(pe_get(f"/hosts/{host_uuid}", host=resolve_host(cluster_name)))
