"""
Get the player's owned items (agents, skins, buddies, sprays, cards, titles, etc.).

Endpoint used:
- GET Owned Items: https://pd.{shard}.a.pvp.net/store/v1/entitlements/{puuid}/{ItemTypeID}

Note: This endpoint only works for your own PUUID (authenticated account).
You cannot view other players' owned items.
"""

import json
import requests
from typing import Optional, Dict, List, Any

from valo_api_utils import (
    CLIENT_PLATFORM,
    get_entitlement_token,
    get_client_version,
    get_player_region,
    region_to_shard,
    get_player_info,
    cookie_reauth,
)


# Item Type IDs for owned items endpoint
ITEM_TYPE_IDS = {
    "01bb38e1-da47-4e6a-9b3d-945fe4655707": "Agents",
    "f85cb6f7-33e5-4dc8-b609-ec7212301948": "Contracts",
    "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475": "Sprays",
    "dd3bf334-87f3-40bd-b043-682a57a8dc3a": "Gun Buddies",
    "3f296c07-64c3-494c-923b-fe692a4fa1bd": "Cards",
    "e7c63390-eda7-46e0-bb7a-a6abdacd2433": "Skins",
    "3ad1b2b2-acdb-4524-852f-954a76ddae0a": "Skin Variants",
    "de7caa6b-adf7-4588-bbd1-143831e786c6": "Titles",
}

# Reverse mapping for lookup by name
ITEM_TYPE_BY_NAME = {v.lower(): k for k, v in ITEM_TYPE_IDS.items()}


def get_owned_items_by_type(
    puuid: str, 
    access_token: str, 
    entitlement_token: str, 
    shard: str,
    item_type_id: str
) -> Optional[dict]:
    """
    Get owned items for a specific item type.
    
    Args:
        puuid: Player UUID
        access_token: Auth token
        entitlement_token: Entitlement JWT
        shard: Server shard (na, eu, ap, kr)
        item_type_id: Item type UUID (see ITEM_TYPE_IDS)
    
    Returns:
        Raw response with entitlements or None if failed
    """
    client_version = get_client_version()
    url = f"https://pd.{shard}.a.pvp.net/store/v1/entitlements/{puuid}/{item_type_id}"
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Owned items request failed: {res.status_code}")
        print(f"Response: {res.text[:500] if res.text else 'Empty'}")
        return None
    return res.json()


def get_all_owned_items(
    puuid: str, 
    access_token: str, 
    entitlement_token: str, 
    shard: str
) -> Dict[str, List[str]]:
    """
    Get all owned items across all categories.
    
    Returns:
        Dict mapping category name to list of item IDs
    """
    result = {}
    
    for item_type_id, item_type_name in ITEM_TYPE_IDS.items():
        data = get_owned_items_by_type(puuid, access_token, entitlement_token, shard, item_type_id)
        if data:
            entitlements = data.get("Entitlements", [])
            item_ids = [e.get("ItemID", "") for e in entitlements]
            result[item_type_name] = item_ids
    
    return result


# =============================================================================
# Name resolution functions using valorant-api.com
# =============================================================================

def get_agent_name(agent_uuid: str) -> str:
    """Get agent name from valorant-api.com."""
    if not agent_uuid:
        return agent_uuid
    try:
        url = f"https://valorant-api.com/v1/agents/{agent_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", agent_uuid)
    except Exception:
        pass
    return agent_uuid


def get_skin_name(skin_uuid: str) -> str:
    """Get skin name from valorant-api.com."""
    if not skin_uuid:
        return skin_uuid
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
    """Get skin chroma/variant name from valorant-api.com."""
    if not chroma_uuid:
        return chroma_uuid
    try:
        url = f"https://valorant-api.com/v1/weapons/skinchromas/{chroma_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", chroma_uuid)
    except Exception:
        pass
    return chroma_uuid


