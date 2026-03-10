"""PC cluster tools — list and inspect clusters via Prism Central v4.0 API."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pc_v4_get
from nutanix_mcp.registry import json_response, resolve_pc_instance

_PC_CLUSTERS = "/api/clustermgmt/v4.0/config/clusters"


@mcp.tool()
def list_pc_clusters(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all clusters registered with and managed by a Prism Central instance.

    Returns cluster summaries including name, extId, AOS version, and node count
    across all PE clusters visible to that Prism Central.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(pc_v4_get(_PC_CLUSTERS, params=params, **resolve_pc_instance(pc_name)))


@mcp.tool()
def get_pc_cluster(cluster_extid: str, pc_name=None) -> str:
    """
    Get full configuration details of a cluster registered with Prism Central.

    Returns AOS version, node count, cluster function, network config,
    and management server details.

    Args:
        cluster_extid: extId of the cluster. Obtain from list_pc_clusters.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"{_PC_CLUSTERS}/{cluster_extid}", **resolve_pc_instance(pc_name)))
