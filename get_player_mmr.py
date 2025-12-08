import requests
from cookies import cookie_reauth

# Static client platform (base64 encoded JSON)
CLIENT_PLATFORM = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"

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
    
    # Fallback version if API fails
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


def get_player_mmr(puuid: str, access_token: str, entitlement_token: str, region: str):
    """Get player's MMR and competitive history"""
    shard = region_to_shard(region)
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


def get_puuid_by_name(game_name: str, tag_line: str, access_token: str):
    """Get a player's PUUID from their Riot ID (GameName#TagLine) using Riot Auth API"""
    # Using the Riot account API (works globally, doesn't require shard)
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
    print(f"DEBUG - Account API Response: {data}")
    
    # API returns a list of results
    if not data or len(data) == 0:
        print(f"❌ Player not found: {game_name}#{tag_line}")
        return None
    
    # Get the first result (most relevant match)
    player = data[0]
    return player.get("puuid")


def get_my_puuid(access_token: str):
    """Get the current user's PUUID"""
    url = "https://auth.riotgames.com/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error getting user info: {response.status_code}")
        return None
    
    return response.json().get("sub")


# Example usage
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
    
    print("🌍 Getting player region...")
    region = get_player_region(access_token, id_token)
    
    if not region:
        print("❌ Could not retrieve region")
        exit(1)
    
    print(f"✅ Your Region: {region}")
    
    # Get PUUID by Riot ID (GameName#TagLine)
    # Replace these with the player you want to look up
    game_name = input("\n🎮 Enter player Game Name: ")
    tag_line = input("🏷️  Enter player Tag (without #): ")
    
    # Ask for player's region for MMR lookup
    print("\n🌍 Player Region Options:")
    print("  na   - North America, LATAM, Brazil")
    print("  eu   - Europe")
    print("  ap   - Asia Pacific")
    print("  kr   - Korea")
    player_region = input("Enter player's region (or press Enter to use your region): ").strip().lower()
    
    if not player_region:
        player_region = region
        print(f"Using your region: {player_region}")
    
    print(f"\n🔍 Looking up PUUID for {game_name}#{tag_line}...")
    target_puuid = get_puuid_by_name(game_name, tag_line, access_token)
    
    if not target_puuid:
        print("❌ Could not retrieve PUUID")
        exit(1)
    
    print(f"✅ PUUID: {target_puuid}")
    
    print(f"\n📊 Getting MMR for player: {game_name}#{tag_line}...")
    mmr_data = get_player_mmr(target_puuid, access_token, entitlement_token, player_region)
    
    if mmr_data:
        print("\n✅ MMR Data Retrieved Successfully!")
        print(f"\nFull Response:")
        import json
        print(json.dumps(mmr_data, indent=2))
        
        # Parse and display key information
        if "QueueSkills" in mmr_data:
            print("\n📈 Competitive Stats:")
            competitive = mmr_data["QueueSkills"].get("competitive", {})
            if competitive:
                print(f"  Total Games: {competitive.get('TotalGamesNeededForRating', 'N/A')}")
                print(f"  Games Needed: {competitive.get('TotalGamesNeededForLeaderboard', 'N/A')}")
                
                seasonal = competitive.get("SeasonalInfoBySeasonID", {})
                if seasonal:
                    latest_season = max(seasonal.keys())
                    season_data = seasonal[latest_season]
                    print(f"\n  Latest Season: {latest_season}")
                    print(f"  Rank: {season_data.get('CompetitiveTier', 'Unranked')}")
                    print(f"  RR: {season_data.get('RankedRating', 0)}")
                    print(f"  Games Played: {season_data.get('NumberOfGames', 0)}")
                    print(f"  Wins: {season_data.get('NumberOfWins', 0)}")
    else:
        print("❌ Failed to retrieve MMR data")
