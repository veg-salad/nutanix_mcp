"""PE storage tools — containers, pools, and physical disks."""

import re

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pe_get
from nutanix_mcp.registry import json_response, resolve_cluster

_UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


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
    return json_response(pe_get("/storage_containers/", {"count": limit, "page": page}, **resolve_cluster(cluster_name)))


@mcp.tool()
def get_storage_container(container_name: str, cluster_name=None) -> str:
    """
    Get full details of a storage container by name or UUID.

    Returns capacity, usage, compression ratio, dedup savings, replication factor,
    erasure coding state, and associated storage pool.

    Args:
        container_name: Name or UUID of the storage container. Obtain from list_storage_containers.
            The PE v2.0 API only supports direct path lookup by UUID; if a name is supplied,
            the tool resolves it by listing all containers and matching by 'name' field.
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
    """
    cluster = resolve_cluster(cluster_name)
    if _UUID_RE.match(container_name):
        return json_response(pe_get(f"/storage_containers/{container_name}", **cluster))
    # Name supplied — enumerate and match
    page, page_size = 1, 100
    while True:
        data = pe_get("/storage_containers/", {"count": page_size, "page": page}, **cluster)
        entities = data.get("entities", [])
        for entity in entities:
            if entity.get("name") == container_name:
                uuid = entity.get("storage_container_uuid")
                return json_response(pe_get(f"/storage_containers/{uuid}", **cluster))
        meta = data.get("metadata", {})
        if meta.get("end_index", 0) >= meta.get("grand_total_entities", 0):
            break
        page += 1
    return json_response({"error": f"Storage container '{container_name}' not found"})


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
    # On AOS 6.x the v2.0 /storage_pools/ endpoint returns 404; the correct path is v1.
    return json_response(pe_get("/storage_pools", {"count": limit, "page": page}, base_path="/PrismGateway/services/rest/v1", **resolve_cluster(cluster_name)))


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
    return json_response(pe_get("/disks/", {"count": limit, "page": page}, **resolve_cluster(cluster_name)))


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
    return json_response(pe_get(f"/disks/{disk_uuid}", **resolve_cluster(cluster_name)))
