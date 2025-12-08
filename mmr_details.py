import requests
import json
from cookies import cookie_reauth
from datetime import datetime

# Static client platform (base64 encoded JSON)
CLIENT_PLATFORM = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"

TIER_MAP = {
    0: "Unranked",
    1: "Iron",
    2: "Bronze",
    3: "Silver",
    4: "Gold",
    5: "Platinum",
    6: "Diamond",
    7: "Ascendant",
    8: "Immortal",
    9: "Radiant"
}


def get_entitlement_token(access_token: str):
    """Get the entitlement token using the access token"""
    url = "https://entitlements.auth.riotgames.com/api/token/v1"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code != 200:
        print(f"❌ Error getting entitlement token: {response.status_code}")
        return None
    
    return response.json().get("entitlements_token")


def get_client_version():
    """Get the latest Valorant client version from third-party API"""
    url = "https://valorant-api.com/v1/version"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["riotClientVersion"]
    except:
        pass
    
    return "release-10.00-shipping-9-2555555"


def get_player_region(access_token: str, id_token: str):
    """Get player's region using Riot Geo endpoint"""
    url = "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.put(url, headers=headers, json={"id_token": id_token})
    
    if response.status_code != 200:
        print(f"❌ Error getting region: {response.status_code}")
        return None
    
    data = response.json()
    return data.get("affinities", {}).get("live")


def region_to_shard(region: str):
    """Convert region to shard"""
    shard_map = {
        "latam": "na",
        "br": "na",
        "na": "na",
        "pbe": "pbe",
        "eu": "eu",
        "ap": "ap",
        "kr": "kr"
    }
    return shard_map.get(region, "na")


