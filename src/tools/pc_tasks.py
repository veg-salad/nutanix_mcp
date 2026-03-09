"""PC task tools — list and inspect tasks via Prism Central v4.0 API."""

from app import mcp
from client import pc_v4_get
from registry import json_response, resolve_pc_host

_PC_TASKS = "/api/prism/v4.0/config/tasks"


@mcp.tool()
def list_pc_tasks(
    pc_name=None,
    limit: int = 50,
    page: int = 0,
    filter: str = None,
) -> str:
    """
    List tasks across all clusters managed by a Prism Central instance.

    Returns each task's extId, operation type, status (Queued/Running/Succeeded/Failed),
    progress percentage, start time, and completion time.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
        filter: Optional OData $filter expression (e.g. "status eq 'FAILED'").
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    if filter:
        params["$filter"] = filter
    return json_response(pc_v4_get(_PC_TASKS, params=params, host=resolve_pc_host(pc_name)))


@mcp.tool()
def get_pc_task(task_extid: str, pc_name=None) -> str:
    """
    Get full details of a specific Prism Central task.

    Returns operation type, status, progress, error details (on failure),
    and impacted entities.

    Args:
        task_extid: extId of the task. Obtain from list_pc_tasks.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"{_PC_TASKS}/{task_extid}", host=resolve_pc_host(pc_name)))
