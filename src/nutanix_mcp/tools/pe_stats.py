"""PE resource utilization stats — time-series metrics for VMs, hosts, cluster, and containers.

All ppm (parts-per-million) metrics can be converted to a percentage by dividing by 10,000.
Example: 500,000 ppm → 50 %.
"""

import re
import time

from nutanix_mcp.app import mcp
from nutanix_mcp.client import pe_get
from nutanix_mcp.registry import json_response, resolve_cluster

_UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


def _resolve_container_uuid(container_name: str, cluster: dict) -> str:
    """Resolve a storage container name to its UUID; return as-is if already a UUID."""
    if _UUID_RE.match(container_name):
        return container_name
    page, page_size = 1, 100
    while True:
        data = pe_get("/storage_containers/", {"count": page_size, "page": page}, **cluster)
        for entity in data.get("entities", []):
            if entity.get("name") == container_name:
                return entity["storage_container_uuid"]
        meta = data.get("metadata", {})
        if meta.get("end_index", 0) >= meta.get("grand_total_entities", 0):
            break
        page += 1
    raise ValueError(f"Storage container '{container_name}' not found")


# ---------------------------------------------------------------------------
# Default metric sets
# ---------------------------------------------------------------------------

_VM_METRICS = [
    "hypervisor_cpu_usage_ppm",               # Guest vCPU utilisation  (ppm → %)
    "memory_usage_ppm",                        # Guest memory utilisation (ppm → %)
    "controller_num_iops",                     # Total storage IOPS
    "controller_io_bandwidth_kBps",            # Total I/O bandwidth (kB/s)
    "controller_read_io_bandwidth_kBps",       # Read bandwidth (kB/s)
    "controller_write_io_bandwidth_kBps",      # Write bandwidth (kB/s)
    "controller_avg_read_io_latency_usecs",    # Avg read latency (µs)
    "controller_avg_write_io_latency_usecs",   # Avg write latency (µs)
    "hypervisor_num_net_bytes_received",       # Network RX (bytes)
    "hypervisor_num_net_bytes_transmitted",    # Network TX (bytes)
]

_HOST_METRICS = [
    "hypervisor_cpu_usage_ppm",               # Host CPU utilisation  (ppm → %)
    "hypervisor_memory_usage_ppm",            # Host memory utilisation (ppm → %)
    "controller_num_iops",                    # Storage controller IOPS
    "controller_io_bandwidth_kBps",           # Storage I/O bandwidth (kB/s)
    "controller_avg_read_io_latency_usecs",   # Avg read latency (µs)
    "controller_avg_write_io_latency_usecs",  # Avg write latency (µs)
]

_CLUSTER_METRICS = [
    "hypervisor_cpu_usage_ppm",               # Cluster-wide CPU utilisation  (ppm → %)
    "hypervisor_memory_usage_ppm",            # Cluster-wide memory utilisation (ppm → %)
    "controller_num_iops",                    # Cluster IOPS
    "controller_io_bandwidth_kBps",           # Cluster I/O bandwidth (kB/s)
    "controller_avg_read_io_latency_usecs",   # Avg read latency (µs)
    "controller_avg_write_io_latency_usecs",  # Avg write latency (µs)
]

_CONTAINER_METRICS = [
    "controller_num_iops",                    # Container IOPS
    "controller_io_bandwidth_kBps",           # Container I/O bandwidth (kB/s)
    "controller_avg_read_io_latency_usecs",   # Avg read latency (µs)
    "controller_avg_write_io_latency_usecs",  # Avg write latency (µs)
]


def _stats_params(metrics, duration_secs, interval_secs):
    """Build the list-of-tuples params block used by all PE /stats/ endpoints."""
    now_usecs = int(time.time() * 1_000_000)
    start_usecs = now_usecs - duration_secs * 1_000_000
    return (
        [("metrics", m) for m in metrics]
        + [
            ("startTimeInUsecs", start_usecs),
            ("endTimeInUsecs", now_usecs),
            ("intervalInSecs", interval_secs),
        ]
    )


