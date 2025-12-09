"""
Get the player's current loadout (equipped skins, sprays, player card, title).

Endpoint used:
- GET Player Loadout: https://pd.{shard}.a.pvp.net/personalization/v2/players/{puuid}/playerloadout

Note: This endpoint only works for your own PUUID (authenticated account).
You cannot view other players' loadouts through this endpoint.
"""

import json
import requests
from typing import Optional, Dict, List, Any, Tuple

from valo_api_utils import (
    CLIENT_PLATFORM,
    get_entitlement_token,
    get_client_version,
    get_player_region,
    region_to_shard,
    get_player_info,
    cookie_reauth,
)


# Weapon UUIDs mapping
WEAPON_IDS = {
    "63e6c2b6-4a8e-869c-3d4c-e38355226584": "Odin",
    "55d8a0f4-4274-ca67-fe2c-06ab45efdf58": "Ares",
    "9c82e19d-4575-0200-1a81-3eacf00cf872": "Vandal",
    "ae3de142-4d85-2547-dd26-4e90bed35cf7": "Bulldog",
    "ee8e8d15-496b-07ac-e5f6-8fae5d4c7b1a": "Phantom",
    "ec845bf4-4f79-ddda-a3da-0db3774b2794": "Judge",
    "910be174-449b-c412-ab22-d0873436b21b": "Bucky",
    "44d4e95c-4157-0037-81b2-17841bf2e8e3": "Frenzy",
    "29a0cfab-485b-f5d5-779a-b59f85e204a8": "Classic",
    "1baa85b4-4c70-1284-64bb-6481dfc3bb4e": "Ghost",
    "e336c6b8-418d-9340-d77f-7a9e4cfe0702": "Sheriff",
    "42da8ccc-40d5-affc-beec-15aa47b42eda": "Shorty",
    "a03b24d3-4319-996d-0f8c-94bbfba1dfc7": "Operator",
    "4ade7faa-4cf1-8376-95ef-39884480959b": "Guardian",
    "5f0aaf7a-4289-3998-d5ff-eb9a5cf7f5ce": "Outlaw",
    "c4883e50-4494-202c-3ec3-6b8a9284f00b": "Marshal",
    "462080d1-4035-2937-7c09-27aa2a5c27a7": "Spectre",
    "f7e1b454-4ad4-1063-ec0a-159e56b58941": "Stinger",
    "2f59173c-4bed-b6c3-2191-dea9b58be9c7": "Melee",
    "5f0aaf7a-4289-3998-d5ff-eb9a5cf7ef5c": "Outlaw",
}

# Spray slot IDs
SPRAY_SLOTS = {
    "0814b2fe-4512-60a4-5288-1fbdcec6ca48": "Pre-Round",
    "04af080a-4071-487b-61c0-5b9c0cfaac74": "Mid-Round",
    "5863985e-43ac-b05d-cb2d-139e72970571": "Post-Round",
    "5863985e-43ac-b05d-cb2d-139e72970014": "Slot 4",
    "7cdc908e-4f69-9140-a604-899bd879eed1": "Slot 5",
}


def get_player_loadout(puuid: str, access_token: str, entitlement_token: str, shard: str) -> Optional[dict]:
    """
    Get the player's current loadout.
    
    Returns the raw loadout response including:
    - Guns: All equipped weapon skins, chromas, and buddies
    - Sprays: Equipped sprays for each slot
    - Identity: Player card, title, account level, level border
    - Incognito: Whether the player is hiding their identity
    
    Note: This only works for the authenticated account's loadout.
    You cannot view other players' loadouts through this endpoint.
    """
    client_version = get_client_version()
    url = f"https://pd.{shard}.a.pvp.net/personalization/v2/players/{puuid}/playerloadout"
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Loadout request failed: {res.status_code}")
        print(f"Response: {res.text[:500] if res.text else 'Empty'}")
        return None
    return res.json()


