# Nutanix Prism MCP for GitHub Copilot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Ask GitHub Copilot questions about your Nutanix environment in plain English — VMs, hosts, storage, networking, alerts, tasks, protection domains, resource utilization, and more — directly from VS Code.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [VS Code](https://code.visualstudio.com/)
- GitHub Copilot + Copilot Chat extensions (VS Code will prompt you to install them)

## Setup

### 1. Run the setup script

Open a terminal, navigate to the `nutanix_mcp` folder, and run:

```bash
python setup.py
```

This single command will:
- Verify your Python version (3.10+ required)
- Install all Python dependencies
- Prompt for your **Prism Element (PE)** and **Prism Central (PC)** credentials and write `.vscode/mcp.json`
- Prompt you to register your Prism Central instance(s) and Prism Element cluster(s) and write `inventory.yaml`

Credentials are optional at setup time — press Enter to skip any prompt and fill in `.vscode/mcp.json` manually later.

> **Already set up?** Re-run `python setup.py` at any time to add missing credentials or append more clusters / PC instances.

### 2. Open the folder in VS Code

```
File → Open Folder → select the nutanix_mcp folder
```

VS Code will recommend the GitHub Copilot extensions — install them if not already present.

### 3. Confirm the MCP server is active

Open the Copilot Chat panel, click the **Tools** (plug) icon, and confirm `nutanix-prism` is listed and enabled.

## Configuration

### Credentials — `.vscode/mcp.json`

All credentials live in one place: `.vscode/mcp.json` (created by `setup.py`, gitignored).

| Variable | Description |
|---|---|
| `NUTANIX_PE_USERNAME` | Prism Element username (e.g. `admin`) |
| `NUTANIX_PE_PASSWORD` | Prism Element password |
| `NUTANIX_VERIFY_SSL` | `true` / `false` — whether to verify TLS certificates (default `false`) |
| `NUTANIX_PC_USERNAME` | Prism Central username (used if no API key is set) |
| `NUTANIX_PC_PASSWORD` | Prism Central password (used if no API key is set) |
| `NUTANIX_PC_API_KEY` | Prism Central API key — preferred over username/password when set |

> PE and PC credentials are kept separate because most organisations use different accounts for each.

### Cluster inventory — `inventory.yaml`

Register your Prism Central instances and PE clusters here. Edit directly or re-run `setup.py`.

```yaml
prism_central:
  - name: PROD-PC-1
    pc_host: 192.168.1.50

clusters:
  - name: PROD-CLUSTER-1
    pe_host: 192.168.1.100
  - name: PROD-CLUSTER-2
    pe_host: 192.168.1.200
```

- `prism_central[].name` — label used in prompts (e.g. *"from PC PROD-PC-1"*); pass as `pc_name` to PC tools
- `prism_central[].pc_host` — Prism Central IP or FQDN
- `clusters[].name` — label used in prompts (e.g. *"from cluster PROD-CLUSTER-1"*); pass as `cluster_name` to PE tools
- `clusters[].pe_host` — Prism Element IP or FQDN
- Single entry → selected automatically; multiple entries → specify the name in your prompt

## Usage

Switch Copilot Chat to **Agent mode** and ask questions like:

```
List all VMs and their power state
How much free storage does the cluster have?
Show me any critical alerts
What tasks are currently running?
Show resource utilization for the cluster over the last hour
Get CPU and memory stats for VM <uuid>
Which hosts are in the cluster and what model are they?
Show me the NICs for VM xyz
List all protection domains
```

Target a specific cluster or PC by name:

```
List all hosts from cluster PROD-CLUSTER-1
Show VMs on PROD-CLUSTER-2
List all VMs managed by PC PROD-PC-1
Show subnets across all clusters from Prism Central PROD-PC-1
```

Copilot will call `list_inventory` automatically to discover available entries when needed.

## Project structure

```
nutanix_mcp/
├── inventory.yaml         Cluster & PC registry
├── setup.py               One-time setup wizard
├── available_tools.md     Full tool reference
└── src/
    ├── server.py          Entry point — imports tool modules, starts MCP server
    ├── app.py             Shared FastMCP instance
    ├── registry.py        Inventory loading, host resolvers, JSON helper
    ├── client.py          HTTP clients for PE v2.0 and PC v4.0 APIs
    └── tools/
        ├── inventory.py       list_inventory
        ├── pe_cluster.py      list_clusters, get_cluster
        ├── pe_hosts.py        list_hosts, get_host
        ├── pe_vms.py          list_vms, get_vm, get_vm_nics, get_vm_disks
        ├── pe_storage.py      list_storage_containers, get_storage_container,
        │                      list_storage_pools, list_disks, get_disk
        ├── pe_networking.py   list_subnets
        ├── pe_images.py       list_images
        ├── pe_alerts.py       list_alerts, list_events
        ├── pe_ops.py          list_protection_domains, list_tasks
        ├── pe_stats.py        get_vm_stats, get_host_stats,
        │                      get_cluster_stats, get_storage_container_stats
        ├── pc_clusters.py     list_pc_clusters, get_pc_cluster
        ├── pc_vms.py          list_pc_vms, get_pc_vm, list_pc_vm_disks, list_pc_vm_nics
        ├── pc_hosts.py        list_pc_hosts, get_pc_host
        ├── pc_networking.py   list_pc_subnets
        ├── pc_images.py       list_pc_images
        ├── pc_storage.py      list_pc_storage_containers
        ├── pc_alerts.py       list_pc_alerts, get_pc_alert
        ├── pc_tasks.py        list_pc_tasks, get_pc_task
        └── pc_categories.py   list_pc_categories, get_pc_category
```

See [available_tools.md](available_tools.md) for the full tool reference including parameters, return values, and source modules.

## Notes

- All tools are **read-only** — no changes are made to your cluster
- PE tools use the Prism Element **v2.0** REST API (per-cluster)
- PC tools use the Prism Central **v4.0** REST API (cross-cluster); `list_pc_alerts` uses the v2.0 gateway (GET with query params) and `get_pc_alert` uses the v3 API — both are cross-cluster via PC, as the v4 alerting namespace is not yet available on all PC versions
- PC tools use `extId` as the entity identifier; use values from `list_*` calls as input to `get_*` calls
- Stats metrics are returned in **ppm** (parts per million); divide by 10,000 to convert to a percentage
- Transport is **stdio** — the server runs locally and is managed by VS Code via `.vscode/mcp.json`

## Disclaimer

This is an independent, community-built project and is **not an official Nutanix product**. It is not affiliated with, endorsed by, or supported by Nutanix, Inc. in any way. Nutanix and Prism are trademarks of Nutanix, Inc.

Use this tool at your own discretion. While all operations are read-only, you are responsible for ensuring it is used appropriately within your environment. The author provides this project as-is, without warranty of any kind — see the [MIT License](LICENSE) for full terms.

