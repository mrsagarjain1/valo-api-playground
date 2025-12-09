import json
import requests

from valo_api_utils import (
    CLIENT_PLATFORM,
    get_entitlement_token,
    get_client_version,
    get_player_region,
    region_to_shard,
    cookie_reauth,
    TIER_MAP,
    SEASON_MAP,
    get_tier_name,
    season_short,
    get_puuid_by_name,
    get_player_mmr,
    get_competitive_updates,
)


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
