"""PC alert tools — list and inspect alerts via Prism Central v4.0 API."""

from app import mcp
from client import pc_v4_get
from registry import json_response, resolve_pc_host

_PC_ALERTS = "/api/alerting/v4.0/alerts"


@mcp.tool()
def list_pc_alerts(
    pc_name=None,
    limit: int = 50,
    page: int = 0,
    filter: str = None,
) -> str:
    """
    List alerts across all clusters managed by a Prism Central instance.

    Returns each alert's extId, severity (CRITICAL/WARNING/INFO), title, message,
    creation time, and resolution status.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
        filter: Optional OData $filter expression (e.g. "severity eq 'CRITICAL'").
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    if filter:
        params["$filter"] = filter
    return json_response(pc_v4_get(_PC_ALERTS, params=params, host=resolve_pc_host(pc_name)))


@mcp.tool()
def get_pc_alert(alert_extid: str, pc_name=None) -> str:
    """
    Get full details of a specific Prism Central alert.

    Returns severity, impacted entities, root cause analysis, resolution
    status, and timestamps.

    Args:
        alert_extid: extId of the alert. Obtain from list_pc_alerts.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"{_PC_ALERTS}/{alert_extid}", host=resolve_pc_host(pc_name)))
