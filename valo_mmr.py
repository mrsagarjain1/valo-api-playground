import json
import sys
from datetime import datetime, UTC
import requests

from cookies import cookie_reauth

# Static client platform (base64 encoded JSON)
CLIENT_PLATFORM = (
    "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
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
SEASON_MAP = {
    "0530b9c4-4980-f2ee-df5d-09864cd00542": "e1a2",
    "46ea6166-4573-1128-9cea-60a15640059b": "e1a3",
    "97b6e739-44cc-ffa7-49ad-398ba502ceb0": "e2a1",
    "ab57ef51-4e59-da91-cc8d-51a5a2b9b8ff": "e2a2",
    "52e9749a-429b-7060-99fe-4595426a0cf7": "e2a3",
    "16118998-4705-5813-86dd-0292a2439d90": "e3a1",
    "4cb622e1-4244-6da3-7276-8daaf1c01be2": "e3a2",
    "a16955a5-4ad0-f761-5e9e-389df1c892fb": "e3a3",
    "573f53ac-41a5-3a7d-d9ce-d6a6298e5704": "e4a1",
    "d929bc38-4ab6-7da4-94f0-ee84f8ac141e": "e4a2",
    "3e47230a-463c-a301-eb7d-67bb60357d4f": "e4a3",
    "67e373c7-48f7-b422-641b-079ace30b427": "e5a1",
    "7a85de9a-4032-61a9-61d8-f4aa2b4a84b6": "e5a2",
    "aca29595-40e4-01f5-3f35-b1b3d304c96e": "e5a3",
    "9c91a445-4f78-1baa-a3ea-8f8aadf4914d": "e6a1",
    "34093c29-4306-43de-452f-3f944bde22be": "e6a2",
    "2de5423b-4aad-02ad-8d9b-c0a931958861": "e6a3",
    "4d4ce85a-f26f-d7e1-fb23-f02dc69dc52c": "e7a1",
    "03dfd004-45d4-ebfd-ab0a-948ce780dac4": "e7a2",
    "4401f9fd-4170-2e4c-4bc3-f3b4d7d150d1": "e7a3",
    "22d10d66-4d2a-a340-6c54-408c7bd53807": "e8a1",
    "292f58db-4c17-89a7-b1c0-ba988f0e9d98": "e8a2",
    "4539cac3-47ae-90e5-3d01-b3812ca3274e": "e8a3",
    "476b0893-4c2e-abd6-c5fe-708facff0772": "e9a1",
    "4c4b8cff-43eb-13d3-8f14-96b783c90cd2": "e9a2",
    "dcde7346-4085-de4f-c463-2489ed47983b": "e9a3",
    "476b92e4-88ac-d0ea-4c0f-84838b62b0d7": "e10a1",
    "1611cbeb-c1e6-d92d-22f6-8a8084e4c5a7": "e10a2",
    "aef237a0-494d-3a14-a1c8-ec8de84e309c": "e10a3",
    "ac12e9b3-47e6-9599-8fa1-0bb473e5efc7": "e10a4",
    "5adc33fa-4f30-2899-f131-6fba64c5dd3a": "e10a5",
    "4c4bf00b-e78a-7a79-04af-0aa63068e4e2": "e10a6",
    "ec876e6c-43e8-fa63-ffc1-2e8d4db25525": "e10a7",
}


def get_entitlement_token(access_token: str):
    url = "https://entitlements.auth.riotgames.com/api/token/v1"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json={})
    if res.status_code != 200:
        return None
    return res.json().get("entitlements_token")


def get_client_version():
    url = "https://valorant-api.com/v1/version"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("riotClientVersion")
    except Exception:
        pass
    return "release-10.00-shipping-9-2555555"


def get_player_region(access_token: str, id_token: str):
    url = "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.put(url, headers=headers, json={"id_token": id_token})
    if res.status_code != 200:
        return None
    return res.json().get("affinities", {}).get("live")


def region_to_shard(region: str):
    shard_map = {"latam": "na", "br": "na", "na": "na", "pbe": "pbe", "eu": "eu", "ap": "ap", "kr": "kr"}
    return shard_map.get(region, "na")


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


