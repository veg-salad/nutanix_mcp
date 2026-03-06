"""
Nutanix Prism API HTTP clients.

pe_get    — Prism Element v2.0 REST API (per-cluster, GET)
pc_v4_get — Prism Central v4.0 REST API (GET, OData query params)
"""

import os

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_BASE_PATH = "/PrismGateway/services/rest/v2.0"

# Prism Element credentials
_USERNAME = os.environ.get("NUTANIX_USERNAME", "")
_PASSWORD = os.environ.get("NUTANIX_PASSWORD", "")
_VERIFY_SSL = os.environ.get("NUTANIX_VERIFY_SSL", "false").lower() == "true"

# Prism Central credentials — stored separately from PE (credentials differ per org).
# Use NUTANIX_PC_API_KEY (preferred) OR NUTANIX_PC_USERNAME + NUTANIX_PC_PASSWORD.
_PC_USERNAME = os.environ.get("NUTANIX_PC_USERNAME", "")
_PC_PASSWORD = os.environ.get("NUTANIX_PC_PASSWORD", "")
_PC_API_KEY  = os.environ.get("NUTANIX_PC_API_KEY", "")

if not _USERNAME:
    raise EnvironmentError(
        "NUTANIX_USERNAME is not set. "
        "Add it to your mcp.json environment configuration."
    )


def pe_get(path, params=None, host=None):
    """Issue an authenticated GET request to Prism Element and return parsed JSON."""
    if not host:
        raise ValueError("No host provided. Ensure inventory.yaml has at least one cluster entry.")
    url = f"https://{host}:9440{_BASE_PATH}{path}"
    try:
        response = requests.get(
            url,
            auth=(_USERNAME, _PASSWORD),
            params=params,
            verify=_VERIFY_SSL,
            timeout=30,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError as exc:
        raise RuntimeError(
            f"SSL error connecting to {host}. Set NUTANIX_VERIFY_SSL=false to skip verification."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Cannot connect to {host}:9440. Verify the host is reachable."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        body = exc.response.text if exc.response is not None else ""
        raise RuntimeError(f"HTTP {status} from Nutanix API: {body}") from exc


def _pc_auth_check():
    if not _PC_API_KEY and not _PC_USERNAME:
        raise EnvironmentError(
            "No Prism Central credentials found. "
            "Set NUTANIX_PC_API_KEY for API key auth, or "
            "NUTANIX_PC_USERNAME + NUTANIX_PC_PASSWORD for basic auth, "
            "in your mcp.json environment configuration."
        )


def pc_v4_get(path, params=None, host=None):
    """Issue an authenticated GET to a Prism Central v4 endpoint and return parsed JSON.

    path should be the full sub-path including namespace and version, e.g.
    '/api/vmm/v4.0/ahv/config/vms'.  OData query params ($page, $limit, $filter
    etc.) are passed via the params dict.

    Authentication priority: API key (X-Ntnx-Api-Key header) takes precedence
    over basic auth if NUTANIX_PC_API_KEY is set.
    """
    if not host:
        raise ValueError("No host provided. Ensure inventory.yaml has at least one prism_central entry.")
    _pc_auth_check()
    url = f"https://{host}:9440{path}"
    if _PC_API_KEY:
        auth = None
        headers = {"Accept": "application/json", "X-Ntnx-Api-Key": _PC_API_KEY}
    else:
        auth = (_PC_USERNAME, _PC_PASSWORD)
        headers = {"Accept": "application/json"}
    try:
        response = requests.get(
            url,
            auth=auth,
            params=params,
            verify=_VERIFY_SSL,
            timeout=30,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError as exc:
        raise RuntimeError(
            f"SSL error connecting to {host}. Set NUTANIX_VERIFY_SSL=false to skip verification."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(f"Cannot connect to {host}:9440. Verify the host is reachable.") from exc
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        body_text = exc.response.text if exc.response is not None else ""
        raise RuntimeError(f"HTTP {status} from Nutanix PC API: {body_text}") from exc