def get_skin_name(skin_uuid: str) -> str:
    """Get skin name from valorant-api.com."""
    if not skin_uuid:
        return "Default"
    try:
        # Try weapon skin level first
        url = f"https://valorant-api.com/v1/weapons/skinlevels/{skin_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", skin_uuid)
        
        # Try weapon skin
        url = f"https://valorant-api.com/v1/weapons/skins/{skin_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", skin_uuid)
    except Exception:
        pass
    return skin_uuid


def get_chroma_name(chroma_uuid: str) -> str:
    """Get chroma name from valorant-api.com."""
    if not chroma_uuid:
        return "Default"
    try:
        url = f"https://valorant-api.com/v1/weapons/skinchromas/{chroma_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", chroma_uuid)
    except Exception:
        pass
    return chroma_uuid


def get_buddy_name(buddy_uuid: str) -> Optional[str]:
    """Get buddy name from valorant-api.com."""
    if not buddy_uuid:
        return None
    try:
        url = f"https://valorant-api.com/v1/buddies/levels/{buddy_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", buddy_uuid)
        
        url = f"https://valorant-api.com/v1/buddies/{buddy_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", buddy_uuid)
    except Exception:
        pass
    return buddy_uuid


def get_spray_name(spray_uuid: str) -> str:
    """Get spray name from valorant-api.com."""
    if not spray_uuid:
        return "None"
    try:
        url = f"https://valorant-api.com/v1/sprays/{spray_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", spray_uuid)
    except Exception:
        pass
    return spray_uuid


def get_player_card_name(card_uuid: str) -> str:
    """Get player card name from valorant-api.com."""
    if not card_uuid:
        return "Default"
    try:
        url = f"https://valorant-api.com/v1/playercards/{card_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", card_uuid)
    except Exception:
        pass
    return card_uuid


def get_player_title_text(title_uuid: str) -> str:
    """Get player title text from valorant-api.com."""
    if not title_uuid:
        return "None"
    try:
        url = f"https://valorant-api.com/v1/playertitles/{title_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()["data"]
            return data.get("titleText") or data.get("displayName", title_uuid)
    except Exception:
        pass
    return title_uuid


def get_level_border_name(border_uuid: str) -> str:
    """Get level border name from valorant-api.com."""
    if not border_uuid:
        return "Default"
    try:
        url = f"https://valorant-api.com/v1/levelborders/{border_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", border_uuid)
    except Exception:
        pass
    return border_uuid


def parse_loadout(loadout: dict) -> dict:
    """
    Parse loadout response into a more readable format.
    
    Args:
        loadout: Raw loadout response
    
    Returns:
        Parsed loadout data with item names
    """
    result = {
        "weapons": [],
        "sprays": [],
        "identity": {},
    }
    
    # Parse weapons/guns
    guns = loadout.get("Guns", [])
    for gun in guns:
        weapon_id = gun.get("ID", "")
        weapon_name = WEAPON_IDS.get(weapon_id, weapon_id)
        
        skin_id = gun.get("SkinLevelID") or gun.get("SkinID", "")
        skin_name = get_skin_name(skin_id)
        
        chroma_id = gun.get("ChromaID", "")
        chroma_name = get_chroma_name(chroma_id) if chroma_id else None
        
        buddy_id = gun.get("CharmLevelID") or gun.get("CharmID", "")
        buddy_name = get_buddy_name(buddy_id) if buddy_id else None
        
        weapon_data = {
            "weapon": weapon_name,
            "weapon_uuid": weapon_id,
            "skin": skin_name,
            "skin_uuid": skin_id,
        }
        
        if chroma_name and chroma_name != skin_name:
            weapon_data["chroma"] = chroma_name
            weapon_data["chroma_uuid"] = chroma_id
        
        if buddy_name:
            weapon_data["buddy"] = buddy_name
            weapon_data["buddy_uuid"] = buddy_id
        
        result["weapons"].append(weapon_data)
    
    # Parse sprays
    sprays = loadout.get("Sprays", [])
    for spray in sprays:
        slot_id = spray.get("EquipSlotID", "")
        slot_name = SPRAY_SLOTS.get(slot_id, slot_id)
        
        spray_id = spray.get("SprayID", "")
        spray_name = get_spray_name(spray_id)
        
        result["sprays"].append({
            "slot": slot_name,
            "slot_uuid": slot_id,
            "spray": spray_name,
            "spray_uuid": spray_id,
        })
    
    # Parse identity
    identity = loadout.get("Identity", {})
    
    card_id = identity.get("PlayerCardID", "")
    card_name = get_player_card_name(card_id)
    
    title_id = identity.get("PlayerTitleID", "")
    title_text = get_player_title_text(title_id)
    
    border_id = identity.get("PreferredLevelBorderID", "")
    border_name = get_level_border_name(border_id) if border_id else "Default"
    
    result["identity"] = {
        "player_card": card_name,
        "player_card_uuid": card_id,
        "player_title": title_text,
        "player_title_uuid": title_id,
        "account_level": identity.get("AccountLevel", 0),
        "level_border": border_name,
        "level_border_uuid": border_id,
        "hide_account_level": identity.get("HideAccountLevel", False),
    }
    
    result["incognito"] = loadout.get("Incognito", False)
    
    return result


