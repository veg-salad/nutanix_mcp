"""PE cluster tools — cluster summary and full configuration."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pe_get
from nutanix_mcp.registry import json_response, resolve_cluster


@mcp.tool()
def list_clusters(cluster_name=None) -> str:
    """
    Get the cluster summary for a Prism Element cluster.

    Returns cluster details including name, UUID, software version,
    hypervisor types, and redundancy factor.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(pe_get("/cluster/", **resolve_cluster(cluster_name)))
