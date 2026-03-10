"""PE alerts and events tools."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pe_get
from nutanix_mcp.registry import json_response, resolve_cluster


@mcp.tool()
def list_alerts(
    cluster_name=None,
    limit: int = 50,
    page: int = 1,
    resolved: bool = False,
    acknowledged: bool = False,
) -> str:
    """
    List alerts on a Prism Element cluster.

    Returns each alert's UUID, severity (CRITICAL/WARNING/INFO), title,
    message, creation time, and resolution status.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
        resolved: Return only resolved alerts when True (default False = unresolved only).
        acknowledged: Return only acknowledged alerts when True (default False).
    """
    params = {
        "count": limit,
        "page": page,
        "resolved": str(resolved).lower(),
        "acknowledged": str(acknowledged).lower(),
    }
    return json_response(pe_get("/alerts/", params, **resolve_cluster(cluster_name)))


@mcp.tool()
def list_events(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List audit events on a Prism Element cluster.

    Returns each event's type, message, source entity, creation time,
    and associated cluster.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return json_response(pe_get("/events/", {"count": limit, "page": page}, **resolve_cluster(cluster_name)))
