"""PE CVM tools — list and inspect Controller VMs.

Each Nutanix node runs exactly one CVM (Controller VM) that handles all I/O
and cluster services.  On VMware ESXi and Hyper-V clusters, CVMs are not part
of the guest VM inventory, so their details are sourced from the host (node)
objects, which expose a CVM-centric view via service_vm* and controller_vm_*
fields.
"""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pe_get
from nutanix_mcp.registry import json_response, resolve_cluster


def _cvm_view(host: dict) -> dict:
    """Extract CVM-relevant fields from a host object."""
    return {
        "host_name": host.get("name"),
        "host_uuid": host.get("uuid"),
        "cvm_id": host.get("service_vmid"),
        "cvm_ip": host.get("service_vmexternal_ip"),
        "cvm_backplane_ip": host.get("controller_vm_backplane_ip"),
        "hypervisor_ip": host.get("hypervisor_address"),
        "hypervisor_type": host.get("hypervisor_type"),
        "hypervisor_full_name": host.get("hypervisor_full_name"),
        "state": host.get("state"),
        "is_degraded": host.get("is_degraded"),
        "host_in_maintenance_mode": host.get("host_in_maintenance_mode"),
        "reboot_pending": host.get("reboot_pending"),
        "metadata_store_status": host.get("metadata_store_status"),
        "metadata_store_status_message": host.get("metadata_store_status_message"),
        "oplog_disk_pct": host.get("oplog_disk_pct"),
        "block_serial": host.get("block_serial"),
        "block_model": host.get("block_model_name") or host.get("block_model"),
    }


@mcp.tool()
def list_cvms(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all Controller VMs (CVMs) in a Prism Element cluster.

    Returns one entry per node with the CVM's IP addresses, associated host
    UUID and hypervisor IP, operational state, metadata store status, and
    hardware model/serial.  There is exactly one CVM per node.

    On VMware ESXi and Hyper-V clusters, CVMs are not in the guest VM
    inventory; this tool sources their details from the host (node) objects.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    data = pe_get("/hosts/", {"count": limit, "page": page}, **resolve_cluster(cluster_name))
    cvms = [_cvm_view(h) for h in data.get("entities", [])]
    result = {"metadata": data.get("metadata", {}), "entities": cvms}
    return json_response(result)


@mcp.tool()
def get_cvm(host_uuid: str, cluster_name=None) -> str:
    """
    Get details of the Controller VM (CVM) running on a specific node.

    Returns the CVM's IP addresses, hypervisor IP, operational state,
    metadata store status, oplog disk usage, and hardware model/serial.
    Uses the host UUID as the identifier since each node has exactly one CVM.

    Args:
        host_uuid: UUID of the host node. Obtain from list_hosts or list_cvms.
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    host = pe_get(f"/hosts/{host_uuid}", **resolve_cluster(cluster_name))
    return json_response(_cvm_view(host))
