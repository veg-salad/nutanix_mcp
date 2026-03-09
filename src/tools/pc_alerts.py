"""PC alert tools — list and inspect alerts via Prism Central v2.0 gateway API."""

from app import mcp
from client import pc_v4_get
from registry import json_response, resolve_pc_host

_PC_ALERTS = "/PrismGateway/services/rest/v2.0/alerts"


@mcp.tool()
def list_pc_alerts(
    pc_name=None,
    limit: int = 50,
    page: int = 1,
    resolved: bool = False,
    acknowledged: bool = None,
) -> str:
    """
    List alerts across all clusters managed by a Prism Central instance.

    Uses the Prism Central v2.0 gateway. Returns each alert's id, severity
    (kCritical/kWarning/kInfo), alert_title, message, resolved/acknowledged
    status, and timestamps (in microseconds).

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return (default 50).
        page: 1-based page index for pagination (default 1).
        resolved: If False (default), return only active alerts. Set True to include resolved alerts.
        acknowledged: Filter by acknowledged status. Omit to return all.
    """
    params = {"count": min(limit, 100), "page": page, "resolved": str(resolved).lower()}
    if acknowledged is not None:
        params["acknowledged"] = str(acknowledged).lower()
    return json_response(pc_v4_get(_PC_ALERTS, params=params, host=resolve_pc_host(pc_name)))


@mcp.tool()
def get_pc_alert(alert_id: str, pc_name=None) -> str:
    """
    Get full details of a specific Prism Central alert.

    Returns severity, impacted entities, possible causes, resolution
    status, and timestamps.

    Args:
        alert_id: id of the alert (UUID). Obtain from list_pc_alerts.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"/api/nutanix/v3/alerts/{alert_id}", host=resolve_pc_host(pc_name)))
