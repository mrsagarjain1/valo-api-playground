"""
Valorant Match History API

Fetches match history for a player using the Valorant API.
https://valapidocs.techchrism.me/endpoint/match-history
"""

import json
import requests
from typing import Optional
from datetime import datetime

from valo_api_utils import (
    cookie_reauth,
    get_entitlement_token,
    get_client_version,
    get_puuid_by_name,
    region_to_shard,
    CLIENT_PLATFORM,
)


def get_match_history(
    puuid: str,
    access_token: str,
    entitlement_token: str,
    shard: str,
    start_index: Optional[int] = None,
    end_index: Optional[int] = None,
    queue: Optional[str] = None,
) -> Optional[dict]:
    """
    Fetch match history for a player.
    
    Args:
        puuid: Player's PUUID
        access_token: Valid Riot access token
        entitlement_token: Valid entitlement token
        shard: Server shard (na/eu/ap/kr)
        start_index: Index of the first match to return (optional, API defaults to 0)
        end_index: Index of the last match to return (optional, API defaults to 20)
        queue: Queue type to filter by (optional, e.g., 'competitive', 'unrated', 'spikerush')
    
    Returns:
        Match history data dict or None if failed
    """
    client_version = get_client_version()
    url = f"https://pd.{shard}.a.pvp.net/match-history/v1/history/{puuid}"
    
    params: dict = {}
    if start_index is not None:
        params["startIndex"] = start_index
    if end_index is not None:
        params["endIndex"] = end_index
    if queue:
        params["queue"] = queue
    
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print(f"Error fetching match history: {res.status_code}")
        print(res.text)
        return None
    return res.json()


def format_match_history(data: dict) -> None:
    """Format and print match history data."""
    if not data:
        print("No match history data available.")
        return
    
    print(f"\n{'='*60}")
    print(f"Match History for Player: {data.get('Subject', 'Unknown')}")
    print(f"{'='*60}")
    print(f"Total Matches: {data.get('Total', 0)}")
    print(f"Showing: {data.get('BeginIndex', 0)} to {data.get('EndIndex', 0)}")
    print(f"{'='*60}\n")
    
    history = data.get("History", [])
    if not history:
        print("No matches found.")
        return
    
    for i, match in enumerate(history, 1):
        match_id = match.get("MatchID", "Unknown")
        game_start_time = match.get("GameStartTime", 0)
        queue_id = match.get("QueueID", "Unknown")
        
        # Convert milliseconds to datetime
        if game_start_time:
            start_time = datetime.fromtimestamp(game_start_time / 1000)
            time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = "Unknown"
        
        print(f"{i}. Match ID: {match_id}")
        print(f"   Queue: {queue_id}")
        print(f"   Start Time: {time_str}")
        print()


def get_player_match_history(
    player_name: str,
    player_tag: str,
    region: str = "ap",
    platform: str = "PC",
    start_index: Optional[int] = None,
    end_index: Optional[int] = None,
    queue: Optional[str] = None,
) -> Optional[dict]:
    """
    Get match history for a player by name and tag.
    
    Args:
        player_name: Player's in-game name
        player_tag: Player's tag (without #)
        region: Player's region (na/eu/ap/kr/latam/br)
        platform: Platform (PC) - not used directly but for clarity
        start_index: Index of the first match to return (optional, API defaults to 0)
        end_index: Index of the last match to return (optional, API defaults to 20)
        queue: Queue type to filter (optional - 'competitive', 'unrated', 'spikerush', etc.)
    
    Returns:
        Match history data or None if failed
    """
    # 1. Authenticate using cookies
    print("Authenticating...")
    tokens = cookie_reauth()
    if not tokens:
        print("Failed to authenticate. Please update cookies.json")
        return None
    
    access_token = tokens["access_token"]
    
    # 2. Get entitlement token
    print("Getting entitlement token...")
    entitlement_token = get_entitlement_token(access_token)
    if not entitlement_token:
        print("Failed to get entitlement token")
        return None
    
    # 3. Get PUUID from player name and tag
    print(f"Looking up player: {player_name}#{player_tag}...")
    puuid = get_puuid_by_name(player_name, player_tag, access_token)
    if not puuid:
        print(f"Player not found: {player_name}#{player_tag}")
        return None
    print(f"Found PUUID: {puuid}")
    
    # 4. Convert region to shard
    shard = region_to_shard(region)
    print(f"Using shard: {shard}")
    
    # 5. Fetch match history
    start_str = start_index if start_index is not None else "default(0)"
    end_str = end_index if end_index is not None else "default(20)"
    print(f"Fetching match history (indices {start_str} to {end_str})...")
    match_data = get_match_history(
        puuid=puuid,
        access_token=access_token,
        entitlement_token=entitlement_token,
        shard=shard,
        start_index=start_index,
        end_index=end_index,
        queue=queue,
    )
    
    return match_data


if __name__ == "__main__":
    # Example usage - modify these values as needed
    PLAYER_NAME = "gevenator"  # Replace with actual player name
    PLAYER_TAG = "fear"              # Replace with actual tag (without #)
    REGION = "ap"                   # Options: na, eu, ap, kr, latam, br
    PLATFORM = "PC"
    START_INDEX = None              # Optional: defaults to 0
    END_INDEX = None                # Optional: defaults to 20
    QUEUE = "competitive"                    
    
    # Fetch and display match history
    match_data = get_player_match_history(
        player_name=PLAYER_NAME,
        player_tag=PLAYER_TAG,
        region=REGION,
        platform=PLATFORM,
        start_index=START_INDEX,
        end_index=END_INDEX,
        queue=QUEUE,
    )
    
    if match_data:
        # Print formatted output
        format_match_history(match_data)
        
        # Save to valo_matches.json file
        with open("valo_matches.json", "w") as f:
            json.dump(match_data, f, indent=2)
        print("\nMatch data saved to valo_matches.json")
