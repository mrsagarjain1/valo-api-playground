import json
import requests
from urllib.parse import urlparse, parse_qsl

REAUTH_URL = (
    "https://auth.riotgames.com/authorize?"
    "redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&"
    "client_id=play-valorant-web-prod&"
    "response_type=token%20id_token&"
    "nonce=1&"
    "scope=account%20openid"
)

def load_cookies(session):
    with open("cookies.json", "r") as f:
        cookies = json.load(f)
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain="auth.riotgames.com")

def cookie_reauth():
    session = requests.Session()
    load_cookies(session)

    res = session.get(REAUTH_URL, allow_redirects=False)
    location = res.headers.get("Location", "")

    # Failure → redirect to login page
    if "authenticate.riotgames.com" in location:
        print("❌ Cookies expired. Need new cookies.")
        return None

    # Success → extract tokens from redirect fragment
    fragment = urlparse(location).fragment
    params = dict(parse_qsl(fragment))

    tokens = {
        "access_token": str(params.get("access_token", "")),
        "id_token": str(params.get("id_token", "")),
        "expires_in": str(params.get("expires_in", "")),
        "token_type": str(params.get("token_type", ""))
    }

    print("\n🎉 Fresh tokens obtained")
    return tokens


if __name__ == "__main__":
    cookie_reauth()
