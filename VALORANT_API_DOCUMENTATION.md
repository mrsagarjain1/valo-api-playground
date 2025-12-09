# Valorant API Documentation (Unofficial)

Source: [https://valapidocs.techchrism.me/](https://valapidocs.techchrism.me/)

This is a site dedicated to documenting the Valorant API endpoints the client uses internally. These endpoints are not officially supported. However, as long as you use common sense and don't do anything a Riot employee would frown at, you won't get banned.

**Discord:** [https://discord.gg/a9yzrw3KAm](https://discord.gg/a9yzrw3KAm)

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication Endpoints](#authentication-endpoints)
- [PVP Endpoints](#pvp-endpoints)
- [Party Endpoints](#party-endpoints)
- [Store Endpoints](#store-endpoints)
- [Pre-Game Endpoints](#pre-game-endpoints)
- [Current Game Endpoints](#current-game-endpoints)
- [Contract Endpoints](#contract-endpoints)
- [Local Endpoints](#local-endpoints)
- [Local Endpoints - Chat](#local-endpoints---chat)
- [XMPP](#xmpp)

---

## Getting Started

One of the easiest ways to get started and get a feel for what kinds of data you can get from the apis is to play around with the requests yourself in a REST client like Insomnia.

1.  Download and install Insomnia here: [https://insomnia.rest/download](https://insomnia.rest/download)
    *   Recent updates to Insomnia require a Kong account. For a fork of Insomnia that does not require an account, see [https://github.com/ArchGPT/insomnium](https://github.com/ArchGPT/insomnium)
2.  [Add insomnia-plugin-valorant](insomnia://plugins/install?name=insomnia-plugin-valorant)
    *   This plugin autocompletes useful API placeholders such as auth info, lockfile data, and player info. For more info, see [https://github.com/techchrism/insomnia-plugin-valorant](https://github.com/techchrism/insomnia-plugin-valorant)
3.  [Import Workspace](insomnia://app/import?uri=https://valapidocs.techchrism.me/insomnia.json)

You can right-click a request in Insomnia and click "Generate Code" to see how to make the request in the language and library of your choice.

## Investigating Endpoints

Endpoints are commonly found from the ShooterGame log located at `%LocalAppData%\VALORANT\Saved\Logs\ShooterGame.log`. You can use [Valorant Log Endpoint Scraper](https://github.com/techchrism/valorant-log-endpoint-scraper) to quickly export a list of endpoints and other urls found in the log.

---

## Authentication Endpoints

| Endpoint | Description |
| :--- | :--- |
| [POST Auth Cookies](https://valapidocs.techchrism.me/endpoint/auth-cookies) | Prepare cookies for auth request |
| [PUT Auth Request](https://valapidocs.techchrism.me/endpoint/auth-request) | Perform the main authorization |
| [PUT Multi-Factor Authentication](https://valapidocs.techchrism.me/endpoint/multi-factor-authentication) | Submit 2FA code |
| [GET Cookie Reauth](https://valapidocs.techchrism.me/endpoint/cookie-reauth) | Re-authenticate using existing cookies |
| [POST Entitlement](https://valapidocs.techchrism.me/endpoint/entitlement) | Get entitlement token |
| [GET Player Info](https://valapidocs.techchrism.me/endpoint/player-info) | Get player info (PUUID, etc.) |
| [PUT Riot Geo](https://valapidocs.techchrism.me/endpoint/riot-geo) | Get region/shard info |
| [GET PAS Token](https://valapidocs.techchrism.me/endpoint/pas-token) | Get PAS token |
| [GET Riot Client Config](https://valapidocs.techchrism.me/endpoint/riot-client-config) | Get client config |

## PVP Endpoints

| Endpoint | Description |
| :--- | :--- |
| [GET Fetch Content](https://valapidocs.techchrism.me/endpoint/fetch-content) | Get content (seasons, acts, events) |
| [GET Account XP](https://valapidocs.techchrism.me/endpoint/account-xp) | Get account XP and level |
| [GET Player Loadout](https://valapidocs.techchrism.me/endpoint/player-loadout) | Get current player loadout |
| [PUT Set Player Loadout](https://valapidocs.techchrism.me/endpoint/set-player-loadout) | Set player loadout |
| [GET Player MMR](https://valapidocs.techchrism.me/endpoint/player-mmr) | Get player MMR details |
| [GET Match History](https://valapidocs.techchrism.me/endpoint/match-history) | Get match history |
| [GET Match Details](https://valapidocs.techchrism.me/endpoint/match-details) | Get details of a specific match |
| [GET Competitive Updates](https://valapidocs.techchrism.me/endpoint/competitive-updates) | Get recent competitive matches and MMR changes |
| [GET Leaderboard](https://valapidocs.techchrism.me/endpoint/leaderboard) | Get ranked leaderboard |
| [GET Penalties](https://valapidocs.techchrism.me/endpoint/penalties) | Get player penalties |
| [GET Config](https://valapidocs.techchrism.me/endpoint/config) | Get config |
| [PUT Name Service](https://valapidocs.techchrism.me/endpoint/name-service) | Update player name/tagline |

## Party Endpoints

| Endpoint | Description |
| :--- | :--- |
| [GET Party](https://valapidocs.techchrism.me/endpoint/party) | Get current party info |
| [GET Party Player](https://valapidocs.techchrism.me/endpoint/party-player) | Get party player info |
| [DELETE Party Remove Player](https://valapidocs.techchrism.me/endpoint/party-remove-player) | Remove player from party |
| [POST Party Set Member Ready](https://valapidocs.techchrism.me/endpoint/party-set-member-ready) | Set ready status |
| [POST Refresh Competitive Tier](https://valapidocs.techchrism.me/endpoint/refresh-competitive-tier) | Refresh competitive tier |
| [POST Refresh Player Identity](https://valapidocs.techchrism.me/endpoint/refresh-player-identity) | Refresh player identity |
| [POST Refresh Pings](https://valapidocs.techchrism.me/endpoint/refresh-pings) | Refresh pings |
| [POST Change Queue](https://valapidocs.techchrism.me/endpoint/change-queue) | Change matchmaking queue |
| [POST Start Custom Game](https://valapidocs.techchrism.me/endpoint/start-custom-game) | Start a custom game |
| [POST Enter Matchmaking Queue](https://valapidocs.techchrism.me/endpoint/enter-matchmaking-queue) | Enter queue |
| [POST Leave Matchmaking Queue](https://valapidocs.techchrism.me/endpoint/leave-matchmaking-queue) | Leave queue |
| [POST Set Party Accessibility](https://valapidocs.techchrism.me/endpoint/set-party-accessibility) | Set party open/closed |
| [POST Set Custom Game Settings](https://valapidocs.techchrism.me/endpoint/set-custom-game-settings) | Set custom game options |
| [POST Party Invite](https://valapidocs.techchrism.me/endpoint/party-invite) | Invite player to party |
| [POST Party Request](https://valapidocs.techchrism.me/endpoint/party-request) | Request to join party |
| [POST Party Decline](https://valapidocs.techchrism.me/endpoint/party-decline) | Decline party request |
| [GET Custom Game Configs](https://valapidocs.techchrism.me/endpoint/custom-game-configs) | Get custom game configs |
| [GET Party Chat Token](https://valapidocs.techchrism.me/endpoint/party-chat-token) | Get party chat token |
| [GET Party Voice Token](https://valapidocs.techchrism.me/endpoint/party-voice-token) | Get party voice token |
| [DELETE Party Disable Code](https://valapidocs.techchrism.me/endpoint/party-disable-code) | Disable party code |
| [POST Party Generate Code](https://valapidocs.techchrism.me/endpoint/party-generate-code) | Generate party code |
| [POST Party Join By Code](https://valapidocs.techchrism.me/endpoint/party-join-by-code) | Join party by code |

## Store Endpoints

| Endpoint | Description |
| :--- | :--- |
| [GET Prices](https://valapidocs.techchrism.me/endpoint/prices) | Get item prices |
| [GET Storefront](https://valapidocs.techchrism.me/endpoint/storefront) | Get player store (daily shop, bundle) |
| [GET Wallet](https://valapidocs.techchrism.me/endpoint/wallet) | Get player wallet (VP, Radianite) |
| [GET Owned Items](https://valapidocs.techchrism.me/endpoint/owned-items) | Get owned items |

## Pre-Game Endpoints

| Endpoint | Description |
| :--- | :--- |
| [GET Pre-Game Player](https://valapidocs.techchrism.me/endpoint/pre-game-player) | Get pre-game player info |
| [GET Pre-Game Match](https://valapidocs.techchrism.me/endpoint/pre-game-match) | Get pre-game match info |
| [GET Pre-Game Loadouts](https://valapidocs.techchrism.me/endpoint/pre-game-loadouts) | Get pre-game loadouts |
| [POST Select Character](https://valapidocs.techchrism.me/endpoint/select-character) | Select agent |
| [POST Lock Character](https://valapidocs.techchrism.me/endpoint/lock-character) | Lock agent |
| [POST Pre-Game Quit](https://valapidocs.techchrism.me/endpoint/pre-game-quit) | Quit pre-game (dodge) |

## Current Game Endpoints

| Endpoint | Description |
| :--- | :--- |
| [GET Current Game Player](https://valapidocs.techchrism.me/endpoint/current-game-player) | Get current game player info |
| [GET Current Game Match](https://valapidocs.techchrism.me/endpoint/current-game-match) | Get current game match info |
| [GET Current Game Loadouts](https://valapidocs.techchrism.me/endpoint/current-game-loadouts) | Get current game loadouts |
| [POST Current Game Quit](https://valapidocs.techchrism.me/endpoint/current-game-quit) | Quit current game |

## Contract Endpoints

| Endpoint | Description |
| :--- | :--- |
| [GET Item Upgrades](https://valapidocs.techchrism.me/endpoint/item-upgrades) | Get item upgrades |
| [GET Contracts](https://valapidocs.techchrism.me/endpoint/contracts) | Get contracts progress |
| [POST Activate Contract](https://valapidocs.techchrism.me/endpoint/activate-contract) | Activate a contract |

## Local Endpoints

| Endpoint | Description |
| :--- | :--- |
| [GET Local Help](https://valapidocs.techchrism.me/endpoint/local-help) | Get local help |
| [GET Sessions](https://valapidocs.techchrism.me/endpoint/sessions) | Get sessions |
| [GET RSO User Info](https://valapidocs.techchrism.me/endpoint/rso-user-info) | Get RSO user info |
| [GET Client Region](https://valapidocs.techchrism.me/endpoint/client-region) | Get client region |
| [GET Account Alias](https://valapidocs.techchrism.me/endpoint/account-alias) | Get account alias |
| [GET Entitlements Token](https://valapidocs.techchrism.me/endpoint/entitlements-token) | Get entitlements token |
| [GET Chat Session](https://valapidocs.techchrism.me/endpoint/chat-session) | Get chat session |
| [GET Friends](https://valapidocs.techchrism.me/endpoint/friends) | Get friends list |
| [POST Send Friend Request](https://valapidocs.techchrism.me/endpoint/send-friend-request) | Send friend request |
| [DELETE Remove Friend Request](https://valapidocs.techchrism.me/endpoint/remove-friend-request) | Remove friend request |
| [GET Presence](https://valapidocs.techchrism.me/endpoint/presence) | Get presence info |
| [GET Friend Requests](https://valapidocs.techchrism.me/endpoint/friend-requests) | Get friend requests |
| [GET Local Swagger Docs](https://valapidocs.techchrism.me/endpoint/local-swagger-docs) | Get local swagger docs |
| [WSS Local WebSocket](https://valapidocs.techchrism.me/endpoint/local-websocket) | Local WebSocket connection |

## Local Endpoints - Chat

| Endpoint | Description |
| :--- | :--- |
| [GET Party Chat Info](https://valapidocs.techchrism.me/endpoint/party-chat-info) | Get party chat info |
| [GET Pre-Game Chat Info](https://valapidocs.techchrism.me/endpoint/pre-game-chat-info) | Get pre-game chat info |
| [GET Current Game Chat Info](https://valapidocs.techchrism.me/endpoint/current-game-chat-info) | Get current game chat info |
| [GET All Chat Info](https://valapidocs.techchrism.me/endpoint/all-chat-info) | Get all chat info |
| [GET Chat Participants](https://valapidocs.techchrism.me/endpoint/chat-participants) | Get chat participants |
| [POST Send Chat](https://valapidocs.techchrism.me/endpoint/send-chat) | Send chat message |
| [GET Chat History](https://valapidocs.techchrism.me/endpoint/chat-history) | Get chat history |

## XMPP

| Endpoint | Description |
| :--- | :--- |
| [TCP XMPP Connection](https://valapidocs.techchrism.me/endpoint/xmpp-connection) | XMPP Connection details |
