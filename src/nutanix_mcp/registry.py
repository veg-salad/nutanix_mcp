"""Inventory loading, host-resolution helpers, and shared JSON serialiser.

All tool modules import from here rather than duplicating inventory logic.

Inventory path resolution order:
  1. NUTANIX_MCP_INVENTORY environment variable
  2. ./inventory.yaml  (current working directory — set by mcp.json env)
  3. ~/.nutanix_mcp/inventory.yaml
  4. Source-layout relative fallback (for editable installs from the repo root)
"""

import json
import os

import yaml

from nutanix_mcp.credentials import (
    get_pe_credentials,
    get_pc_credentials,
    get_move_credentials,
)


def _find_inventory() -> str | None:
    """Return the path to inventory.yaml, or None if not found."""
    # 1. Explicit env override
    env_path = os.environ.get("NUTANIX_MCP_INVENTORY", "")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. CWD
    cwd_path = os.path.join(os.getcwd(), "inventory.yaml")
    if os.path.exists(cwd_path):
        return cwd_path

    # 3. ~/.nutanix_mcp/inventory.yaml
    home_path = os.path.join(os.path.expanduser("~"), ".nutanix_mcp", "inventory.yaml")
    if os.path.exists(home_path):
        return home_path

    # 4. Source-layout repo fallback (for editable dev installs)
    repo_rel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "inventory.yaml")
    repo_abs = os.path.normpath(repo_rel)
    if os.path.exists(repo_abs):
        return repo_abs

    return None


def _load_yaml_section(section: str) -> list:
    path = _find_inventory()
    if not path:
        return []
    with open(path) as f:
        data = yaml.safe_load(f)
    return (data or {}).get(section, [])


INVENTORY = _load_yaml_section("clusters")
PC_INVENTORY = _load_yaml_section("prism_central")
MOVE_INVENTORY = _load_yaml_section("move_instances")


# ---------------------------------------------------------------------------
# Resolve helpers — return full connection + credential dicts
# ---------------------------------------------------------------------------

def resolve_cluster(cluster_name=None) -> dict:
    """Return host + credentials dict for the named PE cluster.

    The returned dict has keys: host, username, password, verify_ssl.
    These match the keyword arguments accepted by client.pe_get().
    """
    names = [e["name"] for e in INVENTORY]
    if not INVENTORY:
        raise ValueError(
            "inventory.yaml has no clusters defined. "
            "Run 'nutanix-mcp configure' to register clusters."
        )
    if not cluster_name:
        if len(INVENTORY) == 1:
            entry = INVENTORY[0]
        else:
            raise ValueError(
                f"Multiple clusters in inventory — specify cluster_name. "
                f"Available: {names}"
            )
    else:
        for e in INVENTORY:
            if e["name"].lower() == cluster_name.lower():
                entry = e
                break
        else:
            raise ValueError(
                f"Cluster '{cluster_name}' not found in inventory.yaml. "
                f"Available: {names}"
            )
    creds = get_pe_credentials(entry["name"])
    return {"host": entry["pe_host"], **creds}


def resolve_pc_instance(pc_name=None) -> dict:
    """Return host + credentials dict for the named Prism Central instance.

    The returned dict has keys: host, api_key, username, password, verify_ssl.
    These match the keyword arguments accepted by client.pc_v4_get().
    """
    names = [e["name"] for e in PC_INVENTORY]
    if not PC_INVENTORY:
        raise ValueError(
            "inventory.yaml has no prism_central entries. "
            "Run 'nutanix-mcp configure' to register PC instances."
        )
    if not pc_name:
        if len(PC_INVENTORY) == 1:
            entry = PC_INVENTORY[0]
        else:
            raise ValueError(
                f"Multiple PC instances in inventory — specify pc_name. "
                f"Available: {names}"
            )
    else:
        for e in PC_INVENTORY:
            if e["name"].lower() == pc_name.lower():
                entry = e
                break
        else:
            raise ValueError(
                f"Prism Central '{pc_name}' not found in inventory.yaml. "
                f"Available: {names}"
            )
    creds = get_pc_credentials(entry["name"])
    return {"host": entry["pc_host"], **creds}


def resolve_move_instance(move_name=None) -> dict:
    """Return host + credentials dict for the named Move appliance.

    The returned dict has keys: host, username, password, verify_ssl.
    These match the keyword arguments accepted by client.move_get().
    """
    names = [e["name"] for e in MOVE_INVENTORY]
    if not MOVE_INVENTORY:
        raise ValueError(
            "inventory.yaml has no move_instances defined. "
            "Run 'nutanix-mcp configure' to register Move appliances."
        )
    if not move_name:
        if len(MOVE_INVENTORY) == 1:
            entry = MOVE_INVENTORY[0]
        else:
            raise ValueError(
                f"Multiple Move appliances in inventory — specify move_name. "
                f"Available: {names}"
            )
    else:
        for e in MOVE_INVENTORY:
            if e["name"].lower() == move_name.lower():
                entry = e
                break
        else:
            raise ValueError(
                f"Move appliance '{move_name}' not found in inventory.yaml. "
                f"Available: {names}"
            )
    creds = get_move_credentials(entry["name"])
    return {"host": entry["move_host"], **creds}


# ---------------------------------------------------------------------------
# Thin wrappers for backward compatibility
# ---------------------------------------------------------------------------

def resolve_host(cluster_name=None) -> str:
    return resolve_cluster(cluster_name)["host"]


def resolve_pc_host(pc_name=None) -> str:
    return resolve_pc_instance(pc_name)["host"]


# ---------------------------------------------------------------------------
# JSON serialiser
# ---------------------------------------------------------------------------

def json_response(data) -> str:
    """Serialise data to a pretty-printed JSON string."""
    return json.dumps(data, indent=2, default=str)
