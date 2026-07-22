"""OAuth2 (Cognito client-credentials) token helper for an AgentCore Gateway MCP endpoint.

Framework-agnostic. When you create an AgentCore Gateway it provisions an OAuth2 client
(Amazon Cognito). The agent exchanges client_id/secret for a short-lived bearer token and
sends it to the Gateway's MCP URL. Token is cached until shortly before expiry.

Set these from the gateway creation output (see README):
  GATEWAY_MCP_URL, GATEWAY_CLIENT_ID, GATEWAY_CLIENT_SECRET, GATEWAY_TOKEN_ENDPOINT, GATEWAY_SCOPE
"""

import os
from datetime import datetime, timedelta

import httpx

GATEWAY_MCP_URL = os.environ.get("GATEWAY_MCP_URL")
CLIENT_ID = os.environ.get("GATEWAY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GATEWAY_CLIENT_SECRET")
TOKEN_ENDPOINT = os.environ.get("GATEWAY_TOKEN_ENDPOINT")
SCOPE = os.environ.get("GATEWAY_SCOPE")

_cache = {"token": None, "expires_at": None}


def get_oauth_token():
    """Return a cached or freshly-minted OAuth2 bearer token for the Gateway."""
    if _cache["token"] and _cache["expires_at"] and datetime.now() < _cache["expires_at"]:
        return _cache["token"]
    resp = httpx.post(
        TOKEN_ENDPOINT,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": SCOPE,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    _cache["token"] = data["access_token"]
    _cache["expires_at"] = datetime.now() + timedelta(
        seconds=data.get("expires_in", 3600) - 300
    )
    return _cache["token"]
