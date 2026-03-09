"""PC host tools — list and inspect nodes via Prism Central v4.0 API."""

from app import mcp
from client import pc_v4_get
from registry import json_response, resolve_pc_host

_PC_HOSTS = "/api/clustermgmt/v4.0/config/hosts"
_PC_CLUSTERS = "/api/clustermgmt/v4.0/config/clusters"


@mcp.tool()
def list_pc_hosts(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all hosts (nodes) across all clusters managed by a Prism Central instance.

    Returns host summaries including name, extId, cluster, CPU/memory capacity,
    hypervisor version, and current node state.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(pc_v4_get(_PC_HOSTS, params=params, host=resolve_pc_host(pc_name)))


@mcp.tool()
def get_pc_host(host_extid: str, cluster_extid: str, pc_name=None) -> str:
    """
    Get full details of a host (node) managed by Prism Central.

    Returns CPU model, core/thread counts, memory capacity, hypervisor version,
    CVM IP, and current operational state.

    Args:
        host_extid: extId of the host. Obtain from list_pc_hosts.
        cluster_extid: extId of the cluster the host belongs to. Obtain from list_pc_clusters.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    path = f"{_PC_CLUSTERS}/{cluster_extid}/hosts/{host_extid}"
    return json_response(pc_v4_get(path, host=resolve_pc_host(pc_name)))
