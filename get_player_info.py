import requests
from cookies import cookie_reauth

def get_player_info(access_token: str):
    url = "https://auth.riotgames.com/userinfo"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None

    return response.json()


# Example usage
if __name__ == "__main__":
    tokens = cookie_reauth()
    
    if tokens and tokens["access_token"]:
        info = get_player_info(tokens["access_token"])
        print(info)
    else:
        print("❌ Could not retrieve access token")
