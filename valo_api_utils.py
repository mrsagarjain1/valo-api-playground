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

    # Failure - redirect to login page
    if "authenticate.riotgames.com" in location:
        print("Cookies expired. Need new cookies.")
        return None

    # Success - extract tokens from redirect fragment
    fragment = urlparse(location).fragment
    params = dict(parse_qsl(fragment))

    tokens = {
        "access_token": str(params.get("access_token", "")),
        "id_token": str(params.get("id_token", "")),
        "expires_in": str(params.get("expires_in", "")),
        "token_type": str(params.get("token_type", ""))
    }

    print("\nFresh tokens obtained")
    return tokens


# =============================================================================
# Competitive Tier Mapping
# =============================================================================

# Competitive tier mapping from Riot tier numbers to readable names
TIER_MAP = {
    0: "Unrated",
    1: "Unused",
    2: "Unused",
    3: "Iron 1",
    4: "Iron 2",
    5: "Iron 3",
    6: "Bronze 1",
    7: "Bronze 2",
    8: "Bronze 3",
    9: "Silver 1",
    10: "Silver 2",
    11: "Silver 3",
    12: "Gold 1",
    13: "Gold 2",
    14: "Gold 3",
    15: "Platinum 1",
    16: "Platinum 2",
    17: "Platinum 3",
    18: "Diamond 1",
    19: "Diamond 2",
    20: "Diamond 3",
    21: "Ascendant 1",
    22: "Ascendant 2",
    23: "Ascendant 3",
    24: "Immortal 1",
    25: "Immortal 2",
    26: "Immortal 3",
    27: "Radiant",
}

# Season UUID to Episode/Act mapping (Henrik API format)
# Source: https://valorant-api.com/v1/seasons
SEASON_MAP = {
    # Episode 1
    "3f61c772-4560-cd3f-5d3f-a7ab5abda6b3": "e1a1",
    "0530b9c4-4980-f2ee-df5d-09864cd00542": "e1a2",
    "46ea6166-4573-1128-9cea-60a15640059b": "e1a3",
    # Episode 2
    "97b6e739-44cc-ffa7-49ad-398ba502ceb0": "e2a1",
    "ab57ef51-4e59-da91-cc8d-51a5a2b9b8ff": "e2a2",
    "52e9749a-429b-7060-99fe-4595426a0cf7": "e2a3",
    # Episode 3
    "2a27e5d2-4d30-c9e2-b15a-93b8909a442c": "e3a1",
    "4cb622e1-4244-6da3-7276-8daaf1c01be2": "e3a2",
    "a16955a5-4ad0-f761-5e9e-389df1c892fb": "e3a3",
    # Episode 4
    "573f53ac-41a5-3a7d-d9ce-d6a6298e5704": "e4a1",
    "d929bc38-4ab6-7da4-94f0-ee84f8ac141e": "e4a2",
    "3e47230a-463c-a301-eb7d-67bb60357d4f": "e4a3",
    # Episode 5
    "67e373c7-48f7-b422-641b-079ace30b427": "e5a1",
    "7a85de9a-4032-61a9-61d8-f4aa2b4a84b6": "e5a2",
    "aca29595-40e4-01f5-3f35-b1b3d304c96e": "e5a3",
    # Episode 6
    "9c91a445-4f78-1baa-a3ea-8f8aadf4914d": "e6a1",
    "34093c29-4306-43de-452f-3f944bde22be": "e6a2",
    "2de5423b-4aad-02ad-8d9b-c0a931958861": "e6a3",
    # Episode 7
    "0981a882-4e7d-371a-70c4-c3b4f46c504a": "e7a1",
    "03dfd004-45d4-ebfd-ab0a-948ce780dac4": "e7a2",
    "4401f9fd-4170-2e4c-4bc3-f3b4d7d150d1": "e7a3",
    # Episode 8
    "ec876e6c-43e8-fa63-ffc1-2e8d4db25525": "e8a1",
    "22d10d66-4d2a-a340-6c54-408c7bd53807": "e8a2",
    "4539cac3-47ae-90e5-3d01-b3812ca3274e": "e8a3",
    # Episode 9
    "52ca6698-41c1-e7de-4008-8994d2221209": "e9a1",
    "292f58db-4c17-89a7-b1c0-ba988f0e9d98": "e9a2",
    "dcde7346-4085-de4f-c463-2489ed47983b": "e9a3",
    # V25 (Episode 10) - First half
    "476b0893-4c2e-abd6-c5fe-708facff0772": "v25a1",
    "16118998-4705-5813-86dd-0292a2439d90": "v25a2",
    "aef237a0-494d-3a14-a1c8-ec8de84e309c": "v25a3",
    # V25 (Episode 10) - Second half
    "ac12e9b3-47e6-9599-8fa1-0bb473e5efc7": "v25a4",
    "5adc33fa-4f30-2899-f131-6fba64c5dd3a": "v25a5",
    "4c4b8cff-43eb-13d3-8f14-96b783c90cd2": "v25a6",
    # V26 - First half
    "3ea2b318-423b-cf86-25da-7cbb0eefbe2d": "v26a1",
    "9d85c932-4820-c060-09c3-668636d4df1b": "v26a2",
    "ce2783e8-44fc-dd48-3da3-33b5ba6c4a22": "v26a3",
    # V26 - Second half
    "4f0864e2-40af-28a4-de2c-0e9e64e75f23": "v26a4",
    "8102cd81-43a0-d0d7-bd59-47b8fe9bed1b": "v26a5",
    "d816f426-48ea-f052-117f-9697a155b319": "v26a6",
}


