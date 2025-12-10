"""
Valorant Match Details API

Fetches detailed match information for a specific match using the Valorant API.
https://valapidocs.techchrism.me/endpoint/match-details
"""

import json
import requests
from typing import Optional
from datetime import datetime

from valo_api_utils import (
    cookie_reauth,
    get_entitlement_token,
    get_client_version,
    get_player_region,
    region_to_shard,
    CLIENT_PLATFORM,
    TIER_MAP,
)


def get_match_details(
    match_id: str,
    access_token: str,
    entitlement_token: str,
    shard: str,
) -> Optional[dict]:
    """
    Fetch detailed match information for a specific match.
    
    Args:
        match_id: The Match ID to fetch details for
        access_token: Valid Riot access token
        entitlement_token: Valid entitlement token
        shard: Server shard (na/eu/ap/kr/pbe)
    
    Returns:
        Match details data dict or None if failed
    """
    client_version = get_client_version()
    url = f"https://pd.{shard}.a.pvp.net/match-details/v1/matches/{match_id}"
    
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Error fetching match details: {res.status_code}")
        print(res.text)
        return None
    return res.json()


def format_match_details(data: dict) -> None:
    """Format and print match details data."""
    if not data:
        print("No match details data available.")
        return
    
    match_info = data.get("matchInfo", {})
    players = data.get("players", [])
    teams = data.get("teams", [])
    round_results = data.get("roundResults", [])
    
    # Match Info
    print(f"\n{'='*70}")
    print(f"MATCH DETAILS")
    print(f"{'='*70}")
    print(f"Match ID: {match_info.get('matchId', 'Unknown')}")
    print(f"Map ID: {match_info.get('mapId', 'Unknown')}")
    print(f"Game Mode: {match_info.get('gameMode', 'Unknown')}")
    print(f"Queue: {match_info.get('queueID', 'Unknown')}")
    print(f"Is Ranked: {match_info.get('isRanked', False)}")
    print(f"Is Completed: {match_info.get('isCompleted', False)}")
    print(f"Completion State: {match_info.get('completionState', 'Unknown')}")
    
    # Game timing
    game_start_ms = match_info.get("gameStartMillis", 0)
    game_length_ms = match_info.get("gameLengthMillis")
    if game_start_ms:
        start_time = datetime.fromtimestamp(game_start_ms / 1000)
        print(f"Game Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if game_length_ms:
        minutes = game_length_ms // 60000
        seconds = (game_length_ms % 60000) // 1000
        print(f"Game Duration: {minutes}m {seconds}s")
    
    print(f"Season ID: {match_info.get('seasonId', 'Unknown')}")
    print(f"Game Version: {match_info.get('gameVersion', 'Unknown')}")
    
    # Teams
    if teams:
        print(f"\n{'='*70}")
        print("TEAMS")
        print(f"{'='*70}")
        for team in teams:
            team_id = team.get("teamId", "Unknown")
            won = "✓ WON" if team.get("won", False) else "✗ LOST"
            rounds_won = team.get("roundsWon", 0)
            rounds_played = team.get("roundsPlayed", 0)
            print(f"  {team_id}: {rounds_won}/{rounds_played} rounds {won}")
    
    # Players
    if players:
        print(f"\n{'='*70}")
        print("PLAYERS")
        print(f"{'='*70}")
        
        # Sort players by team
        blue_team = [p for p in players if p.get("teamId") == "Blue"]
        red_team = [p for p in players if p.get("teamId") == "Red"]
        
        for team_name, team_players in [("Blue Team", blue_team), ("Red Team", red_team)]:
            if team_players:
                print(f"\n  --- {team_name} ---")
                # Sort by score descending
                team_players.sort(key=lambda p: (p.get("stats") or {}).get("score", 0), reverse=True)
                for player in team_players:
                    game_name = player.get("gameName", "Unknown")
                    tag_line = player.get("tagLine", "")
                    stats = player.get("stats") or {}
                    kills = stats.get("kills", 0)
                    deaths = stats.get("deaths", 0)
                    assists = stats.get("assists", 0)
                    score = stats.get("score", 0)
                    comp_tier = player.get("competitiveTier", 0)
                    tier_name = TIER_MAP.get(comp_tier, f"Tier {comp_tier}")
                    account_level = player.get("accountLevel", 0)
                    character_id = player.get("characterId", "Unknown")
                    
                    print(f"    {game_name}#{tag_line}")
                    print(f"      Agent: {character_id[:8]}...")
                    print(f"      K/D/A: {kills}/{deaths}/{assists} | Score: {score}")
                    print(f"      Rank: {tier_name} | Level: {account_level}")
    
    # Round Results Summary
    if round_results:
        print(f"\n{'='*70}")
        print("ROUND RESULTS")
        print(f"{'='*70}")
        for rnd in round_results:
            round_num = rnd.get("roundNum", 0) + 1  # 0-indexed to 1-indexed
            winning_team = rnd.get("winningTeam", "Unknown")
            round_result = rnd.get("roundResult", "Unknown")
            ceremony = rnd.get("roundCeremony", "")
            
            ceremony_str = f" ({ceremony})" if ceremony and ceremony != "CeremonyDefault" else ""
            print(f"  Round {round_num:2d}: {winning_team:4s} - {round_result}{ceremony_str}")


def main():
    """Main entry point for fetching match details."""
    # Step 1: Authenticate using cookies
    print("Authenticating with Riot...")
    tokens = cookie_reauth()
    if not tokens:
        print("Authentication failed. Please update cookies.json")
        return
    
    access_token = tokens["access_token"]
    id_token = tokens["id_token"]
    
    # Step 2: Get entitlement token
    entitlement_token = get_entitlement_token(access_token)
    if not entitlement_token:
        print("Failed to get entitlement token")
        return
    
    # Step 3: Get player region and shard
    region = get_player_region(access_token, id_token)
    if not region:
        print("Failed to get player region")
        return
    
    shard = region_to_shard(region)
    print(f"Region: {region}, Shard: {shard}")
    
    # Step 4: Get match ID from user
    match_id = input("\nEnter Match ID: ").strip()
    if not match_id:
        print("No match ID provided.")
        return
    
    # Step 5: Fetch match details
    print(f"\nFetching match details for: {match_id}...")
    match_data = get_match_details(match_id, access_token, entitlement_token, shard)
    
    if match_data:
        # Format and display
        format_match_details(match_data)
        
        # Save to file
        output_file = "match_details.json"
        with open(output_file, "w") as f:
            json.dump(match_data, f, indent=2)
        print(f"\n{'='*70}")
        print(f"Full match data saved to: {output_file}")
    else:
        print("Failed to fetch match details.")


if __name__ == "__main__":
    main()