def get_puuid_by_name(game_name: str, tag_line: str, access_token: str):
    """Get a player's PUUID from their Riot ID (GameName#TagLine) using Riot Auth API"""
    url = "https://api.account.riotgames.com/aliases/v1/aliases"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "gameName": game_name,
        "tagLine": tag_line
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"❌ Error getting PUUID: {response.status_code}")
        print(f"Riot ID: {game_name}#{tag_line}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    
    if not data or len(data) == 0:
        print(f"❌ Player not found: {game_name}#{tag_line}")
        return None
    
    player = data[0]
    return player.get("puuid")


def get_player_mmr(puuid: str, access_token: str, entitlement_token: str, shard: str):
    """Get player's complete MMR data"""
    client_version = get_client_version()
    
    url = f"https://pd.{shard}.a.pvp.net/mmr/v1/players/{puuid}"
    
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error getting MMR: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    return response.json()


def format_mmr_details(game_name: str, tag_line: str, puuid: str, mmr_data: dict):
    """Format and display MMR details in a structured way"""
    
    print("\n" + "="*70)
    print(f"📊 MMR DETAILS FOR: {game_name}#{tag_line}")
    print("="*70)
    
    print(f"\n👤 Account Information:")
    print(f"   PUUID: {puuid}")
    print(f"   Rig ID: {game_name}#{tag_line}")
    
    # Get competitive queue data
    if "QueueSkills" not in mmr_data:
        print("\n❌ No competitive data found")
        return
    
    queue_skills = mmr_data.get("QueueSkills", {})
    competitive = queue_skills.get("competitive", {})
    
    if not competitive:
        print("\n❌ No competitive queue data found")
        return
    
    # Current rank info
    print(f"\n📈 Current Competitive Status:")
    print(f"   Total Games: {competitive.get('TotalGamesNeededForRating', 'N/A')}")
    print(f"   Leaderboard Games Needed: {competitive.get('TotalGamesNeededForLeaderboard', 'N/A')}")
    
    # Get seasonal info
    seasonal_info = competitive.get("SeasonalInfoBySeasonID", {})
    
    if seasonal_info:
        # Get latest season
        latest_season_id = max(seasonal_info.keys())
        season_data = seasonal_info[latest_season_id]
        
        tier_name = TIER_MAP.get(season_data.get("CompetitiveTier", 0), "Unknown")
        
        print(f"\n🎮 Latest Season Info:")
        print(f"   Season ID: {latest_season_id[:8]}...")
        print(f"   Rank: {tier_name}")
        print(f"   RR (Ranked Rating): {season_data.get('RankedRating', 0)}")
        print(f"   Games Played: {season_data.get('NumberOfGames', 0)}")
        print(f"   Wins: {season_data.get('NumberOfWins', 0)}")
        print(f"   Leaderboard Rank: {season_data.get('LeaderboardRank', 'Not on leaderboard')}")
        
        if season_data.get("NumberOfGames", 0) > 0:
            win_rate = (season_data.get("NumberOfWins", 0) / season_data.get("NumberOfGames", 1)) * 100
            print(f"   Win Rate: {win_rate:.1f}%")
    
    # Latest competitive update
    latest_update = mmr_data.get("LatestCompetitiveUpdate", {})
    
    if latest_update:
        print(f"\n⏱️  Latest Match Update:")
        print(f"   Match ID: {latest_update.get('MatchID', 'N/A')[:16]}...")
        print(f"   Season ID: {latest_update.get('SeasonID', 'N/A')[:8]}...")
        
        tier_before = TIER_MAP.get(latest_update.get("TierBeforeUpdate", 0), "Unknown")
        tier_after = TIER_MAP.get(latest_update.get("TierAfterUpdate", 0), "Unknown")
        
        print(f"   Tier Before: {tier_before}")
        print(f"   Tier After: {tier_after}")
        print(f"   RR Before: {latest_update.get('RankedRatingBeforeUpdate', 0)}")
        print(f"   RR After: {latest_update.get('RankedRatingAfterUpdate', 0)}")
        print(f"   RR Earned: {latest_update.get('RankedRatingEarned', 0)}")
        print(f"   AFK Penalty: {latest_update.get('AFKPenalty', 0)}")
    
    # All seasons summary
    print(f"\n📋 All Seasons Summary:")
    season_count = 1
    for season_id, season_data in sorted(seasonal_info.items(), reverse=True):
        tier_name = TIER_MAP.get(season_data.get("CompetitiveTier", 0), "Unknown")
        print(f"   Season {season_count}: {tier_name} - {season_data.get('NumberOfWins', 0)}W {season_data.get('NumberOfGames', 0) - season_data.get('NumberOfWins', 0)}L ({season_data.get('NumberOfGames', 0)}G)")
        season_count += 1
    
    print("\n" + "="*70 + "\n")


# Main execution
if __name__ == "__main__":
    print("🔐 Authenticating with cookies...")
    tokens = cookie_reauth()
    
    if not tokens or not tokens["access_token"]:
        print("❌ Could not retrieve access token")
        exit(1)
    
    access_token = tokens["access_token"]
    id_token = tokens["id_token"]
    
    print("🎫 Getting entitlement token...")
    entitlement_token = get_entitlement_token(access_token)
    
    if not entitlement_token:
        print("❌ Could not retrieve entitlement token")
        exit(1)
    
    print("🌍 Getting your region...")
    region = get_player_region(access_token, id_token)
    
    if not region:
        print("❌ Could not retrieve region")
        exit(1)
    
    shard = region_to_shard(region)
    print(f"✅ Your Region: {region} (Shard: {shard})")
    
    # Get player input
    print("\n" + "="*70)
    print("Enter the player's Riot ID to fetch their MMR details")
    print("="*70)
    game_name = input("\n🎮 Enter player Game Name: ").strip()
    tag_line = input("🏷️  Enter player Tag (without #): ").strip()
    
    if not game_name or not tag_line:
        print("❌ Both Game Name and Tag are required")
        exit(1)
    
    # Ask for player's region
    print("\n🌍 Player Region Options:")
    print("  na   - North America, LATAM, Brazil")
    print("  eu   - Europe")
    print("  ap   - Asia Pacific")
    print("  kr   - Korea")
    player_region = input("Enter player's region (or press Enter to use your region): ").strip().lower()
    
    if not player_region:
        player_region = region
        print(f"Using your region: {player_region}")
    
    player_shard = region_to_shard(player_region)
    
    # Get PUUID
    print(f"\n🔍 Looking up PUUID for {game_name}#{tag_line}...")
    puuid = get_puuid_by_name(game_name, tag_line, access_token)
    
    if not puuid:
        print("❌ Could not retrieve PUUID")
        exit(1)
    
    print(f"✅ PUUID: {puuid}")
    
    # Get MMR data
    print(f"\n📊 Fetching MMR data for {game_name}#{tag_line}...")
    mmr_data = get_player_mmr(puuid, access_token, entitlement_token, player_shard)
    
    if not mmr_data:
        print("❌ Failed to retrieve MMR data")
        exit(1)
    
    # Display formatted MMR details
    format_mmr_details(game_name, tag_line, puuid, mmr_data)
    
    # Option to save raw JSON
    save_option = input("💾 Save raw MMR data to JSON file? (y/n): ").strip().lower()
    if save_option == 'y':
        filename = f"mmr_data_{game_name}_{tag_line}.json"
        with open(filename, 'w') as f:
            json.dump(mmr_data, f, indent=2)
        print(f"✅ Saved to {filename}")
