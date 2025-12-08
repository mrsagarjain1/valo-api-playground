# Valorant API Documentation

Complete documentation of all Valorant API endpoints from https://valapidocs.techchrism.me/

**Status:** Unofficial - These endpoints are not officially supported by Riot Games, but documented for educational purposes.

---

## Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [PVP Endpoints](#pvp-endpoints)
3. [Party Endpoints](#party-endpoints)
4. [Store Endpoints](#store-endpoints)
5. [Pre-Game Endpoints](#pre-game-endpoints)
6. [Current Game Endpoints](#current-game-endpoints)
7. [Contract Endpoints](#contract-endpoints)
8. [Local Endpoints](#local-endpoints)
9. [Local Endpoints - Chat](#local-endpoints---chat)
10. [XMPP](#xmpp)

---

## Common Variables & Headers

### Shards

The shard depends on where the Riot account was created:

| Shard | Regions |
|-------|---------|
| na | North America, LATAM, Brazil |
| pbe | PBE (NA) |
| eu | Europe |
| ap | Asia Pacific |
| kr | Korea |

**Obtaining Shard:**
- Locally: Find in `%LocalAppData%\VALORANT\Saved\Logs\ShooterGame.log`
- Remotely: Use [Riot Geo Endpoint](#put-riot-geo) with auth tokens

### Required Headers

All PVP, Party, Store, Pre-Game, and Current Game endpoints require:

```
X-Riot-ClientPlatform: {client platform}
X-Riot-ClientVersion: {client version}
X-Riot-Entitlements-JWT: {entitlement token}
Authorization: Bearer {auth token}
```

### Client Platform

Base-64 encoded JSON (this value works for all requests):
```
ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9
```

Decodes to:
```json
{
    "platformType": "PC",
    "platformOS": "Windows",
    "platformOSVersion": "10.0.19042.1.256.64bit",
    "platformChipset": "Unknown"
}
```

### Client Version

Obtain from:
- ShooterGame log at `%LocalAppData%\VALORANT\Saved\Logs\ShooterGame.log`
- [Sessions Local Endpoint](#get-sessions)
- [Third-party API](https://dash.valorant-api.com/endpoints/version)

---

## Authentication Endpoints

### POST Auth Cookies
**URL:** `https://auth.riotgames.com/api/v1/authorization`

Get access token using username and password.

---

### PUT Auth Request
**URL:** `https://auth.riotgames.com/api/v1/authorization`

Complete multi-factor authentication (if needed).

---

### PUT Multi-Factor Authentication
**URL:** `https://auth.riotgames.com/api/v1/authorization`

Handle MFA challenges during authentication.

---

### GET Cookie Reauth
**URL:** `https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&nonce=1&scope=account%20openid`

**Purpose:** Get fresh access and ID tokens from existing cookies

**Headers Required:**
- Cookie: ssid, sub, tdid, csid, clid (from cookies.json)

**Response:**
- `access_token`: Bearer token for API requests
- `id_token`: ID token for Riot Geo endpoint
- `expires_in`: Token expiration time (seconds)
- `token_type`: "Bearer"

**Usage:** Automatically handles cookie refresh without needing username/password

---

### POST Entitlement
**URL:** `https://entitlements.auth.riotgames.com/api/token/v1`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body:** `{}`

**Response:**
```json
{
    "entitlements_token": "JWT_TOKEN"
}
```

**Purpose:** Get entitlement token for Valorant API requests

---

### GET Player Info
**URL:** `https://auth.riotgames.com/userinfo`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
    "sub": "PUUID",
    "email": "email@example.com",
    ...
}
```

**Purpose:** Get current player's PUUID and basic info

---

### PUT Riot Geo
**URL:** `https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body:**
```json
{
    "id_token": "{id_token}"
}
```

**Response:**
```json
{
    "affinities": {
        "live": "na"
    }
}
```

**Purpose:** Get player's region/shard

---

### GET PAS Token
**URL:** `https://riot-entitlements.my.microsoftonline.com/...`

**Purpose:** Get PAS (Player Authentication Service) token

---

### GET Riot Client Config
**URL:** `https://valorant-client-config.playvalorant.com/client-config/v2`

**Purpose:** Get Valorant client configuration

---

## PVP Endpoints

### GET Fetch Content
**URL:** `https://pd.{shard}.a.pvp.net/content-service/v3/content`

**Purpose:** Fetch game content (agents, weapons, maps, etc.)

---

### GET Account XP
**URL:** `https://pd.{shard}.a.pvp.net/account-xp/v1/players/{puuid}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Purpose:** Get player's account level and XP

---

### GET Player Loadout
**URL:** `https://pd.{shard}.a.pvp.net/loadout/v1/players/{puuid}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Purpose:** Get player's current loadout (skins, sprays, cards, etc.)

---

### PUT Set Player Loadout
**URL:** `https://pd.{shard}.a.pvp.net/loadout/v1/players/{puuid}/loadout`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Purpose:** Update player's loadout

---

### GET Player MMR
**URL:** `https://pd.{shard}.a.pvp.net/mmr/v1/players/{puuid}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Response:**
```typescript
type PlayerMMRResponse = {
    Version: number;
    Subject: string; // Player UUID
    NewPlayerExperienceFinished: boolean;
    QueueSkills: {
        [queueName: string]: {
            TotalGamesNeededForRating: number;
            TotalGamesNeededForLeaderboard: number;
            CurrentSeasonGamesNeededForRating: number;
            SeasonalInfoBySeasonID: {
                [seasonId: string]: {
                    SeasonID: string;
                    NumberOfWins: number;
                    NumberOfWinsWithPlacements: number;
                    NumberOfGames: number;
                    Rank: number;
                    CapstoneWins: number;
                    LeaderboardRank: number;
                    CompetitiveTier: number;
                    RankedRating: number;
                    WinsByTier: { [tier: string]: number } | null;
                    GamesNeededForRating: number;
                    TotalWinsNeededForRank: number;
                };
            };
        };
    };
    LatestCompetitiveUpdate: {
        MatchID: string;
        MapID: string;
        SeasonID: string;
        MatchStartTime: number;
        TierAfterUpdate: number;
        TierBeforeUpdate: number;
        RankedRatingAfterUpdate: number;
        RankedRatingBeforeUpdate: number;
        RankedRatingEarned: number;
        RankedRatingPerformanceBonus: number;
        CompetitiveMovement: "MOVEMENT_UNKNOWN";
        AFKPenalty: number;
    };
    IsLeaderboardAnonymized: boolean;
    IsActRankBadgeHidden: boolean;
};
```

**Purpose:** Get player's MMR, ranking, and competitive history

---

### GET Match History
**URL:** `https://pd.{shard}.a.pvp.net/match-history/v1/history/{puuid}?startIndex={startIndex}&endIndex={endIndex}&queue={queue}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Query Parameters:**
- `startIndex` (optional): Default 0
- `endIndex` (optional): Default 20
- `queue` (optional): Filter by queue

**Response:**
```typescript
type MatchHistoryResponse = {
    Subject: string; // Player UUID
    BeginIndex: number;
    EndIndex: number;
    Total: number;
    History: {
        MatchID: string;
        GameStartTime: number; // Milliseconds since epoch
        QueueID: string;
    }[];
};
```

**Purpose:** Get player's recent match history

---

### GET Match Details
**URL:** `https://pd.{shard}.a.pvp.net/match-details/v1/matches/{matchID}`

**Parameters:**
- `{shard}`: Player's shard
- `{matchID}`: Match ID

**Response:** Comprehensive match data including:
- Match info (map, queue, game mode, duration)
- Players (all players' stats, kills, deaths, assists)
- Round results (each round's outcome)
- Kill details (timestamps, locations, weapons)
- Economy (weapon purchases per round)
- Behavior factors (AFK, FF, etc.)

**Purpose:** Get detailed information about a specific match

---

### GET Competitive Updates
**URL:** `https://pd.{shard}.a.pvp.net/mmr/v1/players/{puuid}/competitiveupdates?startIndex={startIndex}&endIndex={endIndex}&queue={queue}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Query Parameters:**
- `startIndex` (optional)
- `endIndex` (optional)
- `queue` (optional)

**Response:**
```typescript
type CompetitiveUpdatesResponse = {
    Version: number;
    Subject: string; // Player UUID
    Matches: {
        MatchID: string;
        MapID: string;
        SeasonID: string;
        MatchStartTime: number;
        TierAfterUpdate: number;
        TierBeforeUpdate: number;
        RankedRatingAfterUpdate: number;
        RankedRatingBeforeUpdate: number;
        RankedRatingEarned: number;
        RankedRatingPerformanceBonus: number;
        CompetitiveMovement: "MOVEMENT_UNKNOWN";
        AFKPenalty: number;
    }[];
};
```

**Purpose:** Get recent matches and how they affected ranking

---

### GET Leaderboard
**URL:** `https://pd.{shard}.a.pvp.net/mmr/v1/leaderboards/affinity/na/queue/competitive/season/{seasonId}?startIndex={startIndex}&size={size}&query={query}`

**Parameters:**
- `{shard}`: Player's shard
- `{seasonId}`: Season ID

**Query Parameters:**
- `startIndex` (required)
- `size` (required): Number of entries to retrieve
- `query` (optional): Username to search for

**Response:**
```typescript
type LeaderboardResponse = {
    Deployment: string;
    QueueID: string;
    SeasonID: string;
    Players: {
        PlayerCardID: string;
        TitleID: string;
        IsBanned: boolean;
        IsAnonymized: boolean;
        puuid: string;
        gameName: string;
        tagLine: string;
        leaderboardRank: number;
        rankedRating: number;
        numberOfWins: number;
        competitiveTier: number;
    }[];
    totalPlayers: number;
    immortalStartingPage: number;
    immortalStartingIndex: number;
    topTierRRThreshold: number;
    tierDetails: { [tier: string]: {...} };
    startIndex: number;
    query: string;
};
```

**Purpose:** Get competitive leaderboard (top 500 players - Immortal/Radiant)

---

### GET Penalties
**URL:** `https://pd.{shard}.a.pvp.net/restrictions/v2/penalties`

**Purpose:** Get player's behavioral penalties (AFK, FF, etc.)

---

### GET Config
**URL:** `https://pd.{shard}.a.pvp.net/api/v1/config/{regionOrShard}`

**Purpose:** Get game configuration for a region

---

### PUT Name Service
**URL:** `https://pd.{shard}.a.pvp.net/name-service/v2/players`

**Body:**
```json
["PUUID1", "PUUID2", ...]
```

**Response:**
```typescript
type NameServiceResponse = {
    DisplayName: string;
    Subject: string; // Player UUID
    GameName: string;
    TagLine: string;
}[];
```

**Purpose:** Convert PUUIDs to player names (works in reverse - not for name→PUUID)

---

## Party Endpoints

### GET Party
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}`

**Purpose:** Get party information

---

### GET Party Player
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/players/{puuid}`

**Purpose:** Get current player's party info

---

### DELETE Party Remove Player
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/members/{puuid}`

**Purpose:** Remove player from party

---

### POST Party Set Member Ready
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/members/{puuid}/ready`

**Purpose:** Mark player as ready

---

### POST Refresh Competitive Tier
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/members/{puuid}/competitivetier`

**Purpose:** Refresh player's competitive tier

---

### POST Refresh Player Identity
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/members/{puuid}/identity`

**Purpose:** Refresh player's identity/name

---

### POST Refresh Pings
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/members/{puuid}/pings`

**Purpose:** Refresh player's pings (latency)

---

### POST Change Queue
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/queue`

**Purpose:** Change party's queue type

---

### POST Start Custom Game
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/customgamedata`

**Purpose:** Start a custom game

---

### POST Enter Matchmaking Queue
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/matchmaking/join`

**Purpose:** Enter matchmaking queue

---

### POST Leave Matchmaking Queue
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/matchmaking/leave`

**Purpose:** Leave matchmaking queue

---

### POST Set Party Accessibility
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/accessibility`

**Purpose:** Set party privacy (open/closed)

---

### POST Set Custom Game Settings
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/customgamesettings`

**Purpose:** Configure custom game settings

---

### POST Party Invite
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/invites`

**Purpose:** Invite player to party

---

### POST Party Request
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/requests`

**Purpose:** Send party join request

---

### POST Party Decline
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/decline`

**Purpose:** Decline party invitation

---

### GET Custom Game Configs
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/customgame/v1/configs`

**Purpose:** Get available custom game configurations

---

### GET Party Chat Token
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/chat/v4/parties/{partyId}`

**Purpose:** Get party chat connection token

---

### GET Party Voice Token
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/voice/v1/parties/{partyId}`

**Purpose:** Get party voice connection token

---

### DELETE Party Disable Code
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/codes`

**Purpose:** Disable party invite code

---

### POST Party Generate Code
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/{partyId}/codes`

**Purpose:** Generate party invite code

---

### POST Party Join By Code
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/parties/v1/parties/join/{partyCode}`

**Purpose:** Join party using invite code

---

## Store Endpoints

### GET Prices
**URL:** `https://pd.{shard}.a.pvp.net/store-front/v1/prices`

**Purpose:** Get current store prices for items

---

### GET Storefront
**URL:** `https://pd.{shard}.a.pvp.net/store-front/v1/storefront/{puuid}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Purpose:** Get player's current store rotation

---

### GET Wallet
**URL:** `https://pd.{shard}.a.pvp.net/store-front/v1/wallet/{puuid}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Purpose:** Get player's currency balance (VP, Radianite)

---

### GET Owned Items
**URL:** `https://pd.{shard}.a.pvp.net/store-front/v1/owned-items/{puuid}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Purpose:** Get player's owned cosmetics

---

## Pre-Game Endpoints

### GET Pre-Game Player
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/players/{puuid}`

**Purpose:** Get current player's pre-game state

---

### GET Pre-Game Match
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{matchId}`

**Purpose:** Get pre-game match information

---

### GET Pre-Game Loadouts
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{matchId}/loadouts`

**Purpose:** Get all players' loadouts in pre-game

---

### POST Select Character
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{matchId}/select/{characterId}`

**Purpose:** Select agent in pre-game

---

### POST Lock Character
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{matchId}/lock/{characterId}`

**Purpose:** Lock selected agent

---

### POST Pre-Game Quit
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/pregame/v1/matches/{matchId}/quit`

**Purpose:** Quit pre-game

---

## Current Game Endpoints

### GET Current Game Player
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/core-game/v1/players/{puuid}`

**Purpose:** Get current player's in-game state

---

### GET Current Game Match
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/core-game/v1/matches/{matchId}`

**Purpose:** Get current match information

---

### GET Current Game Loadouts
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/core-game/v1/matches/{matchId}/loadouts`

**Purpose:** Get all players' in-game loadouts

---

### POST Current Game Quit
**URL:** `https://glz-{region}-1.{shard}.a.pvp.net/core-game/v1/matches/{matchId}/quit`

**Purpose:** Quit current match

---

## Contract Endpoints

### GET Item Upgrades
**URL:** `https://pd.{shard}.a.pvp.net/contract-definitions/v3/item-upgrades`

**Purpose:** Get item upgrade definitions

---

### GET Contracts
**URL:** `https://pd.{shard}.a.pvp.net/contracts/v1/contracts/{puuid}`

**Parameters:**
- `{shard}`: Player's shard
- `{puuid}`: Player's UUID

**Purpose:** Get player's active contracts (battle pass, agent contracts)

---

### POST Activate Contract
**URL:** `https://pd.{shard}.a.pvp.net/contracts/v1/contracts/{puuid}/activate`

**Purpose:** Activate a new contract

---

## Local Endpoints

**Note:** These endpoints require a running Valorant client on `127.0.0.1` with a lockfile

### GET Local Help
**URL:** `https://127.0.0.1:{port}/help`

**Purpose:** Get help information from local client

---

### GET Sessions
**URL:** `https://127.0.0.1:{port}/entitlements/v1/token`

**Purpose:** Get current session tokens and client version

**Response:**
```json
{
    "accessToken": "TOKEN",
    "entitlementsToken": "TOKEN",
    "clientVersion": "RELEASE-VERSION"
}
```

---

### GET RSO User Info
**URL:** `https://127.0.0.1:{port}/rso-auth/v1/authorization`

**Purpose:** Get RSO (Riot Sign On) user information

---

### GET Client Region
**URL:** `https://127.0.0.1:{port}/rso-auth/v1/authorization`

**Purpose:** Get client region settings

---

### GET Account Alias
**URL:** `https://127.0.0.1:{port}/chat/v1/session`

**Purpose:** Get account alias/player name

---

### GET Entitlements Token
**URL:** `https://127.0.0.1:{port}/entitlements/v1/token`

**Purpose:** Get fresh entitlements token

---

### GET Chat Session
**URL:** `https://127.0.0.1:{port}/chat/v1/session`

**Purpose:** Get chat session information

---

### GET Friends
**URL:** `https://127.0.0.1:{port}/chat/v4/friends`

**Purpose:** Get friends list

---

### POST Send Friend Request
**URL:** `https://127.0.0.1:{port}/chat/v4/friends/add/{gameName}/{tagLine}`

**Purpose:** Send friend request

---

### DELETE Remove Friend Request
**URL:** `https://127.0.0.1:{port}/chat/v4/friends/{puuid}`

**Purpose:** Remove friend

---

### GET Presence
**URL:** `https://127.0.0.1:{port}/chat/v4/presence`

**Purpose:** Get online presence for friends

---

### GET Friend Requests
**URL:** `https://127.0.0.1:{port}/chat/v4/friend-requests`

**Purpose:** Get incoming friend requests

---

### GET Local Swagger Docs
**URL:** `https://127.0.0.1:{port}/api-docs/swagger.json`

**Purpose:** Get local API documentation

---

### WSS Local WebSocket
**URL:** `wss://127.0.0.1:{port}/chat`

**Purpose:** WebSocket connection for real-time chat/events

---

## Local Endpoints - Chat

### GET Party Chat Info
**URL:** `https://127.0.0.1:{port}/chat/v5/participants/parties/{partyId}`

**Purpose:** Get party chat participants

---

### GET Pre-Game Chat Info
**URL:** `https://127.0.0.1:{port}/chat/v5/participants/pregame/{matchId}`

**Purpose:** Get pre-game chat participants

---

### GET Current Game Chat Info
**URL:** `https://127.0.0.1:{port}/chat/v5/participants/coregame/{matchId}`

**Purpose:** Get in-game chat participants

---

### GET All Chat Info
**URL:** `https://127.0.0.1:{port}/chat/v5/conversations`

**Purpose:** Get all active conversations

---

### GET Chat Participants
**URL:** `https://127.0.0.1:{port}/chat/v5/participants/{conversationId}`

**Purpose:** Get chat participants for a conversation

---

### POST Send Chat
**URL:** `https://127.0.0.1:{port}/chat/v5/conversations/{conversationId}/messages`

**Body:**
```json
{
    "message": "Your message here"
}
```

**Purpose:** Send chat message

---

### GET Chat History
**URL:** `https://127.0.0.1:{port}/chat/v5/conversations/{conversationId}/messages`

**Purpose:** Get chat history

---

## XMPP

### TCP XMPP Connection
**URL:** `tcp://chat.a.pvp.net:5222`

**Protocol:** XMPP (Extensible Messaging and Presence Protocol)

**Purpose:** Real-time messaging and presence updates

---

## Resources & Links

- **Official Documentation:** https://valapidocs.techchrism.me/
- **GitHub:** https://github.com/techchrism/valorant-api-docs
- **Discord Community:** https://discord.gg/a9yzrw3KAm
- **Valorant Log Scraper:** https://github.com/techchrism/valorant-log-endpoint-scraper

---

## Important Notes

1. **Unofficial API:** These endpoints are not officially supported by Riot Games. Use them responsibly.
2. **Rate Limiting:** Be respectful with API calls to avoid getting rate limited.
3. **Terms of Service:** Using these endpoints may violate Riot's Terms of Service. Use at your own risk.
4. **Authentication:** All remote endpoints require valid auth tokens from cookie reauth or direct auth.
5. **Regional Endpoints:** PVP endpoints use `pd.{shard}` while party/pre-game/current-game use `glz-{region}-1.{shard}`
6. **Local Port:** The port number for local endpoints is specified in the Valorant lockfile at `%LocalAppData%\Riot Games\Riot Client\Config\lockfile`

---

Last Updated: December 8, 2025