def get_buddy_name(buddy_uuid: str) -> str:
    """Get buddy name from valorant-api.com."""
    if not buddy_uuid:
        return buddy_uuid
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
        return spray_uuid
    try:
        url = f"https://valorant-api.com/v1/sprays/{spray_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", spray_uuid)
    except Exception:
        pass
    return spray_uuid


def get_card_name(card_uuid: str) -> str:
    """Get player card name from valorant-api.com."""
    if not card_uuid:
        return card_uuid
    try:
        url = f"https://valorant-api.com/v1/playercards/{card_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", card_uuid)
    except Exception:
        pass
    return card_uuid


def get_title_name(title_uuid: str) -> str:
    """Get player title text from valorant-api.com."""
    if not title_uuid:
        return title_uuid
    try:
        url = f"https://valorant-api.com/v1/playertitles/{title_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()["data"]
            return data.get("titleText") or data.get("displayName", title_uuid)
    except Exception:
        pass
    return title_uuid


def get_contract_name(contract_uuid: str) -> str:
    """Get contract name from valorant-api.com."""
    if not contract_uuid:
        return contract_uuid
    try:
        url = f"https://valorant-api.com/v1/contracts/{contract_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", contract_uuid)
    except Exception:
        pass
    return contract_uuid


def resolve_item_names(category: str, item_ids: List[str], max_items: int = 50) -> List[Dict[str, str]]:
    """
    Resolve item UUIDs to names for a category.
    
    Args:
        category: Category name (Agents, Skins, etc.)
        item_ids: List of item UUIDs
        max_items: Maximum items to resolve (to avoid too many API calls)
    
    Returns:
        List of dicts with uuid and name
    """
    result = []
    
    # Select the appropriate resolver
    resolvers = {
        "Agents": get_agent_name,
        "Skins": get_skin_name,
        "Skin Variants": get_chroma_name,
        "Gun Buddies": get_buddy_name,
        "Sprays": get_spray_name,
        "Cards": get_card_name,
        "Titles": get_title_name,
        "Contracts": get_contract_name,
    }
    
    resolver = resolvers.get(category)
    
    for item_id in item_ids[:max_items]:
        if resolver:
            name = resolver(item_id)
        else:
            name = item_id
        result.append({"uuid": item_id, "name": name})
    
    return result


def get_owned_items_data(
    player_name: Optional[str] = None,
    player_tag: Optional[str] = None,
    player_region: Optional[str] = None,
    platform: str = "pc",
    resolve_names: bool = False,
    categories: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get the authenticated player's owned items.
    
    Note: The owned items endpoint only works for your own PUUID.
    If player_name and player_tag are provided, they are used to verify
    that the authenticated account matches the requested player.
    
    Args:
        player_name: Player's game name (optional, for verification)
        player_tag: Player's tag line (optional, for verification)
        player_region: Player's region (optional, e.g., 'ap', 'na', 'eu', 'kr')
        platform: Platform (default: 'pc')
        resolve_names: Whether to resolve item UUIDs to names (slower)
        categories: List of categories to fetch (default: all)
                   Valid: Agents, Contracts, Sprays, Gun Buddies, Cards, 
                          Skins, Skin Variants, Titles
    
    Returns:
        Dict with:
        - success: bool
        - data: Owned items data (if success)
        - error: Error message (if failed)
        - error_code: Error code (if failed)
            - "AUTH_FAILED": Cookie authentication failed
            - "ENTITLEMENT_FAILED": Failed to get entitlement token
            - "PLAYER_INFO_FAILED": Failed to get player info
            - "REGION_FAILED": Failed to get region
            - "PLAYER_NOT_FOUND": Authenticated player doesn't match requested player
            - "FETCH_FAILED": Failed to fetch owned items
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
                         f"The owned items endpoint only works for the authenticated account ({game_name}#{tag_line}). "
                         f"You cannot view other players' owned items.",
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
    
    # Determine which categories to fetch
    if categories:
        # Map category names to IDs
        fetch_categories = {}
        for cat in categories:
            cat_lower = cat.lower()
            if cat_lower in ITEM_TYPE_BY_NAME:
                type_id = ITEM_TYPE_BY_NAME[cat_lower]
                fetch_categories[type_id] = ITEM_TYPE_IDS[type_id]
            elif cat in ITEM_TYPE_IDS:
                fetch_categories[cat] = ITEM_TYPE_IDS[cat]
    else:
        fetch_categories = ITEM_TYPE_IDS
    
    # Fetch owned items
    print("\nFetching owned items...")
    owned_items = {}
    raw_data = {}
    
    for item_type_id, item_type_name in fetch_categories.items():
        print(f"  - {item_type_name}...", end=" ")
        data = get_owned_items_by_type(puuid, access_token, entitlement_token, shard, item_type_id)
        if data:
            entitlements = data.get("Entitlements", [])
            item_ids = [e.get("ItemID", "") for e in entitlements]
            
            if resolve_names:
                owned_items[item_type_name] = resolve_item_names(item_type_name, item_ids)
            else:
                owned_items[item_type_name] = item_ids
            
            raw_data[item_type_name] = data
            print(f"{len(item_ids)} items")
        else:
            owned_items[item_type_name] = []
            print("failed")
    
    # Count totals
    total_items = sum(len(items) for items in owned_items.values())
    
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
            "owned_items": owned_items,
            "summary": {
                "total_items": total_items,
                "by_category": {k: len(v) for k, v in owned_items.items()}
            },
            "raw": raw_data,
        },
        "error": None,
        "error_code": None
    }


