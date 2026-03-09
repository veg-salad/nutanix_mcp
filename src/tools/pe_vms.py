"""PE VM tools — list, inspect, and retrieve NIC/disk sub-resources."""

from app import mcp
from client import pe_get
from registry import json_response, resolve_host


@mcp.tool()
def list_vms(
    cluster_name=None,
    limit: int = 50,
    page: int = 1,
    search_string=None,
    include_vm_disk_config: bool = False,
    include_vm_nic_config: bool = False,
) -> str:
    """
    List all virtual machines in a Prism Element cluster.

    Returns VM summaries including name, UUID, power state, vCPU count,
    memory size, and host placement.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
        search_string: Optional substring to filter VMs by name.
        include_vm_disk_config: Include disk configuration in each VM entry.
        include_vm_nic_config: Include NIC configuration in each VM entry.
    """
    params = {
        "count": limit,
        "page": page,
        "include_vm_disk_config": include_vm_disk_config,
        "include_vm_nic_config": include_vm_nic_config,
    }
    if search_string:
        params["search_string"] = search_string
    return json_response(pe_get("/vms/", params, host=resolve_host(cluster_name)))


@mcp.tool()
def get_vm(vm_uuid: str, cluster_name=None) -> str:
    """
    Get full details of a specific VM by its UUID.

    Returns VM configuration including vCPU/memory spec, boot config,
    guest OS info, power state, and host placement.

    Args:
        vm_uuid: The UUID of the VM. Obtain from list_vms.
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(pe_get(
        f"/vms/{vm_uuid}",
        {"include_vm_disk_config": True, "include_vm_nic_config": True},
        host=resolve_host(cluster_name),
    ))


@mcp.tool()
def get_vm_nics(vm_uuid: str, cluster_name=None) -> str:
    """
    List all network interfaces (NICs) attached to a specific VM.

    Returns each NIC's network UUID, MAC address, IP addresses, and adapter type.

    Args:
        vm_uuid: The UUID of the VM. Obtain from list_vms or get_vm.
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(
        pe_get(f"/vms/{vm_uuid}", {"include_vm_nic_config": True}, host=resolve_host(cluster_name))
        .get("vm_nics", [])
    )


@mcp.tool()
def get_vm_disks(vm_uuid: str, cluster_name=None) -> str:
    """
    List all disks (virtual drives) attached to a specific VM.

    Returns each disk's index, device bus (SCSI, IDE, etc.), size in bytes,
    backing storage container, and data source image if applicable.

    Args:
        vm_uuid: The UUID of the VM. Obtain from list_vms or get_vm.
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(
        pe_get(f"/vms/{vm_uuid}", {"include_vm_disk_config": True}, host=resolve_host(cluster_name))
        .get("vm_disk_info", [])
    )
