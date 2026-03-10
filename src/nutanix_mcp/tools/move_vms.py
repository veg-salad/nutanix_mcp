"""Move workload (VM) tools — migration workloads via Nutanix Move 4.x API."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import move_get
from nutanix_mcp.registry import json_response, resolve_move_instance

_MOVE_WORKLOADS = "/move/v2/workloads"


@mcp.tool()
def list_move_workloads(move_name=None, status: str = "") -> str:
    """
    List all workloads (VMs) tracked by a Nutanix Move appliance across all plans.

    Each result includes the VM name, source environment, target environment, migration
    phase (seeding / cutover / completed), and any error details.

    Args:
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
        status: Optional filter — one of PENDING, SEEDING, READY_TO_CUTOVER, CUTOVER,
                COMPLETED, FAILED, or empty for all.
    """
    params: dict = {}
    if status:
        params["status"] = status.upper()
    return json_response(
        move_get(_MOVE_WORKLOADS, params=params if params else None, **resolve_move_instance(move_name))
    )


@mcp.tool()
def get_move_workload(workload_id: str, move_name=None) -> str:
    """
    Retrieve full migration details for a single workload (VM) by its ID.

    Returns VM configuration snapshot, migration progress (bytes transferred, ETA),
    current phase, and any error or warning messages.

    Args:
        workload_id: The workload ID (extId or UUID) as returned by list_move_workloads
                     or list_move_plan_workloads.
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
    """
    return json_response(move_get(f"{_MOVE_WORKLOADS}/{workload_id}", **resolve_move_instance(move_name)))


@mcp.tool()
def list_move_plan_workloads(plan_id: str, move_name=None, status: str = "") -> str:
    """
    List workloads (VMs) belonging to a specific migration plan.

    Args:
        plan_id: The plan ID as returned by list_move_plans.
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
        status: Optional filter — one of PENDING, SEEDING, READY_TO_CUTOVER, CUTOVER,
                COMPLETED, FAILED, or empty for all.
    """
    params: dict = {"planId": plan_id}
    if status:
        params["status"] = status.upper()
    return json_response(move_get(_MOVE_WORKLOADS, params=params, **resolve_move_instance(move_name)))
