"""
Nutanix MCP Setup
-----------------
Run once after cloning / extracting the folder:

    python setup.py

What it does:
  1. Checks Python version (3.10+ required)
  2. Installs Python dependencies
  3. Creates .vscode/mcp.json with your PE and PC credentials (prompts interactively)
  4. Populates inventory.yaml with your Prism Central instance(s) and PE clusters

Re-run at any time to add new clusters / PC instances or to add missing credentials.
"""

import json
import os
import subprocess
import sys

MIN_PYTHON = (3, 10)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def info(msg):
    print(f"  {msg}")

def ok(msg):
    print(f"  [OK] {msg}")

def warn(msg):
    print(f"  [!]  {msg}")

def fail(msg):
    print(f"\n  [ERROR] {msg}")
    sys.exit(1)

def prompt(label, secret=False):
    import getpass
    value = ""
    while not value:
        value = getpass.getpass(f"  {label}: ") if secret else input(f"  {label}: ").strip()
        if not value:
            warn("Value cannot be empty, please try again.")
    return value


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def check_python():
    if sys.version_info < MIN_PYTHON:
        fail(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required. "
            f"You are running {sys.version.split()[0]}. "
            f"Download it from https://www.python.org/downloads/"
        )
    ok(f"Python {sys.version.split()[0]}")


def install_dependencies():
    req_path = os.path.join(BASE_DIR, "src", "requirements.txt")
    info("Installing Python dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", req_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"pip install failed:\n{result.stderr}")
    ok("Dependencies installed")


# Placeholder strings written to mcp.json for credentials not yet supplied.
_CREDENTIAL_PLACEHOLDERS = {
    "NUTANIX_PE_USERNAME":  "YOUR_PE_USERNAME",
    "NUTANIX_PE_PASSWORD":  "YOUR_PE_PASSWORD",
    "NUTANIX_VERIFY_SSL":   "false",
    "NUTANIX_PC_USERNAME": "YOUR_PC_USERNAME",
    "NUTANIX_PC_PASSWORD": "YOUR_PC_PASSWORD",
    "NUTANIX_PC_API_KEY":  "YOUR_PC_API_KEY",
}


def _is_placeholder(key, val):
    """Return True when a value is blank or still the default placeholder."""
    return not val or val == _CREDENTIAL_PLACEHOLDERS.get(key, "")


def create_mcp_json():
    import getpass

    vscode_dir = os.path.join(BASE_DIR, ".vscode")
    mcp_path = os.path.join(vscode_dir, "mcp.json")

    # Load existing config so we can preserve real values already set
    existing_env = {}
    if os.path.exists(mcp_path):
        try:
            with open(mcp_path) as f:
                existing_config = json.load(f)
            existing_env = (
                existing_config
                .get("servers", {})
                .get("nutanix-prism", {})
                .get("env", {})
            )
        except Exception:
            pass

    # Start from existing values; seed any missing keys with placeholders
    env = dict(existing_env)
    for key, placeholder in _CREDENTIAL_PLACEHOLDERS.items():
        if key not in env:
            env[key] = placeholder

    need_pe = _is_placeholder("NUTANIX_PE_USERNAME", env.get("NUTANIX_PE_USERNAME", ""))
    need_pc = (
        _is_placeholder("NUTANIX_PC_API_KEY",  env.get("NUTANIX_PC_API_KEY",  ""))
        and _is_placeholder("NUTANIX_PC_USERNAME", env.get("NUTANIX_PC_USERNAME", ""))
    )

    if not need_pe and not need_pc:
        ok(".vscode/mcp.json already has PE and PC credentials — skipping")
        return

    if need_pe:
        print("\n  Enter your Nutanix Prism Element (PE) credentials.")
        print("  Press Enter to skip — placeholders will remain in .vscode/mcp.json.\n")
        username = input("  PE username (e.g. admin): ").strip()
        if username:
            env["NUTANIX_PE_USERNAME"] = username
            env["NUTANIX_PE_PASSWORD"] = getpass.getpass("  PE password: ")
            ssl_input = input("  Verify SSL certificate? (yes/no) [no]: ").strip().lower()
            env["NUTANIX_VERIFY_SSL"] = "true" if ssl_input == "yes" else "false"
        else:
            warn("PE credentials skipped — update NUTANIX_PE_USERNAME / NUTANIX_PE_PASSWORD in .vscode/mcp.json before use.")

    if need_pc:
        print("\n  Enter your Nutanix Prism Central (PC) credentials.")
        print("  (Usually different from PE — each org has separate PC/PE accounts.)")
        print("  Option 1: API key auth (recommended).  Option 2: Basic auth (username + password).")
        print("  Press Enter at any prompt to skip — placeholders will remain in .vscode/mcp.json.\n")
        api_key_input = input("  PC API key (leave blank to use username/password instead): ").strip()
        if api_key_input:
            env["NUTANIX_PC_API_KEY"] = api_key_input
        else:
            pc_username = input("  PC username (e.g. admin, blank to skip): ").strip()
            if pc_username:
                env["NUTANIX_PC_USERNAME"] = pc_username
                env["NUTANIX_PC_PASSWORD"] = getpass.getpass("  PC password: ")
            else:
                warn("PC credentials skipped — update NUTANIX_PC_API_KEY or NUTANIX_PC_USERNAME / NUTANIX_PC_PASSWORD in .vscode/mcp.json before use.")

    config = {
        "servers": {
            "nutanix-prism": {
                "type": "stdio",
                "command": "python",
                "args": ["${workspaceFolder}/src/server.py"],
                "env": env,
            }
        }
    }

    os.makedirs(vscode_dir, exist_ok=True)
    with open(mcp_path, "w") as f:
        json.dump(config, f, indent=2)

    ok(".vscode/mcp.json created/updated")


