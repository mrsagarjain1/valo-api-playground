# VALORANT API Authentication Flow

This document explains how authentication tokens are generated from cookies for the VALORANT API.

## Overview

The authentication uses **cookie-based re-authentication** to obtain fresh API tokens without requiring username/password each time.

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  cookies.json   │────►│ Riot Auth Server     │────►│  access_token   │────►│ entitlement_token│
│  (ssid, etc.)   │     │ auth.riotgames.com   │     │  id_token       │     │                  │
└─────────────────┘     └──────────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Step 1: Cookies (cookies.json)

When you log into VALORANT or the Riot website, your browser stores session cookies. These cookies are saved in `cookies.json`:

| Cookie | Purpose |
|--------|---------|
| `ssid` | **Session ID** - The most important cookie. Contains your encrypted login session (JWT with login token, series token) |
| `sub` | Your **PUUID** (Player UUID) - Unique player identifier |
| `tdid` | **Tracking/Device ID** - Identifies your device |
| `csid` | **Client Session ID** - Current session identifier |
| `clid` | **Client ID** - Client identifier |

### How to Get Cookies

1. Open browser DevTools (F12) → Application → Cookies
2. Go to `https://auth.riotgames.com`
3. Copy the cookie values into `cookies.json`

---

## Step 2: Re-authentication (Getting Access Token)

The `cookie_reauth()` function in `valo_api_utils.py` performs this step.

### Process

1. **Load cookies** into a requests session
2. **Send GET request** to OAuth authorize endpoint:
   ```
   https://auth.riotgames.com/authorize?
     redirect_uri=https://playvalorant.com/opt_in&
     client_id=play-valorant-web-prod&
     response_type=token id_token&
     nonce=1&
     scope=account openid
   ```
3. **Riot validates the `ssid` cookie** - checks if your session is still valid
4. **Two possible outcomes:**
   - ✅ **Success**: Riot redirects to `playvalorant.com/opt_in#access_token=xxx&id_token=yyy`
   - ❌ **Failure**: Riot redirects to `authenticate.riotgames.com` (login page)

### Tokens Returned

| Token | Description | Lifetime |
|-------|-------------|----------|
| `access_token` | JWT for API authorization | ~1 hour |
| `id_token` | Contains player identity info | ~1 hour |
| `expires_in` | Token validity in seconds | Usually 3600 |
| `token_type` | Always "Bearer" | - |

---

## Step 3: Entitlement Token

After obtaining the `access_token`, you need an **entitlement token** for most API calls.

### Process

```python
POST https://entitlements.auth.riotgames.com/api/token/v1
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json
Body: {}
```

### Response

```json
{
  "entitlements_token": "eyJraWQiOi..."
}
```

---

## Step 4: Making API Calls

With all tokens, you can now make authenticated API calls:

### Required Headers

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "X-Riot-Entitlements-JWT": entitlement_token,
    "X-Riot-ClientVersion": client_version,
    "X-Riot-ClientPlatform": client_platform  # Base64 encoded
}
```

### API Endpoints

- **Player Data**: `https://pd.{shard}.a.pvp.net/`
- **Shared Data**: `https://shared.{shard}.a.pvp.net/`
- **GLZ (Game Logic Zone)**: `https://glz-{region}-1.{shard}.a.pvp.net/`

Where:
- `shard` = `na`, `eu`, `ap`, `kr`
- `region` = `na`, `eu`, `ap`, `kr`, `latam`, `br`

---

## Complete Token Chain Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AUTHENTICATION FLOW                          │
└─────────────────────────────────────────────────────────────────────┘

cookies.json
    │
    │ Contains: ssid, sub, tdid, csid, clid
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GET https://auth.riotgames.com/authorize?...                       │
│  Cookies: ssid, tdid, csid, clid                                    │
└─────────────────────────────────────────────────────────────────────┘
    │
    │ Redirect with tokens in URL fragment
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  access_token (JWT, 1 hour validity)                                │
│  id_token (player identity)                                         │
└─────────────────────────────────────────────────────────────────────┘
    │
    │ POST to entitlements endpoint
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  entitlement_token (JWT)                                            │
└─────────────────────────────────────────────────────────────────────┘
    │
    │ Use both tokens in headers
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  VALORANT API CALLS                                                 │
│  Headers:                                                           │
│    - Authorization: Bearer {access_token}                           │
│    - X-Riot-Entitlements-JWT: {entitlement_token}                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Token Expiration & Refresh

| Token Type | Lifetime | What Happens When Expired |
|------------|----------|---------------------------|
| `access_token` | ~1 hour | Call `cookie_reauth()` again |
| `entitlement_token` | ~1 hour | Get new one with fresh access_token |
| Cookies (`ssid`) | Weeks/Months | Must log in manually again |

### Detecting Expired Cookies

When cookies expire, the re-auth redirect goes to `authenticate.riotgames.com` instead of returning tokens. The code detects this:

```python
if "authenticate.riotgames.com" in location:
    print("Cookies expired. Need new cookies.")
    return None
```

---

## Security Notes

⚠️ **Keep your cookies.json private!** Anyone with your cookies can access your account.

- Never commit `cookies.json` to version control
- Add it to `.gitignore`
- Cookies are essentially equivalent to your login credentials

---

## Related Files

- `valo_api_utils.py` - Contains authentication functions
- `cookies.json` - Your session cookies (DO NOT SHARE)
- Other scripts use `get_auth_headers()` or `cookie_reauth()` for authentication
