"""
Instalock Agent Script for Valorant
====================================
Instantly locks in a specified agent during agent selection.

WARNING: Using this for instalocking may violate Riot's Terms of Service.
Use responsibly and at your own risk.

Usage:
    python instalock_agent.py --agent <agent_name> --player_name <name> --player_tag <tag> --player_region <region> --platform <platform>

Example:
    python instalock_agent.py --agent Jett --player_name MyName --player_tag 1234 --player_region na --platform PC
"""

import argparse
import time
import requests
from typing import Optional

from valo_api_utils import (
    cookie_reauth,
    get_entitlement_token,
    get_client_version,
    region_to_shard,
    CLIENT_PLATFORM,
)
from valorant_assets import get_agent_by_name


def get_puuid_from_player_info(access_token: str) -> Optional[str]:
    """Get PUUID from the authenticated user's info."""
    url = "https://auth.riotgames.com/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None
    return res.json().get("sub")


def get_pregame_match_id(
    puuid: str,
    access_token: str,
    entitlement_token: str,
    region: str,
    shard: str
) -> Optional[str]:
    """
    Get the pre-game match ID for the player.
    
    Endpoint: GET https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/players/{puuid}
    
    Returns:
        Pre-game match ID or None if not in agent select
    """
    client_version = get_client_version()
    url = f"https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/players/{puuid}"
    
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None
    
    return res.json().get("MatchID")


def select_agent(
    pregame_match_id: str,
    agent_id: str,
    access_token: str,
    entitlement_token: str,
    region: str,
    shard: str
) -> bool:
    """
    Select an agent in agent selection.
    
    Endpoint: POST https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{pre-game match id}/select/{agent id}
    
    Returns:
        True if successful, False otherwise
    """
    client_version = get_client_version()
    url = f"https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{pregame_match_id}/select/{agent_id}"
    
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    
    res = requests.post(url, headers=headers)
    return res.status_code == 200


def lock_agent(
    pregame_match_id: str,
    agent_id: str,
    access_token: str,
    entitlement_token: str,
    region: str,
    shard: str
) -> bool:
    """
    Lock in an agent in agent selection.
    
    Endpoint: POST https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{pre-game match id}/lock/{agent id}
    
    Returns:
        True if successful, False otherwise
    """
    client_version = get_client_version()
    url = f"https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{pregame_match_id}/lock/{agent_id}"
    
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    
    res = requests.post(url, headers=headers)
    return res.status_code == 200


