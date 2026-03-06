"""
Nutanix Prism MCP Server — read-only tools via Prism Element v2.0 and Prism Central v4.0 APIs.

Tools
-----
Inventory    : list_inventory
PE Cluster   : list_clusters, get_cluster
PE Hosts     : list_hosts, get_host
PE VMs       : list_vms, get_vm, get_vm_nics, get_vm_disks
PE Networking: list_subnets
PE Images    : list_images
PC Clusters  : list_pc_clusters
PC VMs       : list_pc_vms, get_pc_vm
PC Hosts     : list_pc_hosts
PC Networking: list_pc_subnets
PC Images    : list_pc_images

PE tools accept an optional cluster_name parameter resolved from inventory.yaml.
PC tools accept an optional pc_name parameter resolved from inventory.yaml.
If omitted and only one entry is defined, it is used automatically.

Add entries to inventory.yaml. Credentials are configured in .vscode/mcp.json.
PC credentials: NUTANIX_PC_API_KEY (preferred) or NUTANIX_PC_USERNAME + NUTANIX_PC_PASSWORD.
PE credentials: NUTANIX_USERNAME + NUTANIX_PASSWORD.

Transport : stdio (run locally; detected by VS Code GitHub Copilot via .vscode/mcp.json)
"""

import json
import logging
import os

import yaml

logging.getLogger("mcp").setLevel(logging.WARNING)

from mcp.server.fastmcp import FastMCP

from client import pe_get, pc_v4_get

mcp = FastMCP(
    "Nutanix Prism MCP Server",
    instructions=(
        "Provides read-only access to Nutanix Prism Element (PE) clusters via the v2.0 REST API "
        "and Nutanix Prism Central (PC) via the v4.0 REST API. "
        "Call list_inventory first to see available PC instances and PE clusters, "
        "then pass pc_name to PC tools (prefixed pc_) or cluster_name to PE tools. "
        "If only one entry is defined, it is selected automatically. "
        "PC tool responses use extId (not uuid) as the unique identifier for each entity. "
        "Use extId values returned by list_* tools as input for get_* tools. "
        "PC tools operate across all clusters managed by that Prism Central instance."
    ),
)

# ---------------------------------------------------------------------------
# Inventory — maps cluster names to PE host IPs / PC names to PC host IPs
# ---------------------------------------------------------------------------

_INVENTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inventory.yaml")


def _load_inventory():
    if not os.path.exists(_INVENTORY_PATH):
        return []
    with open(_INVENTORY_PATH) as f:
        data = yaml.safe_load(f)
        return data.get("clusters", [])


def _load_pc_inventory():
    if not os.path.exists(_INVENTORY_PATH):
        return []
    with open(_INVENTORY_PATH) as f:
        data = yaml.safe_load(f)
        return data.get("prism_central", [])


_INVENTORY = _load_inventory()
_PC_INVENTORY = _load_pc_inventory()


def _resolve_host(cluster_name=None):
    """Return the PE host IP for the given cluster_name, or auto-select if only one cluster exists."""
    names = [e["name"] for e in _INVENTORY]

    if not _INVENTORY:
        raise ValueError(
            "inventory.yaml has no clusters defined. "
            "Add at least one entry before using any tool."
        )

    if not cluster_name:
        if len(_INVENTORY) == 1:
            return _INVENTORY[0]["pe_host"]
        raise ValueError(
            f"Multiple clusters in inventory — specify cluster_name. "
            f"Available: {names}"
        )

    for entry in _INVENTORY:
        if entry["name"].lower() == cluster_name.lower():
            return entry["pe_host"]

    raise ValueError(
        f"Cluster '{cluster_name}' not found in inventory.yaml. "
        f"Available: {names}"
    )


def _resolve_pc_host(pc_name=None):
    """Return the PC host IP for the given pc_name, or auto-select if only one PC instance exists."""
    names = [e["name"] for e in _PC_INVENTORY]

    if not _PC_INVENTORY:
        raise ValueError(
            "inventory.yaml has no prism_central entries defined. "
            "Add at least one entry before using PC tools."
        )

    if not pc_name:
        if len(_PC_INVENTORY) == 1:
            return _PC_INVENTORY[0]["pc_host"]
        raise ValueError(
            f"Multiple Prism Central instances in inventory — specify pc_name. "
            f"Available: {names}"
        )

    for entry in _PC_INVENTORY:
        if entry["name"].lower() == pc_name.lower():
            return entry["pc_host"]

    raise ValueError(
        f"Prism Central '{pc_name}' not found in inventory.yaml. "
        f"Available: {names}"
    )


