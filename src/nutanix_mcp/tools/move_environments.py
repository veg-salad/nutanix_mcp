"""Move environment tools — source and target environments via Nutanix Move 4.x API."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import move_get
from nutanix_mcp.registry import json_response, resolve_move_instance

_MOVE_ENVIRONMENTS = "/move/v2/environments"


@mcp.tool()
def list_move_environments(move_name=None) -> str:
    """
    List all registered environments (sources and targets) on a Nutanix Move appliance.

    Environments represent vCenter, AHV, or AWS/Azure endpoints that Move knows about.
    Each result includes the environment type (SOURCE / TARGET), protocol, and connectivity
    status. Use 'extId' values as identifiers in other Move tools.

    Args:
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
    """
    return json_response(move_get(_MOVE_ENVIRONMENTS, **resolve_move_instance(move_name)))


@mcp.tool()
def get_move_environment(env_id: str, move_name=None) -> str:
    """
    Retrieve full details for a single environment registered on a Nutanix Move appliance.

    Args:
        env_id: The extId of the environment as returned by list_move_environments.
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
    """
    return json_response(move_get(f"{_MOVE_ENVIRONMENTS}/{env_id}", **resolve_move_instance(move_name)))


@mcp.tool()
def list_move_source_environments(move_name=None) -> str:
    """
    List only source environments registered on a Nutanix Move appliance.

    Source environments are the platforms from which workloads will be migrated
    (e.g., VMware vCenter, legacy AHV clusters).

    Args:
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
    """
    params = {"type": "SOURCE"}
    return json_response(move_get(_MOVE_ENVIRONMENTS, params=params, **resolve_move_instance(move_name)))


@mcp.tool()
def list_move_target_environments(move_name=None) -> str:
    """
    List only target environments registered on a Nutanix Move appliance.

    Target environments are the platforms to which workloads will be migrated
    (e.g., AHV clusters registered in Prism Element or Prism Central).

    Args:
        move_name: Name from inventory.yaml (move_instances section). Omit to use the default
                   Move instance.
    """
    params = {"type": "TARGET"}
    return json_response(move_get(_MOVE_ENVIRONMENTS, params=params, **resolve_move_instance(move_name)))
