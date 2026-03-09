"""PC VM tools — list, inspect, and retrieve disk/NIC sub-resources via Prism Central v4.0 API."""

from app import mcp
from client import pc_v4_get
from registry import json_response, resolve_pc_host

_PC_VMS = "/api/vmm/v4.0/ahv/config/vms"


@mcp.tool()
def list_pc_vms(pc_name=None, limit: int = 50, page: int = 0, filter: str = None) -> str:
    """
    List virtual machines across all clusters managed by a Prism Central instance.

    Returns VM summaries including name, extId, power state, vCPU count,
    memory size, and cluster placement.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
        filter: Optional OData $filter expression (e.g. "name eq 'myvm'" or
                "contains(name, 'prod')" or "powerState eq 'ON'").
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    if filter:
        params["$filter"] = filter
    return json_response(pc_v4_get(_PC_VMS, params=params, host=resolve_pc_host(pc_name)))


@mcp.tool()
def get_pc_vm(vm_extid: str, pc_name=None) -> str:
    """
    Get full details of a specific VM by extId via Prism Central.

    Returns VM spec including vCPU/memory, disk and NIC configuration,
    boot config, guest OS, power state, and cluster placement.

    Args:
        vm_extid: The extId of the VM. Obtain from list_pc_vms.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
    """
    return json_response(pc_v4_get(f"{_PC_VMS}/{vm_extid}", host=resolve_pc_host(pc_name)))


@mcp.tool()
def list_pc_vm_disks(vm_extid: str, pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all disks attached to a VM via Prism Central.

    Returns each disk's extId, device bus (SCSI/IDE/SATA), index, size in bytes,
    storage container, and data source image.

    Args:
        vm_extid: extId of the VM. Obtain from list_pc_vms.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(pc_v4_get(f"{_PC_VMS}/{vm_extid}/disks", params=params, host=resolve_pc_host(pc_name)))


@mcp.tool()
def list_pc_vm_nics(vm_extid: str, pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all network interfaces (NICs) attached to a VM via Prism Central.

    Returns each NIC's extId, network extId, VLAN mode, MAC address, IP addresses,
    and connected state.

    Args:
        vm_extid: extId of the VM. Obtain from list_pc_vms.
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return json_response(pc_v4_get(f"{_PC_VMS}/{vm_extid}/nics", params=params, host=resolve_pc_host(pc_name)))
