"""
Shared utility functions for Valorant API.

Contains common functions used across multiple API modules:
- Cookie-based authentication
- Authentication helpers
- Region/shard detection
- Client version fetching
- Player info retrieval
"""

import json
import requests
from typing import Optional
from urllib.parse import urlparse, parse_qsl

# Reauth URL for cookie-based authentication
REAUTH_URL = (
    "https://auth.riotgames.com/authorize?"
    "redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&"
    "client_id=play-valorant-web-prod&"
    "response_type=token%20id_token&"
    "nonce=1&"
    "scope=account%20openid"
)

# Static client platform (base64 encoded JSON)
CLIENT_PLATFORM = (
    "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
)

# Currency IDs
CURRENCY_IDS = {
    "85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741": "VP",  # Valorant Points
    "e59aa87c-4cbf-517a-5983-6e81511be9b7": "RAD",  # Radianite Points
    "85ca954a-41f2-ce94-9b45-8ca3dd39a00d": "KC",   # Kingdom Credits
}

# Item Type IDs
ITEM_TYPE_IDS = {
    "01bb38e1-da47-4e6a-9b3d-945fe4655707": "Agent",
    "f85cb6f7-33e5-4dc8-b609-ec7212301948": "Contract",
    "d5f120f8-ff8c-4571-a619-6040a99c96ed": "Spray",
    "dd3bf334-87f3-40bd-b043-682a57a8dc3a": "Gun Buddy",
    "3f296c07-64c3-494c-923b-fe692a4fa1bd": "Player Card",
    "e7c63390-eda7-46e0-bb7a-a6abdacd2433": "Skin",
    "3ad1b2b2-acdb-4524-852f-954a76ddae0a": "Skin Level",
    "de7caa6b-adf7-4588-bbd1-143831e786c6": "Skin Chroma",
    "bcef87d6-209b-46c6-8b19-fbe40bd95abc": "Title",
}


def get_entitlement_token(access_token: str) -> Optional[str]:
    """Get entitlement token from Riot servers."""
    url = "https://entitlements.auth.riotgames.com/api/token/v1"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json={})
    if res.status_code != 200:
        return None
    return res.json().get("entitlements_token")


def get_client_version() -> str:
    """Get current Valorant client version from valorant-api.com."""
    url = "https://valorant-api.com/v1/version"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("riotClientVersion")
    except Exception:
        pass
    return "release-10.00-shipping-9-2555555"


def get_player_region(access_token: str, id_token: str) -> Optional[str]:
    """Get player's region from Riot Geo endpoint."""
    url = "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.put(url, headers=headers, json={"id_token": id_token})
    if res.status_code != 200:
        return None
    return res.json().get("affinities", {}).get("live")


def region_to_shard(region: str) -> str:
    """Convert region to shard."""
    shard_map = {
        "latam": "na",
        "br": "na",
        "na": "na",
        "pbe": "pbe",
        "eu": "eu",
        "ap": "ap",
        "kr": "kr",
    }
    return shard_map.get(region, "na")


def get_player_info(access_token: str) -> Optional[dict]:
    """Get player info (PUUID, game name, tag)."""
    url = "https://auth.riotgames.com/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None
    return res.json()


def format_currency(amount: int, currency_id: str) -> str:
    """Format currency amount with symbol."""
    currency_name = CURRENCY_IDS.get(currency_id, "?")
    return f"{amount} {currency_name}"


# =============================================================================
# Cookie-based Authentication
# =============================================================================

def load_cookies(session: requests.Session, cookies_file: str = "cookies.json") -> None:
    """Load cookies from file into session."""
    with open(cookies_file, "r") as f:
        cookies = json.load(f)
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain="auth.riotgames.com")


def cookie_reauth(cookies_file: str = "cookies.json") -> Optional[dict]:
    """
    Perform cookie-based re-authentication to get fresh tokens.
    
    Args:
        cookies_file: Path to the cookies.json file
    
    Returns:
        Dict with access_token, id_token, expires_in, token_type
        or None if cookies are expired
    """
    session = requests.Session()
    load_cookies(session, cookies_file)

    res = session.get(REAUTH_URL, allow_redirects=False)
    location = res.headers.get("Location", "")

    # Failure → redirect to login page
    if "authenticate.riotgames.com" in location:
        print("❌ Cookies expired. Need new cookies.")
        return None

    # Success → extract tokens from redirect fragment
    fragment = urlparse(location).fragment
    params = dict(parse_qsl(fragment))

    tokens = {
        "access_token": str(params.get("access_token", "")),
        "id_token": str(params.get("id_token", "")),
        "expires_in": str(params.get("expires_in", "")),
        "token_type": str(params.get("token_type", ""))
    }

    print("\n🎉 Fresh tokens obtained")
    return tokens
