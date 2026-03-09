"""PE storage tools — containers, pools, and physical disks."""

from app import mcp
from client import pe_get
from registry import json_response, resolve_host


@mcp.tool()
def list_storage_containers(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all storage containers (datastores) in a Prism Element cluster.

    Returns each container's name, UUID, capacity, usage, compression,
    dedup, and erasure-coding settings.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return json_response(pe_get("/storage_containers/", {"count": limit, "page": page}, host=resolve_host(cluster_name)))


@mcp.tool()
def get_storage_container(container_name: str, cluster_name=None) -> str:
    """
    Get full details of a storage container by name or UUID.

    Returns capacity, usage, compression ratio, dedup savings, replication factor,
    erasure coding state, and associated storage pool.

    Args:
        container_name: Name or UUID of the storage container. Obtain from list_storage_containers.
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(pe_get(f"/storage_containers/{container_name}", host=resolve_host(cluster_name)))


@mcp.tool()
def list_storage_pools(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all storage pools in a Prism Element cluster.

    Returns each pool's UUID, name, total capacity, used capacity,
    and associated disks.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return json_response(pe_get("/storage_pools/", {"count": limit, "page": page}, host=resolve_host(cluster_name)))


@mcp.tool()
def list_disks(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all physical disks across all nodes in a Prism Element cluster.

    Returns each disk's UUID, serial number, model, vendor, size in bytes,
    disk type (SSD/HDD), storage tier, and operational state.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return json_response(pe_get("/disks/", {"count": limit, "page": page}, host=resolve_host(cluster_name)))


@mcp.tool()
def get_disk(disk_uuid: str, cluster_name=None) -> str:
    """
    Get full details of a specific physical disk by its UUID.

    Returns serial number, model, vendor, size, storage tier, CVM IP, host UUID,
    and current operational/online status.

    Args:
        disk_uuid: UUID of the disk. Obtain from list_disks.
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    return json_response(pe_get(f"/disks/{disk_uuid}", host=resolve_host(cluster_name)))
