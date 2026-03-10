"""PC alert tools — alerts and policies via Prism Central."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pc_v4_get
from nutanix_mcp.registry import json_response, resolve_pc_instance

_PC_ALERTS_V2 = "/PrismGateway/services/rest/v2.0/alerts"
_PC_ALERT_V4 = "/api/monitoring/v4.0/alerts"


@mcp.tool()
def list_pc_alerts(
    pc_name=None,
    resolved: bool = False,
    acknowledged: bool = False,
    severity: str = "",
    limit: int = 25,
    page: int = 0,
) -> str:
    """
    List alerts from a Prism Central instance across all managed clusters.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        resolved: If True, include only resolved alerts (default False returns open alerts).
        acknowledged: If True, include only acknowledged alerts.
        severity: Filter by severity — one of CRITICAL, WARNING, INFO, or empty for all.
        limit: Maximum number of alerts to return, up to 100 (default 25).
        page: Zero-based page index for pagination (default 0).
    """
    params: dict = {
        "resolved": str(resolved).lower(),
        "acknowledged": str(acknowledged).lower(),
        "count": min(limit, 100),
        "page": page,
    }
    if severity:
        params["severity"] = severity.upper()
    return json_response(pc_v4_get(_PC_ALERTS_V2, params=params, **resolve_pc_instance(pc_name)))


@mcp.tool()
def get_pc_alert(alert_id: str, pc_name=None) -> str:
    """
    Retrieve full details for a single alert by its extId / UUID.

    Args:
        alert_id: The extId (UUID) of the alert as returned by list_pc_alerts.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"{_PC_ALERT_V4}/{alert_id}", **resolve_pc_instance(pc_name)))


@mcp.tool()
def list_pc_alert_policies(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List alert policies (user-defined alert rules) configured on a Prism Central instance.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(
        pc_v4_get("/api/monitoring/v4.0/services/alerts/alert-policies", params=params, **resolve_pc_instance(pc_name))
    )