def _json(data) -> str:
    return json.dumps(data, indent=2, default=str)


# ---------------------------------------------------------------------------
# Inventory tool
# ---------------------------------------------------------------------------


@mcp.tool()
def list_inventory() -> str:
    """
    List all Prism Central instances and Prism Element clusters in inventory.yaml.

    Returns prism_central entries (pass name as pc_name to PC tools) and
    cluster entries (pass name as cluster_name to PE tools).
    Single entries are selected automatically; multiple entries require an explicit name.
    """
    return _json({"prism_central": _PC_INVENTORY, "clusters": _INVENTORY})


# ---------------------------------------------------------------------------
# Cluster tools
# ---------------------------------------------------------------------------


@mcp.tool()
def list_clusters(cluster_name=None) -> str:
    """
    Get the cluster summary for a Prism Element cluster.

    Returns cluster details including name, UUID, software version,
    hypervisor types, and redundancy factor.

    Args:
        cluster_name: Name from inventory.json. Omit to use the default cluster.
    """
    return _json(pe_get("/cluster/", host=_resolve_host(cluster_name)))


@mcp.tool()
def get_cluster(cluster_name=None) -> str:
    """
    Get full configuration details of a Prism Element cluster.

    Returns cluster configuration including nodes, network config, storage summary,
    AOS version, hypervisor info, and fault tolerance state.

    Args:
        cluster_name: Name from inventory.json. Omit to use the default cluster.
    """
    return _json(pe_get("/cluster/", host=_resolve_host(cluster_name)))


# ---------------------------------------------------------------------------
# Host tools
# ---------------------------------------------------------------------------


