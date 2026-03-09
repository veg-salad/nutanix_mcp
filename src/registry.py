"""Inventory loading, host-resolution helpers, and shared JSON serialiser.

All tool modules import from here rather than duplicating inventory logic.
"""

import json
import os

import yaml

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


INVENTORY = _load_inventory()
PC_INVENTORY = _load_pc_inventory()


def resolve_host(cluster_name=None) -> str:
    """Return the PE host IP for cluster_name, or auto-select if only one cluster is defined."""
    names = [e["name"] for e in INVENTORY]

    if not INVENTORY:
        raise ValueError(
            "inventory.yaml has no clusters defined. "
            "Add at least one entry before using any tool."
        )

    if not cluster_name:
        if len(INVENTORY) == 1:
            return INVENTORY[0]["pe_host"]
        raise ValueError(
            f"Multiple clusters in inventory — specify cluster_name. "
            f"Available: {names}"
        )

    for entry in INVENTORY:
        if entry["name"].lower() == cluster_name.lower():
            return entry["pe_host"]

    raise ValueError(
        f"Cluster '{cluster_name}' not found in inventory.yaml. "
        f"Available: {names}"
    )


def resolve_pc_host(pc_name=None) -> str:
    """Return the PC host IP for pc_name, or auto-select if only one PC instance is defined."""
    names = [e["name"] for e in PC_INVENTORY]

    if not PC_INVENTORY:
        raise ValueError(
            "inventory.yaml has no prism_central entries defined. "
            "Add at least one entry before using PC tools."
        )

    if not pc_name:
        if len(PC_INVENTORY) == 1:
            return PC_INVENTORY[0]["pc_host"]
        raise ValueError(
            f"Multiple Prism Central instances in inventory — specify pc_name. "
            f"Available: {names}"
        )

    for entry in PC_INVENTORY:
        if entry["name"].lower() == pc_name.lower():
            return entry["pc_host"]

    raise ValueError(
        f"Prism Central '{pc_name}' not found in inventory.yaml. "
        f"Available: {names}"
    )


def json_response(data) -> str:
    """Serialise data to a pretty-printed JSON string."""
    return json.dumps(data, indent=2, default=str)