def map_mmr_to_henrik(game_name: str, tag_line: str, puuid: str, mmr: dict, updates: list[dict]) -> dict:
    queue = mmr.get("QueueSkills", {}).get("competitive", {})
    seasonal = queue.get("SeasonalInfoBySeasonID", {}) if queue else {}

    def to_iso(ts_ms: int) -> str:
        if not ts_ms:
            return datetime.now(UTC).isoformat().replace("+00:00", "Z")
        return datetime.fromtimestamp(ts_ms / 1000, tz=UTC).isoformat().replace("+00:00", "Z")

    # Build act_wins from WinsByTier (like Henrik does)
    def build_act_wins(wins_by_tier: dict, season_short_str: str) -> list[dict]:
        if not wins_by_tier:
            return []
        act_wins = []
        # WinsByTier is a dict like {"3": 2, "15": 10, ...} where key is tier id
        for tier_str, count in wins_by_tier.items():
            tier_id = int(tier_str)
            for _ in range(count):
                act_wins.append({"id": tier_id, "name": get_tier_name(tier_id, season_short_str)})
        
        # Sort by ID descending (highest rank first)
        act_wins.sort(key=lambda x: x["id"], reverse=True)
        return act_wins

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

    # Determine ranking schema based on season
    def get_ranking_schema(season_id: str) -> str:
        short = season_short(season_id)
        # Episode 5+ uses ascendant schema
        if short and short.startswith("e"):
            try:
                # Extract episode number from format like "e10a7" or "e5a1"
                ep_str = short[1:].split('a')[0]
                ep_num = int(ep_str)
                if ep_num >= 5:
                    return "ascendant"
            except (ValueError, IndexError):
                pass
        return "base"

    # Current season data
    current_season_id = None
    current_tier = 0
    current_rr = 0
    current_data = {}
    latest_competitive_update = mmr.get("LatestCompetitiveUpdate") or {}
    
    if seasonal:
        # Sort seasons to find current (latest by UUID sort order)
        sorted_seasons = sorted(seasonal.keys())
        current_season_id = sorted_seasons[-1]  # Last one is most recent
        current_data = seasonal[current_season_id]
        current_tier = current_data.get("CompetitiveTier", 0)
        current_rr = current_data.get("RankedRating", 0)

    last_change = latest_competitive_update.get("RankedRatingEarned", 0)
    afk_penalty = latest_competitive_update.get("AFKPenalty", 0)
    
    # Calculate ELO using Henrik's formula
    # ELO = (tier - 3) * 100 + (rr % 100)
    # Example: Immortal 3 (26) with 291 RR = (26-3)*100 + 91 = 2300 + 91 = 2391
    current_elo = ((current_tier - 3) * 100) + (current_rr % 100) if current_tier >= 3 else 0

    # Build seasonal breakdown (sorted chronologically: oldest first)
    def sort_key_season(sid: str) -> tuple:
        """Sort seasons chronologically by episode and act"""
        short = season_short(sid)
        try:
            # Extract episode and act from format like "e8a3"
            if short.startswith("e"):
                parts = short[1:].split("a")
                if len(parts) == 2:
                    ep = int(parts[0])
                    act = int(parts[1])
                    return (ep, act)
        except (ValueError, IndexError):
            pass
        return (999, 999)  # Unknown seasons go to the end
    
    seasonal_list = []
    for sid in sorted(seasonal.keys(), key=sort_key_season):
        short = season_short(sid)
        # Skip unmapped seasons (those that don't start with 'e')
        if not short.startswith("e"):
            continue
        
        season_data = seasonal[sid]
        tier_id = season_data.get("CompetitiveTier", 0)
        rr = season_data.get("RankedRating", 0)
        wins = season_data.get("NumberOfWins", 0)
        games = season_data.get("NumberOfGames", 0)
        leaderboard_rank = season_data.get("LeaderboardRank", 0)
        wins_by_tier = season_data.get("WinsByTier")
        
        # Build act_wins from WinsByTier
        act_wins = build_act_wins(wins_by_tier, short)
        
        # Find latest update timestamp for this season
        season_updates = [u for u in updates if u.get("SeasonID") == sid]
        latest_time = max([u.get("MatchStartTime", 0) for u in season_updates], default=0)
        
        seasonal_list.append({
            "season": {"id": sid, "short": season_short(sid)},
            "wins": wins,
            "games": games,
            "end_tier": {"id": tier_id, "name": get_tier_name(tier_id, short)},
            "end_rr": rr,
            "ranking_schema": get_ranking_schema(sid),
            "leaderboard_placement": {
                "rank": leaderboard_rank,
                "updated_at": to_iso(latest_time)
            } if leaderboard_rank > 0 else None,
            "act_wins": act_wins
        })

    output = {
        "status": 200,
        "data": {
            "account": {"name": game_name, "tag": tag_line, "puuid": puuid},
            "peak": {
                "season": {"id": peak_season_id or "", "short": season_short(peak_season_id or "")},
                "ranking_schema": get_ranking_schema(peak_season_id or ""),
                "tier": {"id": peak_tier, "name": get_tier_name(peak_tier, season_short(peak_season_id or ""))},
                "rr": peak_rr
            },
            "current": {
                "tier": {"id": current_tier, "name": get_tier_name(current_tier, season_short(current_season_id or ""))},
                "rr": current_rr,
                "last_change": last_change,
                "elo": current_elo,
                "games_needed_for_rating": queue.get("CurrentSeasonGamesNeededForRating", 0),
                "rank_protection_shields": current_data.get("RankProtectionFirstPlateau", 0),
                "leaderboard_placement": {
                    "rank": current_data.get("LeaderboardRank", 0) if current_data else 0,
                    "updated_at": to_iso(latest_competitive_update.get("MatchStartTime", 0))
                } if current_data.get("LeaderboardRank", 0) > 0 else None
            },
            "seasonal": seasonal_list
        }
    }
    return output


def get_player_mmr_data(game_name: str, tag_line: str, region: str = "", platform: str = "pc") -> dict:
    """
    Fetch player MMR data in Henrik API format.
    
    Args:
        game_name: Player's Riot game name
        tag_line: Player's tag (without #)
        region: Region override (na/eu/ap/kr) or empty string to auto-detect
        platform: Platform (pc/console, currently unused)
    
    Returns:
        Dict with status and data in Henrik format, or error response
    """
    tokens = cookie_reauth()
    if not tokens or not tokens.get("access_token"):
        return {"status": 500, "errors": ["auth_failed"]}

    access_token = tokens["access_token"]
    id_token = tokens.get("id_token", "")

    entitlement = get_entitlement_token(access_token)
    if not entitlement:
        return {"status": 500, "errors": ["entitlement_failed"]}

    detected_region = region or get_player_region(access_token, id_token) or "na"
    shard = region_to_shard(detected_region)

    puuid = get_puuid_by_name(game_name, tag_line, access_token)
    if not puuid:
        return {"status": 404, "errors": ["player_not_found"]}

    mmr = get_player_mmr(puuid, access_token, entitlement, shard)
    if not mmr:
        return {"status": 502, "errors": ["mmr_fetch_failed"]}

    updates = get_competitive_updates(puuid, access_token, entitlement, shard)

    return map_mmr_to_henrik(game_name, tag_line, puuid, mmr, updates)


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
