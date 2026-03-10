"""PC task tools — async tasks via Prism Central v4.0 API."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pc_v4_get
from nutanix_mcp.registry import json_response, resolve_pc_instance

_PC_TASKS = "/api/prism/v4.0/config/tasks"


@mcp.tool()
def list_pc_tasks(
    pc_name=None,
    status: str = "",
    limit: int = 25,
    page: int = 0,
) -> str:
    """
    List asynchronous tasks tracked by a Prism Central instance.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        status: Filter by task status — one of QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED,
                or empty for all.
        limit: Maximum number of results to return, up to 100 (default 25).
        page: Zero-based page index for pagination (default 0).
    """
    params: dict = {"$page": page, "$limit": min(limit, 100)}
    if status:
        params["$filter"] = f"status eq '{status.upper()}'"
    return json_response(pc_v4_get(_PC_TASKS, params=params, **resolve_pc_instance(pc_name)))


@mcp.tool()
def get_pc_task(task_id: str, pc_name=None) -> str:
    """
    Retrieve full details for a single task by its extId.

    Args:
        task_id: The extId (UUID) of the task as returned by list_pc_tasks.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"{_PC_TASKS}/{task_id}", **resolve_pc_instance(pc_name)))