def get_tier_name(tier_id: int, season_short_str: str = "") -> str:
    """
    Get readable rank name from tier ID.
    
    Args:
        tier_id: Riot's numeric tier ID
        season_short_str: Season short string (e.g., "e8a3") for historical mapping
    
    Returns:
        Readable rank name (e.g., "Diamond 2")
    """
    # Default to current map
    name = TIER_MAP.get(tier_id, "Unknown")
    
    # Check for old episodes (Pre-Episode 5)
    if season_short_str and season_short_str.startswith("e"):
        try:
            parts = season_short_str[1:].split("a")
            if len(parts) >= 1:
                ep = int(parts[0])
                if ep < 5:
                    # Old mapping
                    if tier_id == 21: return "Immortal 1"
                    if tier_id == 22: return "Immortal 2"
                    if tier_id == 23: return "Immortal 3"
                    if tier_id == 24: return "Radiant"
        except (ValueError, IndexError):
            pass
    return name


def season_short(season_id: str) -> str:
    """Convert season UUID to episode/act notation (e.g. e8a3)"""
    return SEASON_MAP.get(season_id, season_id[:4].lower() if season_id else "unknown")


# =============================================================================
# Player Lookup and MMR Functions
# =============================================================================

def get_puuid_by_name(game_name: str, tag_line: str, access_token: str) -> Optional[str]:
    """
    Look up a player's PUUID by their game name and tag.
    
    Args:
        game_name: Player's Riot game name
        tag_line: Player's tag (without #)
        access_token: Valid Riot access token
    
    Returns:
        Player's PUUID or None if not found
    """
    url = "https://api.account.riotgames.com/aliases/v1/aliases"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    params = {"gameName": game_name, "tagLine": tag_line}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        return None
    data = res.json()
    if not data:
        return None
    return data[0].get("puuid")


def get_player_mmr(puuid: str, access_token: str, entitlement_token: str, shard: str) -> Optional[dict]:
    """
    Fetch player's MMR data from Riot's API.
    
    Args:
        puuid: Player's PUUID
        access_token: Valid Riot access token
        entitlement_token: Valid entitlement token
        shard: Server shard (na/eu/ap/kr)
    
    Returns:
        MMR data dict or None if failed
    """
    client_version = get_client_version()
    url = f"https://pd.{shard}.a.pvp.net/mmr/v1/players/{puuid}"
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None
    return res.json()


def get_competitive_updates(puuid: str, access_token: str, entitlement_token: str, shard: str, limit: int = 2000) -> list:
    """
    Pull competitive updates (match-by-match MMR changes) with pagination.
    
    Args:
        puuid: Player's PUUID
        access_token: Valid Riot access token
        entitlement_token: Valid entitlement token
        shard: Server shard (na/eu/ap/kr)
        limit: Maximum number of matches to fetch
    
    Returns:
        List of competitive match updates
    """
    all_matches = []
    start = 0
    page = 200
    client_version = get_client_version()
    while start < limit:
        url = f"https://pd.{shard}.a.pvp.net/mmr/v1/players/{puuid}/competitiveupdates"
        params = {"startIndex": start, "endIndex": start + page}
        headers = {
            "X-Riot-ClientPlatform": CLIENT_PLATFORM,
            "X-Riot-ClientVersion": client_version,
            "X-Riot-Entitlements-JWT": entitlement_token,
            "Authorization": f"Bearer {access_token}",
        }
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            break
        matches = res.json().get("Matches", [])
        all_matches.extend(matches)
        if len(matches) < page:
            break
        start += page
    return all_matches