@mcp.tool()
def list_hosts(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all hosts (nodes) in a Prism Element cluster.

    Returns host summaries including name, UUID, IP addresses, CPU/memory
    capacity, hypervisor version, and current node status.

    Args:
        cluster_name: Name from inventory.json. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return _json(pe_get("/hosts/", {"count": limit, "page": page}, host=_resolve_host(cluster_name)))


@mcp.tool()
def get_host(host_uuid: str, cluster_name=None) -> str:
    """
    Get full details of a specific host (node) by its UUID.

    Returns hardware details, CPU/memory capacity and usage, network interfaces,
    disk inventory, and current operational status.

    Args:
        host_uuid: The UUID of the host. Obtain from list_hosts.
        cluster_name: Name from inventory.json. Omit to use the default cluster.
    """
    return _json(pe_get(f"/hosts/{host_uuid}", host=_resolve_host(cluster_name)))


# ---------------------------------------------------------------------------
# VM tools
# ---------------------------------------------------------------------------


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
        cluster_name: Name from inventory.json. Omit to use the default cluster.
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
    return _json(pe_get("/vms/", params, host=_resolve_host(cluster_name)))


@mcp.tool()
def get_vm(vm_uuid: str, cluster_name=None) -> str:
    """
    Get full details of a specific VM by its UUID.

    Returns VM configuration including vCPU/memory spec, boot config,
    guest OS info, power state, and host placement.

    Args:
        vm_uuid: The UUID of the VM. Obtain from list_vms.
        cluster_name: Name from inventory.json. Omit to use the default cluster.
    """
    return _json(pe_get(f"/vms/{vm_uuid}", {"include_vm_disk_config": True, "include_vm_nic_config": True}, host=_resolve_host(cluster_name)))


@mcp.tool()
def get_vm_nics(vm_uuid: str, cluster_name=None) -> str:
    """
    List all network interfaces (NICs) attached to a specific VM.

    Returns each NIC's network UUID, MAC address, IP addresses, and adapter type.

    Args:
        vm_uuid: The UUID of the VM. Obtain from list_vms or get_vm.
        cluster_name: Name from inventory.json. Omit to use the default cluster.
    """
    return _json(pe_get(f"/vms/{vm_uuid}", {"include_vm_nic_config": True}, host=_resolve_host(cluster_name)).get("vm_nics", []))


@mcp.tool()
def get_vm_disks(vm_uuid: str, cluster_name=None) -> str:
    """
    List all disks (virtual drives) attached to a specific VM.

    Returns each disk's index, device bus (SCSI, IDE, etc.), size in bytes,
    backing storage container, and data source image if applicable.

    Args:
        vm_uuid: The UUID of the VM. Obtain from list_vms or get_vm.
        cluster_name: Name from inventory.json. Omit to use the default cluster.
    """
    return _json(pe_get(f"/vms/{vm_uuid}", {"include_vm_disk_config": True}, host=_resolve_host(cluster_name)).get("vm_disk_info", []))


# ---------------------------------------------------------------------------
# Networking tools
# ---------------------------------------------------------------------------


@mcp.tool()
def list_subnets(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all networks (VLANs) configured on a Prism Element cluster.

    Returns each network's UUID, name, VLAN ID, and IP configuration.

    Args:
        cluster_name: Name from inventory.json. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return _json(pe_get("/networks/", {"count": limit, "page": page}, host=_resolve_host(cluster_name)))


# ---------------------------------------------------------------------------
# Image tools
# ---------------------------------------------------------------------------


@mcp.tool()
def list_images(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all disk images stored in the Prism Element image service.

    Returns each image's UUID, name, image type (DISK_IMAGE or ISO_IMAGE),
    size in bytes, creation time, and current availability status.

    Args:
        cluster_name: Name from inventory.json. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return _json(pe_get("/images/", {"count": limit, "page": page}, host=_resolve_host(cluster_name)))


# ---------------------------------------------------------------------------
# Prism Central tools (v4.0 API — GET-based, OData query params)
# ---------------------------------------------------------------------------

# v4 endpoint paths
_PC_CLUSTERS  = "/api/clustermgmt/v4.0/config/clusters"
_PC_HOSTS     = "/api/clustermgmt/v4.0/config/hosts"
_PC_VMS       = "/api/vmm/v4.0/ahv/config/vms"
_PC_SUBNETS   = "/api/networking/v4.0/config/subnets"
_PC_IMAGES    = "/api/vmm/v4.0/content/images"


@mcp.tool()
def list_pc_clusters(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all clusters registered with and managed by a Prism Central instance.

    Returns cluster summaries including name, extId, AOS version, and node count
    across all PE clusters visible to that Prism Central.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return _json(pc_v4_get(_PC_CLUSTERS, params=params, host=_resolve_pc_host(pc_name)))


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
    return _json(pc_v4_get(_PC_VMS, params=params, host=_resolve_pc_host(pc_name)))


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
    return _json(pc_v4_get(f"{_PC_VMS}/{vm_extid}", host=_resolve_pc_host(pc_name)))


@mcp.tool()
def list_pc_hosts(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all hosts (nodes) across all clusters managed by a Prism Central instance.

    Returns host summaries including name, extId, cluster, CPU/memory capacity,
    hypervisor version, and current node state.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return _json(pc_v4_get(_PC_HOSTS, params=params, host=_resolve_pc_host(pc_name)))


@mcp.tool()
def list_pc_subnets(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all subnets (VLANs/overlays) across all clusters managed by a Prism Central instance.

    Returns each subnet's extId, name, type (VLAN or OVERLAY), VLAN ID,
    and IP configuration.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return _json(pc_v4_get(_PC_SUBNETS, params=params, host=_resolve_pc_host(pc_name)))


@mcp.tool()
def list_pc_images(pc_name=None, limit: int = 50, page: int = 0) -> str:
    """
    List all images managed by a Prism Central instance.

    Returns each image's extId, name, image type (DISK_IMAGE or ISO_IMAGE),
    size in bytes, and current availability state.

    Args:
        pc_name: Name from inventory.yaml (prism_central section). Omit to use the default PC.
        limit: Maximum number of results to return, up to 100 (default 50).
        page: Zero-based page index for pagination (default 0).
    """
    params = {"$page": page, "$limit": min(limit, 100)}
    return _json(pc_v4_get(_PC_IMAGES, params=params, host=_resolve_pc_host(pc_name)))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
