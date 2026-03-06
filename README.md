# Nutanix Prism MCP for GitHub Copilot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Ask GitHub Copilot questions about your Nutanix cluster in plain English — VMs, hosts, storage, networking, and images — directly from VS Code.

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
- Prompt for your **Prism Element (PE)** and **Prism Central (PC)** credentials and create `.vscode/mcp.json`
- Prompt you to register your Prism Central instance(s) and Prism Element cluster(s) and write `inventory.yaml`

> **Already have a setup?** Re-run `python setup.py` at any time to add missing credentials or append more clusters / PC instances.

### 2. Open the folder in VS Code

```
File → Open Folder → select the nutanix_mcp folder
```

VS Code will recommend the GitHub Copilot extensions — install them if not already present.

### 3. Start the MCP server

> **Adding clusters or PC instances later?** Re-run `python setup.py` at any time — it will show existing entries and let you append more. You can also edit `inventory.yaml` directly:
> ```yaml
> prism_central:
>   - name: PROD-PC-1
>     pc_host: 192.168.1.50
>
> clusters:
>   - name: PROD-CLUSTER-1
>     pe_host: 192.168.1.100
>   - name: PROD-CLUSTER-2
>     pe_host: 192.168.1.200
> ```
> - `prism_central[].name` — label used in Copilot Chat prompts (e.g. *"from PC PROD-PC-1"*); pass as `pc_name` to PC tools
> - `prism_central[].pc_host` — Prism Central IP or FQDN
> - `clusters[].name` — label used in Copilot Chat prompts (e.g. *"from cluster PROD-CLUSTER-1"*); pass as `cluster_name` to PE tools
> - `clusters[].pe_host` — Prism Element IP or FQDN
> - Single entry → selected automatically; multiple entries → specify `pc_name` / `cluster_name` in your prompt

Open the Copilot Chat panel, click the **Tools** (plug) icon, and confirm `nutanix-prism` is listed and enabled.

## Usage

Switch Copilot Chat to **Agent mode** and ask questions like:

- *"List all VMs and their power state"*
- *"How much free storage does the cluster have?"*
- *"Show me the NICs for VM xyz"*
- *"Which hosts are in the cluster and what model are they?"*

You can also target a specific cluster or Prism Central by name:

- *"List all hosts from cluster SAMPLE-CLUSTER-1"*
- *"Show VMs on SAMPLE-CLUSTER-2"*
- *"List all VMs managed by PC SAMPLE-PC-1"*
- *"Show subnets across all clusters from Prism Central SAMPLE-PC-1"*
- *"What clusters are available?"*

Copilot will call `list_inventory` automatically to discover available PC instances and clusters when needed.

## Available tools

| Tool | Description |
|---|---|
| `list_inventory` | List all Prism Central instances and PE clusters from `inventory.yaml` |
| **Prism Element (PE) tools** | |
| `list_clusters` / `get_cluster` | Cluster summary and full config |
| `list_hosts` / `get_host` | Nodes — hardware, CPU/memory, status |
| `list_vms` / `get_vm` | Virtual machines — spec, power state, placement |
| `get_vm_nics` | NICs attached to a VM |
| `get_vm_disks` | Disks attached to a VM |
| `list_subnets` | VLANs and network config |
| `list_images` | Disk images in the image service |
| **Prism Central (PC) tools** | |
| `list_pc_clusters` | All clusters registered with Prism Central |
| `list_pc_vms` / `get_pc_vm` | VMs across all managed clusters |
| `list_pc_hosts` | Hosts across all managed clusters |
| `list_pc_subnets` | Subnets across all managed clusters |
| `list_pc_images` | Images managed by Prism Central |

PE tools accept an optional `cluster_name` parameter; PC tools accept an optional `pc_name` parameter — both resolved from `inventory.yaml`. Omit when only one entry is defined.

All tools are **read-only**. No changes are made to your cluster.
