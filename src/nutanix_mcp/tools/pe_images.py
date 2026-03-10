"""PE image tools — disk and ISO images in the image service."""

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pe_get
from nutanix_mcp.registry import json_response, resolve_cluster


@mcp.tool()
def list_images(cluster_name=None, limit: int = 50, page: int = 1) -> str:
    """
    List all disk images stored in the Prism Element image service.

    Returns each image's UUID, name, image type (DISK_IMAGE or ISO_IMAGE),
    size in bytes, creation time, and current availability status.
    Note: the Image Service is only available on AHV clusters. This tool
    returns a 422 error on VMware ESXi or Hyper-V clusters.

    Args:
        cluster_name: Name from inventory.yaml. Omit to use the default cluster.
        limit: Maximum number of results to return (default 50).
        page: Page number for pagination (1-based).
    """
    return json_response(pe_get("/images/", {"count": limit, "page": page}, **resolve_cluster(cluster_name)))
