# Available Tools

All tools are **read-only**. No changes are made to your Nutanix environment.

PE tools accept an optional `cluster_name` parameter resolved from `inventory.yaml`.  
PC tools accept an optional `pc_name` parameter resolved from `inventory.yaml`.  
When only one entry is defined the parameter is optional and that entry is selected automatically.  
PC tools use `extId` (not UUID) as the entity identifier — use values returned by `list_*` tools as input to `get_*` tools.

---

## Inventory

| Tool | Module | Description |
|---|---|---|
| `list_inventory` | `tools/inventory.py` | List all registered Prism Central instances and PE clusters from `inventory.yaml`. Returns `prism_central` entries (use name as `pc_name`) and `clusters` entries (use name as `cluster_name`). |

---

## Prism Element (PE) tools — v2.0 REST API

### Cluster

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_clusters` | `tools/pe_cluster.py` | `cluster_name` | Cluster summary: name, UUID, AOS version, hypervisor types, redundancy factor. |
| `get_cluster` | `tools/pe_cluster.py` | `cluster_name` | Full cluster config: nodes, network config, storage summary, AOS version, fault tolerance state. |

### Hosts

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_hosts` | `tools/pe_hosts.py` | `cluster_name`, `limit`, `page` | All nodes: name, UUID, IPs, CPU/memory capacity, hypervisor version, status. |
| `get_host` | `tools/pe_hosts.py` | `host_uuid`*, `cluster_name` | Full node detail: hardware, CPU/memory usage, network interfaces, disk inventory, status. |

### Controller VMs (CVMs)

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_cvms` | `tools/pe_cvms.py` | `cluster_name`, `limit`, `page` | All CVMs (one per node): CVM IP, backplane IP, hypervisor IP, state, metadata store status, oplog %, hardware model/serial. |
| `get_cvm` | `tools/pe_cvms.py` | `host_uuid`*, `cluster_name` | CVM detail for a specific node: IPs, hypervisor type/version, state, metadata status, oplog %, hardware. |

### Virtual Machines

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_vms` | `tools/pe_vms.py` | `cluster_name`, `limit`, `page`, `search_string`, `include_vm_disk_config`, `include_vm_nic_config` | All VMs: name, UUID, power state, vCPU, memory, host placement. |
| `get_vm` | `tools/pe_vms.py` | `vm_uuid`*, `cluster_name` | Full VM config: vCPU/memory spec, boot config, guest OS, power state, placement. |
| `get_vm_nics` | `tools/pe_vms.py` | `vm_uuid`*, `cluster_name` | NICs attached to a VM: network UUID, MAC, IPs, adapter type. |
| `get_vm_disks` | `tools/pe_vms.py` | `vm_uuid`*, `cluster_name` | Disks attached to a VM: bus, index, size, backing container, source image. |

### Storage

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_storage_containers` | `tools/pe_storage.py` | `cluster_name`, `limit`, `page` | All datastores: name, UUID, capacity, usage, compression/dedup/EC settings. |
| `get_storage_container` | `tools/pe_storage.py` | `container_name`*, `cluster_name` | Full container detail: capacity, usage, compression ratio, dedup savings, replication factor, EC state. |
| `list_storage_pools` | `tools/pe_storage.py` | `cluster_name`, `limit`, `page` | All storage pools: UUID, name, total/used capacity, associated disks. |
| `list_disks` | `tools/pe_storage.py` | `cluster_name`, `limit`, `page` | All physical disks: UUID, serial, model, vendor, size, type (SSD/HDD), tier, state. |
| `get_disk` | `tools/pe_storage.py` | `disk_uuid`*, `cluster_name` | Full disk detail: serial, model, vendor, size, tier, CVM IP, host UUID, status. |

### Networking

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_subnets` | `tools/pe_networking.py` | `cluster_name`, `limit`, `page` | All VLANs: UUID, name, VLAN ID, IP config. |

### Images

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_images` | `tools/pe_images.py` | `cluster_name`, `limit`, `page` | All images: UUID, name, type (DISK_IMAGE/ISO_IMAGE), size, creation time, availability status. |

### Alerts & Events

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_alerts` | `tools/pe_alerts.py` | `cluster_name`, `limit`, `page`, `resolved`, `acknowledged` | Alerts: UUID, severity (CRITICAL/WARNING/INFO), title, message, creation time, resolution status. |
| `list_events` | `tools/pe_alerts.py` | `cluster_name`, `limit`, `page` | Audit events: type, message, source entity, creation time. |