def get_player_loadout_data(
    player_name: Optional[str] = None,
    player_tag: Optional[str] = None,
    player_region: Optional[str] = None,
    platform: str = "pc"
) -> Dict[str, Any]:
    """
    Get the authenticated player's loadout.
    
    Note: The loadout endpoint only works for your own PUUID.
    If player_name and player_tag are provided, they are used to verify
    that the authenticated account matches the requested player.
    
    Args:
        player_name: Player's game name (optional, for verification)
        player_tag: Player's tag line (optional, for verification)
        player_region: Player's region (optional, e.g., 'ap', 'na', 'eu', 'kr')
        platform: Platform (default: 'pc')
    
    Returns:
        Dict with:
        - success: bool
        - data: Parsed loadout data (if success)
        - error: Error message (if failed)
        - error_code: Error code (if failed)
            - "AUTH_FAILED": Cookie authentication failed
            - "ENTITLEMENT_FAILED": Failed to get entitlement token
            - "PLAYER_INFO_FAILED": Failed to get player info
            - "REGION_FAILED": Failed to get region
            - "PLAYER_NOT_FOUND": Authenticated player doesn't match requested player
            - "LOADOUT_FAILED": Failed to get loadout
    """
    # Authenticate
    tokens = cookie_reauth()
    if not tokens:
        return {
            "success": False,
            "data": None,
            "error": "Cookie authentication failed. Please update cookies.json",
            "error_code": "AUTH_FAILED"
        }
    
    access_token = tokens["access_token"]
    id_token = tokens.get("id_token", "")
    
    # Get entitlement token
    entitlement_token = get_entitlement_token(access_token)
    if not entitlement_token:
        return {
            "success": False,
            "data": None,
            "error": "Failed to get entitlement token",
            "error_code": "ENTITLEMENT_FAILED"
        }
    
    # Get player info
    player_info = get_player_info(access_token)
    if not player_info:
        return {
            "success": False,
            "data": None,
            "error": "Failed to get player info",
            "error_code": "PLAYER_INFO_FAILED"
        }
    
    puuid = player_info["sub"]
    acct = player_info.get("acct", {})
    game_name = acct.get("game_name", "Unknown")
    tag_line = acct.get("tag_line", "")
    
    # Verify player matches if name/tag provided
    if player_name and player_tag:
        if game_name.lower() != player_name.lower() or tag_line.lower() != player_tag.lower():
            return {
                "success": False,
                "data": None,
                "error": f"Player not found: {player_name}#{player_tag}. "
                         f"The loadout endpoint only works for the authenticated account ({game_name}#{tag_line}). "
                         f"You cannot view other players' loadouts.",
                "error_code": "PLAYER_NOT_FOUND"
            }
    
    # Get region and shard
    if player_region:
        region = player_region.lower()
    else:
        region = get_player_region(access_token, id_token)
        if not region:
            return {
                "success": False,
                "data": None,
                "error": "Failed to get player region",
                "error_code": "REGION_FAILED"
            }
    
    shard = region_to_shard(region)
    
    print(f"\nPlayer: {game_name}#{tag_line}")
    print(f"Region: {region.upper()}, Shard: {shard.upper()}")
    print(f"Platform: {platform.upper()}")
    
    # Get loadout
    print("\nFetching loadout...")
    loadout = get_player_loadout(puuid, access_token, entitlement_token, shard)
    if not loadout:
        return {
            "success": False,
            "data": None,
            "error": "Failed to get loadout from API",
            "error_code": "LOADOUT_FAILED"
        }
    
    # Parse loadout
    parsed = parse_loadout(loadout)
    
    return {
        "success": True,
        "data": {
            "player": {
                "name": game_name,
                "tag": tag_line,
                "puuid": puuid,
                "region": region,
                "platform": platform,
            },
            "loadout": parsed,
            "raw": loadout,
        },
        "error": None,
        "error_code": None
    }