# ---------------------------------------------------------------------------
# Stat tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_vm_stats(
    vm_uuid: str,
    cluster_name=None,
    duration_secs: int = 3600,
    interval_secs: int = 60,
) -> str:
    """
    Get resource utilization time-series statistics for a VM.

    Returns CPU usage (ppm), memory usage (ppm), storage IOPS, I/O bandwidth
    (read/write), read/write latency (µs), and network RX/TX bytes over the
    requested time window.  Divide ppm values by 10,000 to get a percentage.
    Note: only supported on AHV clusters. VMware ESXi clusters return a 404
    because VM performance metrics are managed by vCenter, not by Nutanix CVM.

    Args:
        vm_uuid: UUID of the VM. Obtain from list_vms.
        cluster_name: Cluster name from inventory.yaml. Omit to use the default.
        duration_secs: Time window ending now, in seconds (default 3600 = last hour).
        interval_secs: Sampling interval in seconds (default 60).
    """
    return json_response(pe_get(
        f"/vms/{vm_uuid}/stats/",
        _stats_params(_VM_METRICS, duration_secs, interval_secs),
        **resolve_cluster(cluster_name),
    ))


@mcp.tool()
def get_host_stats(
    host_uuid: str,
    cluster_name=None,
    duration_secs: int = 3600,
    interval_secs: int = 60,
) -> str:
    """
    Get resource utilization time-series statistics for a host (node).

    Returns CPU usage (ppm), memory usage (ppm), storage IOPS, I/O bandwidth,
    and read/write latency (µs) over the requested time window.
    Divide ppm values by 10,000 to get a percentage.

    Args:
        host_uuid: UUID of the host. Obtain from list_hosts.
        cluster_name: Cluster name from inventory.yaml. Omit to use the default.
        duration_secs: Time window ending now, in seconds (default 3600 = last hour).
        interval_secs: Sampling interval in seconds (default 60).
    """
    return json_response(pe_get(
        f"/hosts/{host_uuid}/stats/",
        _stats_params(_HOST_METRICS, duration_secs, interval_secs),
        **resolve_cluster(cluster_name),
    ))


@mcp.tool()
def get_cluster_stats(
    cluster_name=None,
    duration_secs: int = 3600,
    interval_secs: int = 60,
) -> str:
    """
    Get cluster-wide resource utilization time-series statistics.

    Returns CPU usage (ppm), memory usage (ppm), storage IOPS, I/O bandwidth,
    read/write latency (µs), and total storage capacity/usage (bytes) over
    the requested time window.  Divide ppm values by 10,000 to get a percentage.

    Args:
        cluster_name: Cluster name from inventory.yaml. Omit to use the default.
        duration_secs: Time window ending now, in seconds (default 3600 = last hour).
        interval_secs: Sampling interval in seconds (default 60).
    """
    return json_response(pe_get(
        "/cluster/stats/",
        _stats_params(_CLUSTER_METRICS, duration_secs, interval_secs),
        **resolve_cluster(cluster_name),
    ))


@mcp.tool()
def get_storage_container_stats(
    container_name: str,
    cluster_name=None,
    duration_secs: int = 3600,
    interval_secs: int = 60,
) -> str:
    """
    Get I/O utilization time-series statistics for a storage container.

    Returns IOPS, I/O bandwidth, and read/write latency (µs) over the
    requested time window.  The PE v2.0 stats endpoint requires a UUID;
    if a container name is supplied the tool resolves it automatically.

    Args:
        container_name: Name or UUID of the storage container. Obtain from list_storage_containers.
        cluster_name: Cluster name from inventory.yaml. Omit to use the default.
        duration_secs: Time window ending now, in seconds (default 3600 = last hour).
        interval_secs: Sampling interval in seconds (default 60).
    """
    cluster = resolve_cluster(cluster_name)
    container_uuid = _resolve_container_uuid(container_name, cluster)
    return json_response(pe_get(
        f"/storage_containers/{container_uuid}/stats/",
        _stats_params(_CONTAINER_METRICS, duration_secs, interval_secs),
        **cluster,
    ))
