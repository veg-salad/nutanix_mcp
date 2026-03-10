"""Move migration plan tools — migration plans via Nutanix Move 4.x API."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import move_get
from nutanix_mcp.registry import json_response, resolve_move_instance

_MOVE_PLANS = "/move/v2/plans"


@mcp.tool()
def list_move_plans(move_name=None, status: str = "") -> str:
    """
    List migration plans defined on a Nutanix Move appliance.

    Each plan defines the source environment, target environment, network mapping,
    and the set of workloads (VMs) to migrate. The response includes plan status,
    schedule settings, and overall migration progress.

    Args:
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
        status: Optional filter — one of DRAFT, RUNNING, PAUSED, COMPLETED, FAILED, or empty
                for all plans.
    """
    params: dict = {}
    if status:
        params["status"] = status.upper()
    return json_response(move_get(_MOVE_PLANS, params=params if params else None, **resolve_move_instance(move_name)))


@mcp.tool()
def get_move_plan(plan_id: str, move_name=None) -> str:
    """
    Retrieve full details for a single migration plan by its ID.

    Returns plan configuration, source/target environment references, network mappings,
    VM list, and current status / progress metrics.

    Args:
        plan_id: The plan ID (extId or UUID) as returned by list_move_plans.
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
    """
    return json_response(move_get(f"{_MOVE_PLANS}/{plan_id}", **resolve_move_instance(move_name)))


@mcp.tool()
def get_move_plan_status(plan_id: str, move_name=None) -> str:
    """
    Retrieve the current migration status and progress summary for a plan.

    Args:
        plan_id: The plan ID (extId or UUID) as returned by list_move_plans.
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
    """
    return json_response(move_get(f"{_MOVE_PLANS}/{plan_id}/status", **resolve_move_instance(move_name)))