def display_loadout(result: Dict[str, Any]) -> None:
    """Display the loadout in a readable format."""
    if not result["success"]:
        print(f"\nError: {result['error']}")
        print(f"Error Code: {result['error_code']}")
        return
    
    data = result["data"]
    loadout = data["loadout"]
    player = data["player"]
    
    print("\n" + "=" * 60)
    print(f"LOADOUT - {player['name']}#{player['tag']}")
    print("=" * 60)
    
    # Identity
    identity = loadout["identity"]
    print("\n[IDENTITY]")
    print(f"  Player Card: {identity['player_card']}")
    print(f"  Player Title: {identity['player_title']}")
    print(f"  Account Level: {identity['account_level']}")
    print(f"  Level Border: {identity['level_border']}")
    if identity["hide_account_level"]:
        print("  (Account level hidden)")
    if loadout.get("incognito"):
        print("  (Incognito mode enabled)")
    
    # Sprays
    print("\n[SPRAYS]")
    for spray in loadout["sprays"]:
        print(f"  {spray['slot']}: {spray['spray']}")
    
    # Weapons
    print("\n[WEAPONS]")
    for weapon in loadout["weapons"]:
        line = f"  {weapon['weapon']}: {weapon['skin']}"
        if weapon.get("chroma"):
            line += f" ({weapon['chroma']})"
        if weapon.get("buddy"):
            line += f" + {weapon['buddy']}"
        print(line)
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    player_name = None
    player_tag = None
    player_region = None
    platform = "pc"
    
    # Check for command line args
    if len(sys.argv) >= 3:
        player_name = sys.argv[1]
        player_tag = sys.argv[2]
    if len(sys.argv) >= 4:
        player_region = sys.argv[3]
    if len(sys.argv) >= 5:
        platform = sys.argv[4]
    
    # Interactive input if no args provided
    if not player_name:
        print("Get Player Loadout")
        print("-" * 40)
        print("Note: This only works for your own account (authenticated via cookies).")
        print("Leave empty to get your own loadout, or enter name/tag to verify.\n")
        
        player_name = input("Player Name (or press Enter to skip): ").strip() or None
        if player_name:
            player_tag = input("Player Tag: ").strip() or None
            player_region = input("Region (ap/na/eu/kr, or press Enter for auto): ").strip() or None
            platform = input("Platform (pc/console, default: pc): ").strip() or "pc"
    
    # Get loadout
    result = get_player_loadout_data(
        player_name=player_name,
        player_tag=player_tag,
        player_region=player_region,
        platform=platform
    )
    
    if result["success"]:
        display_loadout(result)
        
        # Save to file
        with open("player_loadout.json", "w", encoding="utf-8") as f:
            # Save parsed version (without raw)
            save_data = {
                "player": result["data"]["player"],
                "loadout": result["data"]["loadout"],
            }
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        print("\nLoadout saved to player_loadout.json")
    else:
        print(f"\nFailed to get loadout: {result['error']}")
        print(f"Error Code: {result['error_code']}")
        sys.exit(1)