### Operations

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_protection_domains` | `tools/pe_ops.py` | `cluster_name`, `limit`, `page` | DR/backup configs: name, type, active/standby state, associated VMs. |
| `list_tasks` | `tools/pe_ops.py` | `cluster_name`, `limit`, `include_completed` | Recent tasks: UUID, type, status (Running/Succeeded/Failed), progress %, timestamps. |

### Resource Utilization Stats

Stats return time-series data. **ppm values ÷ 10,000 = percentage** (e.g. 500,000 ppm = 50 %).  
All stat tools accept `duration_secs` (default `3600` = last hour) and `interval_secs` (default `60`).

| Tool | Module | Parameters | Metrics returned |
|---|---|---|---|
| `get_vm_stats` | `tools/pe_stats.py` | `vm_uuid`*, `cluster_name`, `duration_secs`, `interval_secs` | CPU % (ppm), memory % (ppm), IOPS, total/read/write bandwidth (kB/s), read/write latency (µs), network RX/TX (bytes) |
| `get_host_stats` | `tools/pe_stats.py` | `host_uuid`*, `cluster_name`, `duration_secs`, `interval_secs` | CPU % (ppm), memory % (ppm), IOPS, bandwidth (kB/s), read/write latency (µs) |
| `get_cluster_stats` | `tools/pe_stats.py` | `cluster_name`, `duration_secs`, `interval_secs` | CPU % (ppm), memory % (ppm), IOPS, bandwidth (kB/s), read/write latency (µs), storage usage/capacity (bytes) |
| `get_storage_container_stats` | `tools/pe_stats.py` | `container_name`*, `cluster_name`, `duration_secs`, `interval_secs` | IOPS, bandwidth (kB/s), read/write latency (µs), storage usage/capacity (bytes) |

---

## Prism Central (PC) tools — v4.0 REST API

PC tools operate across **all clusters** managed by the target Prism Central instance.  
Responses use `extId` as the unique identifier. Use `extId` values from `list_*` calls as input to `get_*` calls.  
`list_*` tools support OData pagination (`page`, `limit`) and most support an OData `filter` parameter.

### Clusters

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_clusters` | `tools/pc_clusters.py` | `pc_name`, `limit`, `page` | All managed clusters: name, extId, AOS version, node count. |
| `get_pc_cluster` | `tools/pc_clusters.py` | `cluster_extid`*, `pc_name` | Full cluster config: AOS version, node count, cluster function, network config, management server details. |

### Virtual Machines

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_vms` | `tools/pc_vms.py` | `pc_name`, `limit`, `page`, `filter` | VMs across all clusters: name, extId, power state, vCPU, memory, cluster placement. OData filter supported. |
| `get_pc_vm` | `tools/pc_vms.py` | `vm_extid`*, `pc_name` | Full VM spec: vCPU/memory, disks, NICs, boot config, guest OS, power state, cluster. |
| `list_pc_vm_disks` | `tools/pc_vms.py` | `vm_extid`*, `pc_name`, `limit`, `page` | Disks attached to a VM: extId, bus (SCSI/IDE/SATA), index, size, container, source image. |
| `list_pc_vm_nics` | `tools/pc_vms.py` | `vm_extid`*, `pc_name`, `limit`, `page` | NICs attached to a VM: extId, network extId, VLAN mode, MAC, IPs, connected state. |

### Hosts

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_hosts` | `tools/pc_hosts.py` | `pc_name`, `limit`, `page` | All nodes across all clusters: name, extId, cluster, CPU/memory capacity, hypervisor version, state. |
| `get_pc_host` | `tools/pc_hosts.py` | `host_extid`*, `pc_name` | Full node detail: CPU model, cores/threads, memory capacity, hypervisor version, CVM IP, state. |

### Networking

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_subnets` | `tools/pc_networking.py` | `pc_name`, `limit`, `page` | All subnets across clusters: extId, name, type (VLAN/OVERLAY), VLAN ID, IP config. |

### Images

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_images` | `tools/pc_images.py` | `pc_name`, `limit`, `page` | All images: extId, name, type (DISK_IMAGE/ISO_IMAGE), size, availability state. |

### Storage

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_storage_containers` | `tools/pc_storage.py` | `pc_name`, `limit`, `page` | Storage containers across all clusters: extId, name, cluster, capacity, usage, compression/dedup/EC settings. |

### Alerts

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_alerts` | `tools/pc_alerts.py` | `pc_name`, `limit`, `page`, `filter` | Alerts across all clusters: extId, severity (CRITICAL/WARNING/INFO), title, message, timestamps, resolution status. OData filter supported. |
| `get_pc_alert` | `tools/pc_alerts.py` | `alert_extid`*, `pc_name` | Full alert detail: severity, impacted entities, root cause analysis, resolution status, timestamps. |

### Tasks

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_tasks` | `tools/pc_tasks.py` | `pc_name`, `limit`, `page`, `filter` | Tasks across all clusters: extId, operation type, status (Queued/Running/Succeeded/Failed), progress %, timestamps. OData filter supported. |
| `get_pc_task` | `tools/pc_tasks.py` | `task_extid`*, `pc_name` | Full task detail: operation type, status, progress, error details, impacted entities. |

### Categories

| Tool | Module | Parameters | Description |
|---|---|---|---|
| `list_pc_categories` | `tools/pc_categories.py` | `pc_name`, `limit`, `page` | All category key/value tags: extId, key, value, description. |
| `get_pc_category` | `tools/pc_categories.py` | `category_extid`*, `pc_name` | Full category detail: key, value, description, associated entity count. |

---

`*` = required parameter
