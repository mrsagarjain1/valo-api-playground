"""
Valorant Assets API Wrapper
===========================
A comprehensive Python wrapper for valorant-api.com
Provides access to all game assets: agents, weapons, skins, maps, and more.

Base URL: https://valorant-api.com/v1
No authentication required.
"""

import requests
from typing import Optional, List, Dict, Any


BASE_URL = "https://valorant-api.com/v1"

# Supported languages
LANGUAGES = [
    "ar-AE", "de-DE", "en-US", "es-ES", "es-MX", "fr-FR", "id-ID",
    "it-IT", "ja-JP", "ko-KR", "pl-PL", "pt-BR", "ru-RU", "th-TH",
    "tr-TR", "vi-VN", "zh-CN", "zh-TW"
]


# =============================================================================
# Helper Functions
# =============================================================================

def _make_request(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Make a GET request to the valorant-api.com API."""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": 0, "error": str(e), "data": None}


def _get_list(endpoint: str, language: Optional[str] = None) -> List[Dict]:
    """Get a list of items from an endpoint."""
    params = {"language": language} if language else None
    result = _make_request(endpoint, params)
    return result.get("data", [])


def _get_single(endpoint: str, uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a single item by UUID."""
    params = {"language": language} if language else None
    result = _make_request(f"{endpoint}/{uuid}", params)
    return result.get("data")


# =============================================================================
# Agents
# =============================================================================

def get_agents(language: Optional[str] = None, playable_only: bool = True) -> List[Dict]:
    """
    Get all agents.
    
    Args:
        language: Language code (e.g., 'ja-JP', 'ko-KR')
        playable_only: If True, excludes NPC agents (recommended to avoid duplicate Sova)
    
    Returns:
        List of agent dictionaries
    """
    params = {"language": language} if language else {}
    if playable_only:
        params["isPlayableCharacter"] = "true"
    result = _make_request("/agents", params)
    return result.get("data", [])


def get_agent(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific agent by UUID."""
    return _get_single("/agents", uuid, language)


def get_agent_by_name(name: str, language: Optional[str] = None) -> Optional[Dict]:
    """
    Get an agent by display name.
    
    Args:
        name: Agent name (case-insensitive, e.g., 'Jett', 'Chamber')
        language: Language code
    
    Returns:
        Agent dictionary or None if not found
    """
    agents = get_agents(language, playable_only=True)
    name_lower = name.lower()
    for agent in agents:
        if agent.get("displayName", "").lower() == name_lower:
            return agent
    return None


def get_agent_abilities(agent_uuid: str, language: Optional[str] = None) -> List[Dict]:
    """Get abilities for a specific agent."""
    agent = get_agent(agent_uuid, language)
    return agent.get("abilities", []) if agent else []


# =============================================================================
# Buddies (Gun Buddies)
# =============================================================================

def get_buddies(language: Optional[str] = None) -> List[Dict]:
    """Get all gun buddies."""
    return _get_list("/buddies", language)


def get_buddy(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific buddy by UUID."""
    return _get_single("/buddies", uuid, language)


def get_buddy_levels(language: Optional[str] = None) -> List[Dict]:
    """Get all buddy levels."""
    return _get_list("/buddies/levels", language)


def get_buddy_level(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific buddy level by UUID."""
    return _get_single("/buddies/levels", uuid, language)


# =============================================================================
# Bundles
# =============================================================================

def get_bundles(language: Optional[str] = None) -> List[Dict]:
    """Get all store bundles."""
    return _get_list("/bundles", language)


def get_bundle(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific bundle by UUID."""
    return _get_single("/bundles", uuid, language)


def get_bundle_by_name(name: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a bundle by display name (case-insensitive)."""
    bundles = get_bundles(language)
    name_lower = name.lower()
    for bundle in bundles:
        if name_lower in bundle.get("displayName", "").lower():
            return bundle
    return None


# =============================================================================
# Ceremonies
# =============================================================================

def get_ceremonies(language: Optional[str] = None) -> List[Dict]:
    """Get all victory/defeat ceremonies."""
    return _get_list("/ceremonies", language)


def get_ceremony(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific ceremony by UUID."""
    return _get_single("/ceremonies", uuid, language)


# =============================================================================
# Competitive Tiers (Ranks)
# =============================================================================

def get_competitive_tier_sets(language: Optional[str] = None) -> List[Dict]:
    """Get all competitive tier sets (different versions across episodes)."""
    return _get_list("/competitivetiers", language)


def get_competitive_tier_set(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific competitive tier set by UUID."""
    return _get_single("/competitivetiers", uuid, language)


def get_latest_competitive_tiers(language: Optional[str] = None) -> List[Dict]:
    """Get the latest/current competitive tier set."""
    tier_sets = get_competitive_tier_sets(language)
    if tier_sets:
        return tier_sets[-1].get("tiers", [])
    return []


def get_rank_by_tier(tier: int, language: Optional[str] = None) -> Optional[Dict]:
    """
    Get rank info by tier number.
    
    Tier numbers:
        0: Unranked, 3-5: Iron, 6-8: Bronze, 9-11: Silver,
        12-14: Gold, 15-17: Platinum, 18-20: Diamond,
        21-23: Ascendant, 24-26: Immortal, 27: Radiant
    """
    tiers = get_latest_competitive_tiers(language)
    for t in tiers:
        if t.get("tier") == tier:
            return t
    return None


# =============================================================================
# Content Tiers (Skin Rarity)
# =============================================================================

def get_content_tiers(language: Optional[str] = None) -> List[Dict]:
    """
    Get all content tiers (skin rarity levels).
    
    Tiers: Select, Deluxe, Premium, Exclusive, Ultra
    """
    return _get_list("/contenttiers", language)


def get_content_tier(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific content tier by UUID."""
    return _get_single("/contenttiers", uuid, language)


def get_content_tier_by_name(name: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get content tier by name (e.g., 'Ultra', 'Premium')."""
    tiers = get_content_tiers(language)
    name_lower = name.lower()
    for tier in tiers:
        if name_lower in tier.get("devName", "").lower():
            return tier
    return None


# =============================================================================
# Contracts (Battle Passes, Agent Contracts)
# =============================================================================

def get_contracts(language: Optional[str] = None) -> List[Dict]:
    """Get all contracts (battle passes, agent contracts, event passes)."""
    return _get_list("/contracts", language)


def get_contract(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific contract by UUID."""
    return _get_single("/contracts", uuid, language)


# =============================================================================
# Currencies
# =============================================================================

def get_currencies(language: Optional[str] = None) -> List[Dict]:
    """
    Get all in-game currencies.
    
    Currencies:
        - Valorant Points (VP)
        - Radianite Points
        - Kingdom Credits
        - Free Agents
    """
    return _get_list("/currencies", language)


def get_currency(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific currency by UUID."""
    return _get_single("/currencies", uuid, language)


def get_currency_by_name(name: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get currency by name (e.g., 'VP', 'Valorant Points', 'Radianite')."""
    currencies = get_currencies(language)
    name_lower = name.lower()
    for currency in currencies:
        display_name = currency.get("displayName", "").lower()
        if name_lower in display_name or display_name in name_lower:
            return currency
    return None


# Currency UUIDs for quick reference
CURRENCY_VP = "85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"
CURRENCY_RADIANITE = "e59aa87c-4cbf-517a-5983-6e81511be9b7"
CURRENCY_KINGDOM = "85ca954a-41f2-ce94-9b45-8ca3dd39a00d"
CURRENCY_FREE_AGENTS = "f08d4ae3-939c-4576-ab26-09ce1f23bb37"


# =============================================================================
# Events
# =============================================================================

def get_events(language: Optional[str] = None) -> List[Dict]:
    """Get all special events (RiotX Arcane, Anniversary, etc.)."""
    return _get_list("/events", language)


def get_event(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific event by UUID."""
    return _get_single("/events", uuid, language)


# =============================================================================
# Gamemodes
# =============================================================================

def get_gamemodes(language: Optional[str] = None) -> List[Dict]:
    """
    Get all game modes.
    
    Modes: Standard, Deathmatch, Spike Rush, Escalation, Team Deathmatch,
           Replication, Swiftplay, Snowball Fight, Skirmish, etc.
    """
    return _get_list("/gamemodes", language)


def get_gamemode(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific gamemode by UUID."""
    return _get_single("/gamemodes", uuid, language)


def get_gamemode_equippables(language: Optional[str] = None) -> List[Dict]:
    """Get all gamemode-specific equippables."""
    return _get_list("/gamemodes/equippables", language)


def get_gamemode_equippable(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific gamemode equippable by UUID."""
    return _get_single("/gamemodes/equippables", uuid, language)


# =============================================================================
# Gear (Armor)
# =============================================================================

def get_gear(language: Optional[str] = None) -> List[Dict]:
    """
    Get all gear items (armor).
    
    Items:
        - Light Armor (400 credits)
        - Heavy Armor (1000 credits)
        - Regen Shield (650 credits)
    """
    return _get_list("/gear", language)


def get_gear_item(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific gear item by UUID."""
    return _get_single("/gear", uuid, language)


# =============================================================================
# Level Borders
# =============================================================================

def get_level_borders(language: Optional[str] = None) -> List[Dict]:
    """Get all account level borders (change every 20 levels)."""
    return _get_list("/levelborders", language)


def get_level_border(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific level border by UUID."""
    return _get_single("/levelborders", uuid, language)


def get_level_border_for_level(level: int, language: Optional[str] = None) -> Optional[Dict]:
    """Get the level border for a specific account level."""
    borders = get_level_borders(language)
    # Sort by starting level descending to find the correct border
    borders_sorted = sorted(borders, key=lambda x: x.get("startingLevel", 0), reverse=True)
    for border in borders_sorted:
        if level >= border.get("startingLevel", 0):
            return border
    return borders[0] if borders else None


# =============================================================================
# Maps
# =============================================================================

def get_maps(language: Optional[str] = None) -> List[Dict]:
    """
    Get all maps.
    
    Competitive: Ascent, Bind, Breeze, Fracture, Haven, Icebox, Lotus, Pearl, Split, Sunset, Abyss
    TDM: District, Kasbah, Drift, Glitch, Piazza
    Other: The Range, Basic Training
    """
    return _get_list("/maps", language)


def get_map(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific map by UUID."""
    return _get_single("/maps", uuid, language)


def get_map_by_name(name: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a map by display name (case-insensitive)."""
    maps = get_maps(language)
    name_lower = name.lower()
    for m in maps:
        if m.get("displayName", "").lower() == name_lower:
            return m
    return None


def get_map_callouts(map_uuid: str, language: Optional[str] = None) -> List[Dict]:
    """Get callout regions for a specific map."""
    map_data = get_map(map_uuid, language)
    return map_data.get("callouts", []) if map_data else []


# =============================================================================
# Player Cards
# =============================================================================

def get_player_cards(language: Optional[str] = None) -> List[Dict]:
    """Get all player cards."""
    return _get_list("/playercards", language)


def get_player_card(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific player card by UUID."""
    return _get_single("/playercards", uuid, language)


def search_player_cards(query: str, language: Optional[str] = None) -> List[Dict]:
    """Search player cards by name."""
    cards = get_player_cards(language)
    query_lower = query.lower()
    return [c for c in cards if query_lower in c.get("displayName", "").lower()]


# =============================================================================
# Player Titles
# =============================================================================

def get_player_titles(language: Optional[str] = None) -> List[Dict]:
    """Get all player titles."""
    return _get_list("/playertitles", language)


def get_player_title(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific player title by UUID."""
    return _get_single("/playertitles", uuid, language)


def search_player_titles(query: str, language: Optional[str] = None) -> List[Dict]:
    """Search player titles by name or text."""
    titles = get_player_titles(language)
    query_lower = query.lower()
    return [
        t for t in titles 
        if query_lower in t.get("displayName", "").lower() 
        or query_lower in t.get("titleText", "").lower()
    ]


# =============================================================================
# Seasons
# =============================================================================

def get_seasons(language: Optional[str] = None) -> List[Dict]:
    """Get all seasons (acts and episodes)."""
    return _get_list("/seasons", language)


def get_season(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific season by UUID."""
    return _get_single("/seasons", uuid, language)


def get_competitive_seasons(language: Optional[str] = None) -> List[Dict]:
    """Get all competitive seasons with rank borders."""
    return _get_list("/seasons/competitive", language)


def get_competitive_season(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific competitive season by UUID."""
    return _get_single("/seasons/competitive", uuid, language)


def get_current_season(language: Optional[str] = None) -> Optional[Dict]:
    """Get the current/latest season."""
    seasons = get_seasons(language)
    if seasons:
        # Filter to acts and get the last one
        acts = [s for s in seasons if "Act" in s.get("displayName", "")]
        return acts[-1] if acts else seasons[-1]
    return None


def get_acts(language: Optional[str] = None) -> List[Dict]:
    """Get all acts (filter out episodes)."""
    seasons = get_seasons(language)
    return [s for s in seasons if s.get("type") == "EAresSeasonType::Act"]


# =============================================================================
# Sprays
# =============================================================================

def get_sprays(language: Optional[str] = None) -> List[Dict]:
    """Get all sprays."""
    return _get_list("/sprays", language)


def get_spray(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific spray by UUID."""
    return _get_single("/sprays", uuid, language)


def get_spray_levels(language: Optional[str] = None) -> List[Dict]:
    """Get all spray levels."""
    return _get_list("/sprays/levels", language)


def get_spray_level(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific spray level by UUID."""
    return _get_single("/sprays/levels", uuid, language)


def search_sprays(query: str, language: Optional[str] = None) -> List[Dict]:
    """Search sprays by name."""
    sprays = get_sprays(language)
    query_lower = query.lower()
    return [s for s in sprays if query_lower in s.get("displayName", "").lower()]


# =============================================================================
# Themes (Skin Collections)
# =============================================================================

def get_themes(language: Optional[str] = None) -> List[Dict]:
    """Get all skin themes/collections (e.g., Prime, Elderflame, Reaver)."""
    return _get_list("/themes", language)


def get_theme(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific theme by UUID."""
    return _get_single("/themes", uuid, language)


def get_theme_by_name(name: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a theme by name (case-insensitive)."""
    themes = get_themes(language)
    name_lower = name.lower()
    for theme in themes:
        if name_lower in theme.get("displayName", "").lower():
            return theme
    return None


# =============================================================================
# Weapons
# =============================================================================

def get_weapons(language: Optional[str] = None) -> List[Dict]:
    """
    Get all weapons.
    
    Categories:
        - Sidearms: Classic, Shorty, Frenzy, Ghost, Sheriff
        - SMGs: Stinger, Spectre
        - Shotguns: Bucky, Judge
        - Rifles: Bulldog, Guardian, Phantom, Vandal
        - Snipers: Marshal, Outlaw, Operator
        - Machine Guns: Ares, Odin
        - Melee
    """
    return _get_list("/weapons", language)


def get_weapon(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific weapon by UUID."""
    return _get_single("/weapons", uuid, language)


def get_weapon_by_name(name: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a weapon by display name (case-insensitive)."""
    weapons = get_weapons(language)
    name_lower = name.lower()
    for weapon in weapons:
        if weapon.get("displayName", "").lower() == name_lower:
            return weapon
    return None


def get_weapon_skins(weapon_uuid: str, language: Optional[str] = None) -> List[Dict]:
    """Get all skins for a specific weapon."""
    weapon = get_weapon(weapon_uuid, language)
    return weapon.get("skins", []) if weapon else []


def get_weapon_stats(weapon_uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get stats for a specific weapon."""
    weapon = get_weapon(weapon_uuid, language)
    return weapon.get("weaponStats") if weapon else None


# =============================================================================
# Weapon Skins
# =============================================================================

def get_all_skins(language: Optional[str] = None) -> List[Dict]:
    """Get all weapon skins across all weapons."""
    return _get_list("/weapons/skins", language)


def get_skin(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific skin by UUID."""
    return _get_single("/weapons/skins", uuid, language)


def get_skin_by_name(name: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a skin by display name (case-insensitive, partial match)."""
    skins = get_all_skins(language)
    name_lower = name.lower()
    for skin in skins:
        if name_lower in skin.get("displayName", "").lower():
            return skin
    return None


def search_skins(query: str, language: Optional[str] = None) -> List[Dict]:
    """Search skins by name."""
    skins = get_all_skins(language)
    query_lower = query.lower()
    return [s for s in skins if query_lower in s.get("displayName", "").lower()]


# =============================================================================
# Skin Levels
# =============================================================================

def get_all_skin_levels(language: Optional[str] = None) -> List[Dict]:
    """Get all skin levels."""
    return _get_list("/weapons/skinlevels", language)


def get_skin_level(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """
    Get a specific skin level by UUID.
    
    This is useful for resolving skin UUIDs from the store API.
    """
    return _get_single("/weapons/skinlevels", uuid, language)


def get_skin_name_from_level(level_uuid: str, language: Optional[str] = None) -> Optional[str]:
    """Get the display name for a skin level UUID."""
    level = get_skin_level(level_uuid, language)
    return level.get("displayName") if level else None


# =============================================================================
# Skin Chromas
# =============================================================================

def get_all_skin_chromas(language: Optional[str] = None) -> List[Dict]:
    """Get all skin chromas."""
    return _get_list("/weapons/skinchromas", language)


def get_skin_chroma(uuid: str, language: Optional[str] = None) -> Optional[Dict]:
    """Get a specific skin chroma by UUID."""
    return _get_single("/weapons/skinchromas", uuid, language)


# =============================================================================
# Version
# =============================================================================

def get_version() -> Optional[Dict]:
    """
    Get the current game version.
    
    Returns dict with:
        - manifestId
        - branch (e.g., 'release-11.11')
        - version (e.g., '11.11.00.4026545')
        - buildVersion
        - engineVersion
        - riotClientVersion
        - riotClientBuild
        - buildDate
    """
    result = _make_request("/version")
    return result.get("data")


def get_client_version() -> Optional[str]:
    """Get the current Riot client version string (for API headers)."""
    version = get_version()
    return version.get("riotClientVersion") if version else None


def get_game_version() -> Optional[str]:
    """Get the current game version string."""
    version = get_version()
    return version.get("version") if version else None


# =============================================================================
# Utility Functions
# =============================================================================

def download_asset(url: str, save_path: str) -> bool:
    """
    Download an asset (image, video) to a file.
    
    Args:
        url: URL of the asset
        save_path: Local path to save the file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading asset: {e}")
        return False


def get_media_url(asset_type: str, uuid: str, asset_name: str) -> str:
    """
    Build a media URL for an asset.
    
    Args:
        asset_type: Type of asset (agents, weapons, playercards, etc.)
        uuid: UUID of the item
        asset_name: Name of the asset file (displayicon, fullportrait, etc.)
    
    Returns:
        Full media URL
    
    Example:
        get_media_url("agents", "some-uuid", "displayicon.png")
    """
    return f"https://media.valorant-api.com/{asset_type}/{uuid}/{asset_name}"


# =============================================================================
# Main / Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Valorant Assets API Demo")
    print("=" * 60)
    
    # Version
    print("\nGame Version:")
    version = get_version()
    if version:
        print(f"   Version: {version.get('version')}")
        print(f"   Client: {version.get('riotClientVersion')}")
        print(f"   Build Date: {version.get('buildDate')}")
    
    # Agents
    print("\nAgents:")
    agents = get_agents(playable_only=True)
    print(f"   Total: {len(agents)} playable agents")
    print(f"   Names: {', '.join(a['displayName'] for a in agents[:5])}...")
    
    # Get specific agent
    chamber = get_agent_by_name("Chamber")
    if chamber:
        print(f"\n   Chamber's role: {chamber.get('role', {}).get('displayName')}")
        print(f"   Abilities: {', '.join(a['displayName'] for a in chamber.get('abilities', []))}")
    
    # Weapons
    print("\nWeapons:")
    weapons = get_weapons()
    print(f"   Total: {len(weapons)} weapons")
    print(f"   Names: {', '.join(w['displayName'] for w in weapons)}")
    
    # Skins
    vandal = get_weapon_by_name("Vandal")
    if vandal:
        skins = vandal.get("skins", [])
        print(f"\n   Vandal skins: {len(skins)}")
        print(f"   Sample: {', '.join(s['displayName'] for s in skins[:5])}...")
    
    # Maps
    print("\nMaps:")
    maps = get_maps()
    comp_maps = [m for m in maps if m.get("tacticalDescription")]
    print(f"   Total: {len(maps)} maps ({len(comp_maps)} competitive)")
    print(f"   Competitive: {', '.join(m['displayName'] for m in comp_maps[:6])}...")
    
    # Ranks
    print("\nCompetitive Tiers:")
    tiers = get_latest_competitive_tiers()
    ranks = [t for t in tiers if t.get("tierName") not in ["UNRANKED", "Unused1", "Unused2"]]
    print(f"   Total: {len(ranks)} ranks")
    print(f"   Ranks: {', '.join(t['tierName'] for t in ranks[::3])}")
    
    # Currencies
    print("\nCurrencies:")
    currencies = get_currencies()
    for c in currencies:
        print(f"   - {c.get('displayName')}")
    
    # Bundles
    print("\nBundles:")
    bundles = get_bundles()
    print(f"   Total: {len(bundles)} bundles")
    print(f"   Recent: {', '.join(b['displayName'] for b in bundles[-5:])}")
    
    print("\n" + "=" * 60)
    print("Demo complete! Use these functions in your code.")
    print("=" * 60)