def instalock(
    agent_name: str,
    player_name: str,
    player_tag: str,
    player_region: str,
    platform: str,
    cookies_file: str = "cookies.json",
    poll_interval: float = 0.5,
    max_wait: int = 300
) -> bool:
    """
    Main instalock function that waits for agent selection and locks the agent.
    
    Args:
        agent_name: Name of the agent to lock (e.g., "Jett", "Reyna")
        player_name: Player's Riot game name
        player_tag: Player's tag (without #)
        player_region: Player's region (na, eu, ap, kr, latam, br)
        platform: Platform (PC)
        cookies_file: Path to cookies.json file
        poll_interval: How often to check for pre-game lobby (seconds)
        max_wait: Maximum time to wait for agent selection (seconds)
    
    Returns:
        True if agent was locked successfully, False otherwise
    """
    print(f"\n=== Valorant Instalock Agent ===")
    print(f"Agent: {agent_name}")
    print(f"Player: {player_name}#{player_tag}")
    print(f"Region: {player_region}")
    print(f"Platform: {platform}")
    
    # Get agent UUID from name
    print(f"\n[1] Looking up agent '{agent_name}'...")
    agent = get_agent_by_name(agent_name)
    if not agent:
        print(f"Error: Agent '{agent_name}' not found!")
        return False
    
    agent_id: str = agent.get("uuid", "")
    if not agent_id:
        print(f"Error: Could not get UUID for agent '{agent_name}'!")
        return False
    print(f"    Found: {agent.get('displayName')} (UUID: {agent_id})")
    
    # Authenticate using cookies
    print(f"\n[2] Authenticating...")
    tokens = cookie_reauth(cookies_file)
    if not tokens:
        print("Error: Failed to authenticate. Check your cookies.json file.")
        return False
    
    access_token = tokens["access_token"]
    
    # Get entitlement token
    entitlement_token = get_entitlement_token(access_token)
    if not entitlement_token:
        print("Error: Failed to get entitlement token.")
        return False
    
    print("    Authentication successful!")
    
    # Get PUUID
    print(f"\n[3] Getting player info...")
    puuid = get_puuid_from_player_info(access_token)
    if not puuid:
        print("Error: Failed to get player PUUID.")
        return False
    
    print(f"    PUUID: {puuid}")
    
    # Calculate shard from region
    shard = region_to_shard(player_region)
    print(f"    Region: {player_region}, Shard: {shard}")
    
    # Wait for pre-game lobby
    print(f"\n[4] Waiting for agent selection (polling every {poll_interval}s, max {max_wait}s)...")
    print("    Start a game and enter agent selection to continue...")
    
    start_time = time.time()
    pregame_match_id = None
    
    while time.time() - start_time < max_wait:
        pregame_match_id = get_pregame_match_id(
            puuid, access_token, entitlement_token, player_region, shard
        )
        
        if pregame_match_id:
            print(f"\n    Pre-game lobby found! Match ID: {pregame_match_id}")
            break
        
        time.sleep(poll_interval)
    
    if not pregame_match_id:
        print(f"\nError: Timed out waiting for agent selection after {max_wait}s.")
        return False
    
    # Select and lock agent
    print(f"\n[5] Selecting agent {agent_name}...")
    select_success = select_agent(
        pregame_match_id, agent_id, access_token, entitlement_token, player_region, shard
    )
    
    if select_success:
        print(f"    Agent selected!")
    else:
        print(f"    Warning: Select may have failed, attempting lock anyway...")
    
    print(f"\n[6] Locking agent {agent_name}...")
    lock_success = lock_agent(
        pregame_match_id, agent_id, access_token, entitlement_token, player_region, shard
    )
    
    if lock_success:
        print(f"\n=== SUCCESS: {agent_name} LOCKED! ===")
        return True
    else:
        print(f"\nError: Failed to lock {agent_name}. Agent may already be taken or not owned.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Instalock a Valorant agent during agent selection.",
        epilog="WARNING: Using this may violate Riot's Terms of Service. Use responsibly."
    )
    
    parser.add_argument(
        "--agent", "-a",
        required=True,
        help="Agent name to instalock (e.g., Jett, Reyna, Chamber)"
    )
    parser.add_argument(
        "--player_name", "-n",
        required=True,
        help="Your Riot game name"
    )
    parser.add_argument(
        "--player_tag", "-t",
        required=True,
        help="Your Riot tag (without #)"
    )
    parser.add_argument(
        "--player_region", "-r",
        required=True,
        choices=["na", "eu", "ap", "kr", "latam", "br"],
        help="Your region (na, eu, ap, kr, latam, br)"
    )
    parser.add_argument(
        "--platform", "-p",
        default="PC",
        help="Platform (default: PC)"
    )
    parser.add_argument(
        "--cookies", "-c",
        default="cookies.json",
        help="Path to cookies.json file (default: cookies.json)"
    )
    parser.add_argument(
        "--poll_interval",
        type=float,
        default=0.5,
        help="Polling interval in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--max_wait",
        type=int,
        default=300,
        help="Maximum wait time for agent selection in seconds (default: 300)"
    )
    
    args = parser.parse_args()
    
    success = instalock(
        agent_name=args.agent,
        player_name=args.player_name,
        player_tag=args.player_tag,
        player_region=args.player_region,
        platform=args.platform,
        cookies_file=args.cookies,
        poll_interval=args.poll_interval,
        max_wait=args.max_wait
    )
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
