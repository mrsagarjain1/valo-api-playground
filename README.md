# Valorant API Playground

A Python-based toolkit for interacting with Valorant's unofficial API. This project provides utilities to access player data, match history, store information, and more using cookie-based authentication.

> ⚠️ **Disclaimer**: This project uses unofficial Valorant API endpoints. These endpoints are not officially supported by Riot Games. Use responsibly and at your own risk.

## Features

- 🔐 **Cookie-based Authentication** - Secure authentication using Riot session cookies
- 🛒 **Store Access** - View your daily shop, bundles, and night market
- 📊 **Match History** - Fetch detailed match history and statistics
- 🎯 **MMR & Rank Data** - Get competitive rank and MMR information
- 🎨 **Player Loadout** - View equipped skins, sprays, and customizations
- 🎮 **Agent Instalock** - Instantly lock in an agent during agent selection
- 🖼️ **Assets API** - Access game assets (agents, weapons, maps, skins) via valorant-api.com

## Prerequisites

- Python 3.7+
- `requests` library

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mrsagarjain1/valo-api-playground.git
   cd valo-api-playground
   ```

2. Install dependencies:
   ```bash
   pip install requests
   ```

3. Set up authentication (see [Authentication](#authentication) section below)

## Authentication

This project uses cookie-based re-authentication. You need to export your Riot session cookies:

1. Open your browser and log into [Riot Games](https://auth.riotgames.com)
2. Open DevTools (F12) → Application → Cookies → `auth.riotgames.com`
3. Copy the cookie values and create a `cookies.json` file:

```json
{
    "ssid": "your_ssid_value",
    "sub": "your_puuid",
    "tdid": "your_tdid_value",
    "csid": "your_csid_value",
    "clid": "your_clid_value"
}
```

> 📝 The `ssid` cookie is the most important - it contains your encrypted login session.

For more details, see [Authentication Flow Documentation](documents/AUTHENTICATION_FLOW.md).

## Usage

### Get Your Daily Store

```python
python get_my_store.py
```

Displays your current daily shop, featured bundles, and night market (if available).

### Get Match History

```python
python get_valo_matches.py
```

Fetches your recent match history with details like map, mode, and scores.

### Get MMR/Rank Data

```python
python get_valo_mmr.py
```

Shows your competitive rank, RR, and MMR information.

### Get Player Loadout

```python
python get_player_loadout.py
```

Displays your currently equipped skins, sprays, player card, and title.

### Instalock Agent

```python
python instalock_agent.py --agent Jett --player_name YourName --player_tag 1234 --player_region na --platform PC
```

> ⚠️ **Warning**: Using instalock may violate Riot's Terms of Service. Use at your own risk.

## Project Structure

```
├── valo_api_utils.py          # Shared utility functions (auth, tokens, regions)
├── valorant_assets.py         # Valorant Assets API wrapper (valorant-api.com)
├── get_my_store.py            # Fetch daily shop and bundles
├── get_valo_matches.py        # Fetch match history
├── get_match_details.py       # Get detailed match information
├── get_valo_mmr.py            # Fetch MMR and rank data
├── get_player_loadout.py      # Fetch equipped items
├── instalock_agent.py         # Agent instalock script
├── owned_items.py             # Fetch owned items
├── cookies.json               # Your Riot session cookies (create this)
└── documents/
    ├── AUTHENTICATION_FLOW.md       # Auth flow documentation
    ├── VALORANT_API_DOCUMENTATION.md # API endpoints reference
    └── VALORANT_ASSETS_DOCUMENTATION.md # Assets API reference
```

## API Reference

This project uses endpoints documented at:
- **Unofficial Valorant API**: [valapidocs.techchrism.me](https://valapidocs.techchrism.me/)
- **Valorant Assets API**: [valorant-api.com](https://valorant-api.com/)

### Key Endpoints Used

| Endpoint | Description |
|----------|-------------|
| `POST /store/v3/storefront/{puuid}` | Get player's store |
| `GET /match-history/v1/history/{puuid}` | Get match history |
| `GET /mmr/v1/players/{puuid}` | Get MMR data |
| `GET /personalization/v2/players/{puuid}/playerloadout` | Get loadout |
| `GET /pregame/v1/players/{puuid}` | Get pre-game info |
| `POST /pregame/v1/matches/{match_id}/lock/{agent_id}` | Lock agent |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Resources

- [Valorant API Docs (Unofficial)](https://valapidocs.techchrism.me/)
- [Valorant Assets API](https://valorant-api.com/)
- [Discord Community](https://discord.gg/a9yzrw3KAm)

## License

This project is for educational purposes only. Use responsibly.

---

**Note**: This project is not affiliated with Riot Games or Valorant. All product names, logos, and brands are property of their respective owners.
