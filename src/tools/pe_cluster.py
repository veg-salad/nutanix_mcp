"""PE cluster tools — cluster summary and full configuration."""

from app import mcp
from client import pe_get
from registry import json_response, resolve_host


@mcp.tool()
def list_clusters(cluster_name=None) -> str:
    """
    Get the cluster summary for a Prism Element cluster.

    Returns cluster details including name, UUID, software version,
    hypervisor types, and redundancy factor.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(pe_get("/cluster/", host=resolve_host(cluster_name)))


@mcp.tool()
def get_cluster(cluster_name=None) -> str:
    """
    Get full configuration details of a Prism Element cluster.

    Returns cluster configuration including nodes, network config, storage summary,
    AOS version, hypervisor info, and fault tolerance state.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(pe_get("/cluster/", host=resolve_host(cluster_name)))
