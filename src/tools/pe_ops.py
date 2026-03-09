"""PE operations tools — protection domains and tasks."""

from app import mcp
from client import pe_get
from registry import json_response, resolve_host


@mcp.tool()
def list_protection_domains(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List protection domains (DR / backup configurations) in a Prism Element cluster.

    Returns each protection domain's name, type, active/standby state,
    and associated VMs or volume groups.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return json_response(pe_get("/protection_domains/", {"count": limit, "page": page}, host=resolve_host(cluster_name)))


@mcp.tool()
def list_tasks(cluster_name=None, limit: int = 50, include_completed: bool = False) -> str:
    """
    List recent tasks on a Prism Element cluster.

    Returns each task's UUID, type, status (Running/Succeeded/Failed),
    progress percentage, start time, and completion time.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        include_completed: Include completed/failed tasks in addition to running ones (default False).
    """
    params = {"count": limit, "include_completed": str(include_completed).lower()}
    return json_response(pe_get("/tasks/", params, host=resolve_host(cluster_name)))