def configure_inventory():
    import yaml

    inventory_path = os.path.join(BASE_DIR, "inventory.yaml")

    def _is_sample(c):
        return c.get("name", "").upper().startswith("SAMPLE-")

    # Load existing clusters if the file is already present and valid
    existing_clusters = []
    if os.path.exists(inventory_path):
        try:
            with open(inventory_path) as f:
                data = yaml.safe_load(f)
            existing_clusters = data.get("clusters", []) if data else []
        except Exception:
            pass

    # Strip placeholder sample entries — they are never real clusters
    real_clusters = [c for c in existing_clusters if not _is_sample(c)]

    if real_clusters:
        print(f"\n  inventory.yaml already has {len(real_clusters)} cluster(s):")
        for c in real_clusters:
            print(f"    - {c['name']}  ({c['pe_host']})")
        print("  Enter additional clusters below, or press Enter to skip.")
        clusters = list(real_clusters)
    else:
        print("\n  Let's register your Prism Element cluster(s) in inventory.yaml.")
        print("  Enter a cluster name then its IP. Leave either blank to finish.\n")
        clusters = []

    while True:
        name = input(f"  Cluster name (blank to finish): ").strip()
        if not name:
            break
        if any(c["name"].lower() == name.lower() for c in clusters):
            warn(f"A cluster named '{name}' already exists — skipping.")
            continue
        pe_host = input(f"  PE IP / FQDN for {name} (blank to cancel): ").strip()
        if not pe_host:
            break
        clusters.append({"name": name, "pe_host": pe_host})
        ok(f"Added {name} ({pe_host})")

    if not clusters:
        warn("No clusters added — inventory.yaml not written. Add entries manually before use.")
        return

    # Re-read to preserve prism_central entries that may already be in the file
    try:
        with open(inventory_path) as f:
            existing_full = yaml.safe_load(f) or {}
    except Exception:
        existing_full = {}

    inventory_out = {}
    if existing_full.get("prism_central"):
        inventory_out["prism_central"] = existing_full["prism_central"]
    inventory_out["clusters"] = clusters

    with open(inventory_path, "w") as f:
        yaml.dump(inventory_out, f, default_flow_style=False, sort_keys=False)

    ok(f"inventory.yaml written — {len(clusters)} cluster(s) registered")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def configure_pc_inventory():
    import yaml

    inventory_path = os.path.join(BASE_DIR, "inventory.yaml")

    def _is_sample(c):
        return c.get("name", "").upper().startswith("SAMPLE-")

    # Load existing inventory (preserve clusters and existing real PC instances)
    existing_data = {}
    if os.path.exists(inventory_path):
        try:
            with open(inventory_path) as f:
                existing_data = yaml.safe_load(f) or {}
        except Exception:
            pass

    real_pc = [c for c in existing_data.get("prism_central", []) if not _is_sample(c)]

    if real_pc:
        print(f"\n  inventory.yaml already has {len(real_pc)} Prism Central instance(s):")
        for c in real_pc:
            print(f"    - {c['name']}  ({c['pc_host']})")
        print("  Enter additional PC instances below, or press Enter to skip.")
        pc_instances = list(real_pc)
    else:
        print("\n  Let's register your Prism Central instance(s) in inventory.yaml.")
        print("  Enter a name then its IP/FQDN. Leave either blank to finish.\n")
        pc_instances = []

    while True:
        name = input("  Prism Central name (blank to finish): ").strip()
        if not name:
            break
        if any(c["name"].lower() == name.lower() for c in pc_instances):
            warn(f"A Prism Central named '{name}' already exists — skipping.")
            continue
        pc_host = input(f"  PC IP / FQDN for {name} (blank to cancel): ").strip()
        if not pc_host:
            break
        pc_instances.append({"name": name, "pc_host": pc_host})
        ok(f"Added {name} ({pc_host})")

    if not pc_instances:
        warn("No Prism Central instances added. Add entries manually to inventory.yaml before using PC tools.")
        return

    # prism_central listed first, then clusters
    inventory_out = {"prism_central": pc_instances}
    if existing_data.get("clusters"):
        inventory_out["clusters"] = existing_data["clusters"]

    with open(inventory_path, "w") as f:
        yaml.dump(inventory_out, f, default_flow_style=False, sort_keys=False)

    ok(f"inventory.yaml updated — {len(pc_instances)} Prism Central instance(s) registered")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\nNutanix MCP Setup\n" + "-" * 40)

    check_python()
    install_dependencies()
    create_mcp_json()
    configure_inventory()
    configure_pc_inventory()

    print("\n" + "-" * 40)
    print("  Setup complete! Next steps:\n")
    print("  1. Open this folder in VS Code")
    print("  2. Install the GitHub Copilot & Copilot Chat extensions if prompted")
    print("  3. Open Copilot Chat → Agent mode → ask about your cluster\n")


if __name__ == "__main__":
    main()