def display_owned_items(result: Dict[str, Any], show_items: bool = False) -> None:
    """Display owned items in a readable format."""
    if not result["success"]:
        print(f"\nError: {result['error']}")
        print(f"Error Code: {result['error_code']}")
        return
    
    data = result["data"]
    player = data["player"]
    owned = data["owned_items"]
    summary = data["summary"]
    
    print("\n" + "=" * 60)
    print(f"OWNED ITEMS - {player['name']}#{player['tag']}")
    print("=" * 60)
    
    print(f"\nTotal Items: {summary['total_items']}")
    print("\n[SUMMARY BY CATEGORY]")
    for category, count in summary["by_category"].items():
        print(f"  {category}: {count}")
    
    if show_items:
        print("\n[ITEMS BY CATEGORY]")
        for category, items in owned.items():
            print(f"\n  {category} ({len(items)}):")
            for item in items[:20]:  # Show first 20
                if isinstance(item, dict):
                    print(f"    - {item['name']}")
                else:
                    print(f"    - {item}")
            if len(items) > 20:
                print(f"    ... and {len(items) - 20} more")
    
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
        print("Get Owned Items")
        print("-" * 40)
        print("Note: This only works for your own account (authenticated via cookies).")
        print("Leave empty to get your own items, or enter name/tag to verify.\n")
        
        player_name = input("Player Name (or press Enter to skip): ").strip() or None
        if player_name:
            player_tag = input("Player Tag: ").strip() or None
            player_region = input("Region (ap/na/eu/kr, or press Enter for auto): ").strip() or None
            platform = input("Platform (pc/console, default: pc): ").strip() or "pc"
    
    # Ask about name resolution
    resolve = input("\nResolve item names? (y/n, default: n): ").strip().lower() == "y"
    
    # Get owned items
    result = get_owned_items_data(
        player_name=player_name,
        player_tag=player_tag,
        player_region=player_region,
        platform=platform,
        resolve_names=resolve
    )
    
    if result["success"]:
        display_owned_items(result, show_items=resolve)
        
        # Save to file
        with open("owned_items.json", "w", encoding="utf-8") as f:
            # Save without raw data to reduce file size
            save_data = {
                "player": result["data"]["player"],
                "owned_items": result["data"]["owned_items"],
                "summary": result["data"]["summary"],
            }
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        print("\nOwned items saved to owned_items.json")
    else:
        print(f"\nFailed to get owned items: {result['error']}")
        print(f"Error Code: {result['error_code']}")
        sys.exit(1)
