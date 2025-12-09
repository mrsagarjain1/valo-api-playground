import json
import sys
from datetime import datetime, UTC
import requests

from valo_api_utils import (
    CLIENT_PLATFORM,
    get_entitlement_token,
    get_client_version,
    get_player_region,
    region_to_shard,
    cookie_reauth,
)

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

def get_tier_name(tier_id: int, season_short_str: str) -> str:
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


def get_puuid_by_name(game_name: str, tag_line: str, access_token: str):
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


def get_player_mmr(puuid: str, access_token: str, entitlement_token: str, shard: str):
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


def get_competitive_updates(puuid: str, access_token: str, entitlement_token: str, shard: str, limit: int = 2000):
    """Pull competitive updates (match-by-match MMR changes) with simple pagination."""
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


def season_short(season_id: str) -> str:
    """Convert season UUID to episode/act notation (e.g. e8a3)"""
    return SEASON_MAP.get(season_id, season_id[:4].lower() if season_id else "unknown")


def map_mmr_to_henrik(game_name: str, tag_line: str, puuid: str, mmr: dict, act_id: str = "") -> dict:
    queue = mmr.get("QueueSkills", {}).get("competitive", {})
    seasonal = queue.get("SeasonalInfoBySeasonID", {}) if queue else {}
    latest_update = mmr.get("LatestCompetitiveUpdate") or {}

    # Rank protection shields (demotion protection)
    rank_protection = mmr.get("DerankProtectedGamesRemaining", 0)

    # Find peak across ALL seasons by scanning WinsByTier for highest tier
    # (Henrik finds peak by looking at all wins across all seasons, not just end tier)
    peak_tier = 0
    peak_rr = 0
    peak_season_id = None
    for sid, data in seasonal.items():
        wins_by_tier = data.get("WinsByTier", {})
        end_rr = data.get("RankedRating", 0)
        
        # Find highest tier in this season's wins
        if wins_by_tier:
            max_tier_in_season = max((int(t) for t in wins_by_tier.keys()), default=0)
            if max_tier_in_season > peak_tier:
                peak_tier = max_tier_in_season
                peak_rr = end_rr  # Use end RR for that season
                peak_season_id = sid
            elif max_tier_in_season == peak_tier and end_rr > peak_rr:
                peak_rr = end_rr
                peak_season_id = sid

    # Current season data - use act_id if provided, otherwise use latest
    current_season_id = None
    current_tier = 0
    current_rr = 0
    current_data = {}
    is_current_act = False
    
    # Get the actual current season from LatestCompetitiveUpdate
    latest_season_id = latest_update.get("SeasonID", "")
    
    if seasonal:
        if act_id:
            # Find season_id that matches the act_id (e.g., "v25a6" -> UUID)
            season_uuid = None
            for uuid, short in SEASON_MAP.items():
                if short == act_id:
                    season_uuid = uuid
                    break
            
            if season_uuid and season_uuid in seasonal:
                current_season_id = season_uuid
                current_data = seasonal[current_season_id]
                # Check if this is the current/active season
                is_current_act = (season_uuid == latest_season_id)
            else:
                # Act ID not found in player's data, fall back to latest
                current_season_id = latest_season_id if latest_season_id in seasonal else sorted(seasonal.keys())[-1]
                current_data = seasonal.get(current_season_id, {})
                is_current_act = True
        else:
            # No act_id specified - use the current season from LatestCompetitiveUpdate
            if latest_season_id and latest_season_id in seasonal:
                current_season_id = latest_season_id
                current_data = seasonal[current_season_id]
            else:
                # Fallback: sort seasons to find most recent
                sorted_seasons = sorted(seasonal.keys())
                current_season_id = sorted_seasons[-1]
                current_data = seasonal[current_season_id]
            is_current_act = True
        
        # Get current RR and tier
        if is_current_act and latest_update:
            # For the current/active act, use LatestCompetitiveUpdate for most accurate data
            current_tier = latest_update.get("TierAfterUpdate", current_data.get("CompetitiveTier", 0))
            current_rr = latest_update.get("RankedRatingAfterUpdate", 0)
        else:
            # For historical acts, use the seasonal data
            current_tier = current_data.get("CompetitiveTier", 0)
            current_rr = current_data.get("RankedRating", 0)

    # Leaderboard placement from the selected season's data
    leaderboard_placement = current_data.get("LeaderboardRank", 0) if current_data else 0
    
    return {
        "games_needed_for_rating": queue.get("CurrentSeasonGamesNeededForRating", 0),
        "current_rank": get_tier_name(current_tier, season_short(current_season_id or "")),
        "current_rr": current_rr,
        "rank_protection_shields": rank_protection,
        "leaderboard_placement": leaderboard_placement,
        "peak_rank": get_tier_name(peak_tier, season_short(peak_season_id or "")),
        "peak_rr": peak_rr,
        "peak_act": season_short(peak_season_id or "")
    }


def get_player_mmr_data(game_name: str, tag_line: str, region: str = "", platform: str = "pc", act_id: str = "") -> dict:
    """
    Fetch player MMR data in Henrik API format.
    
    Args:
        game_name: Player's Riot game name
        tag_line: Player's tag (without #)
        region: Region override (na/eu/ap/kr) or empty string to auto-detect
        platform: Platform (pc/console, currently unused)
        act_id: Act ID to filter data for (optional)
    
    Returns:
        Dict with status and data in Henrik format, or error response
    """
    tokens = cookie_reauth()
    if not tokens or not tokens.get("access_token"):
        return {
            "status": 500,
            "error": "auth_failed",
            "message": "Failed to authenticate with Riot servers. Please refresh your cookies."
        }

    access_token = tokens["access_token"]
    id_token = tokens.get("id_token", "")

    entitlement = get_entitlement_token(access_token)
    if not entitlement:
        return {
            "status": 500,
            "error": "entitlement_failed",
            "message": "Failed to get entitlement token from Riot servers."
        }

    detected_region = region or get_player_region(access_token, id_token) or "na"
    shard = region_to_shard(detected_region)

    puuid = get_puuid_by_name(game_name, tag_line, access_token)
    if not puuid:
        return {
            "status": 404,
            "error": "player_not_found",
            "message": f"Player '{game_name}#{tag_line}' not found. Please check the name and tag."
        }

    mmr = get_player_mmr(puuid, access_token, entitlement, shard)
    if not mmr:
        return {
            "status": 502,
            "error": "mmr_fetch_failed",
            "message": f"Failed to fetch MMR data for player '{game_name}#{tag_line}'."
        }

    return map_mmr_to_henrik(game_name, tag_line, puuid, mmr, act_id)


def main():
    # Inputs: name, tag, region (optional), platform (ignored but accepted)
    game_name = input("Enter player Game Name: ").strip()
    tag_line = input("Enter player Tag (without #): ").strip()
    region_in = input("Enter region (na/eu/ap/kr or blank to auto): ").strip().lower()
    platform = input("Enter platform (pc/console, unused): ").strip().lower()

    output = get_player_mmr_data(game_name, tag_line, region_in, platform)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
