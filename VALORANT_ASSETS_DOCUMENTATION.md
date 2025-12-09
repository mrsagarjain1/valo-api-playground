# Valorant-API.com Documentation

**Source:** [https://valorant-api.com/](https://valorant-api.com/)  
**Dashboard:** [https://dash.valorant-api.com/](https://dash.valorant-api.com/)

An extensive API containing data of most in-game items, assets and more. This is a **public API** that requires **no authentication**.

> ⚠️ **Note:** This API is separate from the unofficial Riot Valorant API documented in `VALORANT_API_DOCUMENTATION.md`. This API provides static game data (skins, agents, maps, etc.) while the Riot API provides player-specific data (MMR, store, match history).

---

## Table of Contents

- [Base URL](#base-url)
- [Query Parameters](#query-parameters)
- [Response Format](#response-format)
- [Endpoints Overview](#endpoints-overview)
- [Endpoint Details](#endpoint-details)
  - [Agents](#agents)
  - [Buddies](#buddies)
  - [Bundles](#bundles)
  - [Ceremonies](#ceremonies)
  - [Competitive Tiers](#competitive-tiers)
  - [Content Tiers](#content-tiers)
  - [Contracts](#contracts)
  - [Currencies](#currencies)
  - [Events](#events)
  - [Gamemodes](#gamemodes)
  - [Gear](#gear)
  - [Level Borders](#level-borders)
  - [Maps](#maps)
  - [Player Cards](#player-cards)
  - [Player Titles](#player-titles)
  - [Seasons](#seasons)
  - [Sprays](#sprays)
  - [Themes](#themes)
  - [Weapons](#weapons)
  - [Version](#version)
- [Reference Data](#reference-data)

---

## Base URL

```
https://valorant-api.com/v1
```

All endpoints are accessed via GET requests to this base URL.

---

## Query Parameters

All endpoints support the following optional query parameters:

| Parameter | Description | Example |
| :--- | :--- | :--- |
| `language` | Localization language code | `?language=ja-JP` |
| `isPlayableCharacter` | Filter agents (true/false) | `?isPlayableCharacter=true` |

### Supported Languages

| Code | Language |
| :--- | :--- |
| `ar-AE` | Arabic |
| `de-DE` | German |
| `en-US` | English (default) |
| `es-ES` | Spanish (Spain) |
| `es-MX` | Spanish (Mexico) |
| `fr-FR` | French |
| `id-ID` | Indonesian |
| `it-IT` | Italian |
| `ja-JP` | Japanese |
| `ko-KR` | Korean |
| `pl-PL` | Polish |
| `pt-BR` | Portuguese (Brazil) |
| `ru-RU` | Russian |
| `th-TH` | Thai |
| `tr-TR` | Turkish |
| `vi-VN` | Vietnamese |
| `zh-CN` | Chinese (Simplified) |
| `zh-TW` | Chinese (Traditional) |

---

## Response Format

All endpoints return JSON with this structure:

```json
{
    "status": 200,
    "data": [ ... ] // Array for list endpoints, object for single item
}
```

Error responses:

```json
{
    "status": 404,
    "error": "the requested uuid was not found"
}
```

---

## Endpoints Overview

| Endpoint | Description | Count |
| :--- | :--- | :--- |
| `/agents` | All agents and abilities | 28 |
| `/buddies` | All gun buddies | 763 |
| `/bundles` | All store bundles | 252 |
| `/ceremonies` | Victory/defeat ceremonies | 6 |
| `/competitivetiers` | Rank tier data | 5 sets |
| `/contenttiers` | Skin rarity tiers | 5 |
| `/contracts` | Battle passes, agent contracts | 78 |
| `/currencies` | In-game currencies | 4 |
| `/events` | Special events | 15 |
| `/gamemodes` | All game modes | 13 |
| `/gear` | Armor items | 3 |
| `/levelborders` | Account level borders | 25 |
| `/maps` | All maps | 23 |
| `/playercards` | Player card banners | 813 |
| `/playertitles` | Player titles | 348 |
| `/seasons` | Acts and episodes | 53 |
| `/sprays` | All sprays | 807 |
| `/themes` | Skin themes/collections | 379 |
| `/weapons` | All weapons with skins | 19 |
| `/version` | Current game version | 1 |

---

## Endpoint Details

### Agents

**Endpoints:**
- `GET /agents` - List all agents
- `GET /agents/{uuid}` - Get specific agent

**Query Parameters:**
- `isPlayableCharacter=true` - Filter to playable agents only (excludes NPCs)

> ℹ️ **Note:** There are 2 Sovas in the data (one is an NPC). Use `?isPlayableCharacter=true` to avoid duplicates.

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Agent name (e.g., "Jett") |
| `description` | string | Agent lore description |
| `developerName` | string | Internal name |
| `releaseDate` | string | ISO date |
| `characterTags` | array | Tags like "Duelist" |
| `displayIcon` | string | Icon URL |
| `displayIconSmall` | string | Small icon URL |
| `bustPortrait` | string | Bust portrait URL |
| `fullPortrait` | string | Full portrait URL |
| `fullPortraitV2` | string | Updated full portrait URL |
| `killfeedPortrait` | string | Killfeed icon URL |
| `background` | string | Background image URL |
| `backgroundGradientColors` | array | Gradient colors |
| `isPlayableCharacter` | boolean | True for playable agents |
| `isBaseContent` | boolean | True for launch agents |
| `role` | object | Role info (uuid, displayName, displayIcon) |
| `abilities` | array | Array of ability objects |
| `voiceLine` | object | Voice line data |

**Ability Object:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `slot` | string | Ability slot (Ability1, Ability2, Grenade, Ultimate, Passive) |
| `displayName` | string | Ability name |
| `description` | string | Ability description |
| `displayIcon` | string | Ability icon URL |

---

### Buddies

**Endpoints:**
- `GET /buddies` - List all buddies
- `GET /buddies/{uuid}` - Get specific buddy
- `GET /buddies/levels` - List all buddy levels
- `GET /buddies/levels/{uuid}` - Get specific buddy level

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Buddy name |
| `isHiddenIfNotOwned` | boolean | Hidden in collection |
| `themeUuid` | string | Theme UUID |
| `displayIcon` | string | Icon URL |
| `levels` | array | Array of level objects |

---

### Bundles

**Endpoints:**
- `GET /bundles` - List all bundles
- `GET /bundles/{uuid}` - Get specific bundle

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Bundle name |
| `displayNameSubText` | string | Subtitle |
| `description` | string | Bundle description |
| `extraDescription` | string | Additional description |
| `promoDescription` | string | Promotional text |
| `displayIcon` | string | Icon URL |
| `displayIcon2` | string | Secondary icon URL |
| `logoIcon` | string | Logo URL |
| `verticalPromoImage` | string | Vertical promo image URL |

---

### Ceremonies

**Endpoints:**
- `GET /ceremonies` - List all ceremonies
- `GET /ceremonies/{uuid}` - Get specific ceremony

Victory and defeat animations.

---

### Competitive Tiers

**Endpoints:**
- `GET /competitivetiers` - List all tier sets
- `GET /competitivetiers/{uuid}` - Get specific tier set

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Tier set UUID |
| `assetObjectName` | string | Internal name (e.g., "Episode5_CompetitiveTierDataTable") |
| `tiers` | array | Array of tier objects |

**Tier Object:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `tier` | number | Tier number (0-27) |
| `tierName` | string | Rank name (e.g., "DIAMOND 2") |
| `division` | string | Division name |
| `divisionName` | string | Division display name |
| `color` | string | Hex color |
| `backgroundColor` | string | Background hex color |
| `smallIcon` | string | Small rank icon URL |
| `largeIcon` | string | Large rank icon URL |
| `rankTriangleDownIcon` | string | Demotion arrow URL |
| `rankTriangleUpIcon` | string | Promotion arrow URL |

**Tier Numbers Reference:**

| Tier | Rank |
| :--- | :--- |
| 0 | Unranked |
| 3-5 | Iron 1-3 |
| 6-8 | Bronze 1-3 |
| 9-11 | Silver 1-3 |
| 12-14 | Gold 1-3 |
| 15-17 | Platinum 1-3 |
| 18-20 | Diamond 1-3 |
| 21-23 | Ascendant 1-3 |
| 24-26 | Immortal 1-3 |
| 27 | Radiant |

---

### Content Tiers

**Endpoints:**
- `GET /contenttiers` - List all content tiers
- `GET /contenttiers/{uuid}` - Get specific tier

Skin rarity classifications.

**Content Tiers Reference:**

| UUID | Dev Name | Display Name |
| :--- | :--- | :--- |
| `0cebb8be-46d7-c12a-d306-e9907bfc5a25` | Deluxe | Deluxe Edition |
| `e046854e-406c-37f4-6607-19a9ba8426fc` | Exclusive | Exclusive Edition |
| `60bca009-4182-7998-dee7-b8a2558dc369` | Premium | Premium Edition |
| `12683d76-48d7-84a3-4e09-6985794f0445` | Select | Select Edition |
| `411e4a55-4e59-7757-41f0-86a53f101bb5` | Ultra | Ultra Edition |

---

### Contracts

**Endpoints:**
- `GET /contracts` - List all contracts
- `GET /contracts/{uuid}` - Get specific contract

Includes battle passes, agent contracts, and event passes.

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Contract name |
| `displayIcon` | string | Icon URL |
| `content` | object | Contract content (chapters, rewards) |

---

### Currencies

**Endpoints:**
- `GET /currencies` - List all currencies
- `GET /currencies/{uuid}` - Get specific currency

**Currencies Reference:**

| UUID | Name |
| :--- | :--- |
| `85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741` | Valorant Points (VP) |
| `e59aa87c-4cbf-517a-5983-6e81511be9b7` | Radianite Points |
| `85ca954a-41f2-ce94-9b45-8ca3dd39a00d` | Kingdom Credits |
| `f08d4ae3-939c-4576-ab26-09ce1f23bb37` | Free Agents |

---

### Events

**Endpoints:**
- `GET /events` - List all events
- `GET /events/{uuid}` - Get specific event

Special limited-time events (RiotX Arcane, Anniversary, etc.).

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Event name |
| `shortDisplayName` | string | Short name |
| `startTime` | string | ISO date start |
| `endTime` | string | ISO date end |

---

### Gamemodes

**Endpoints:**
- `GET /gamemodes` - List all gamemodes
- `GET /gamemodes/{uuid}` - Get specific gamemode
- `GET /gamemodes/equippables` - List gamemode equippables
- `GET /gamemodes/equippables/{uuid}` - Get specific equippable

**Available Gamemodes:**
- Standard
- Deathmatch
- Spike Rush
- Escalation
- Team Deathmatch
- Replication
- Swiftplay
- Snowball Fight
- Skirmish
- Bot Match
- Basic Training
- The Range
- Onboarding

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Gamemode name |
| `description` | string | Gamemode description |
| `duration` | string | Duration info |
| `economyType` | string | Economy type |
| `allowsMatchTimeouts` | boolean | Allows timeouts |
| `isTeamVoiceAllowed` | boolean | Team voice enabled |
| `isMinimapHidden` | boolean | Minimap hidden |
| `orbCount` | number | Orb count |
| `roundsPerHalf` | number | Rounds per half |
| `displayIcon` | string | Icon URL |

---

### Gear

**Endpoints:**
- `GET /gear` - List all gear
- `GET /gear/{uuid}` - Get specific gear

Armor items available in-game.

**Gear Reference:**

| Name | Cost |
| :--- | :--- |
| Heavy Armor | 1000 |
| Light Armor | 400 |
| Regen Shield | 650 |

---

### Level Borders

**Endpoints:**
- `GET /levelborders` - List all level borders
- `GET /levelborders/{uuid}` - Get specific border

Account level borders that change every 20 levels.

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Border name |
| `startingLevel` | number | Level threshold (1, 20, 40, 60, etc.) |
| `levelNumber` | string | Level number image URL |
| `levelNumberAppearance` | string | Level appearance URL |
| `smallPlayerCardAppearance` | string | Small card URL |

---

### Maps

**Endpoints:**
- `GET /maps` - List all maps
- `GET /maps/{uuid}` - Get specific map

**Available Maps:**
- Ascent, Bind, Breeze, Fracture, Haven, Icebox, Lotus, Pearl, Split, Sunset, Abyss, Corrode
- Team Deathmatch: District, Kasbah, Drift, Glitch, Piazza
- Skirmish: Skirmish A, B, C
- Other: The Range, Basic Training

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Map name |
| `narrativeDescription` | string | Lore description |
| `tacticalDescription` | string | Tactical info |
| `coordinates` | string | Map coordinates |
| `displayIcon` | string | Icon URL |
| `listViewIcon` | string | List view icon URL |
| `listViewIconTall` | string | Tall list icon URL |
| `splash` | string | Splash image URL |
| `stylizedBackgroundImage` | string | Background URL |
| `premierBackgroundImage` | string | Premier background URL |
| `mapUrl` | string | Internal map path |
| `xMultiplier` | number | Minimap X multiplier |
| `yMultiplier` | number | Minimap Y multiplier |
| `xScalarToAdd` | number | Minimap X offset |
| `yScalarToAdd` | number | Minimap Y offset |
| `callouts` | array | Map callout regions |

---

### Player Cards

**Endpoints:**
- `GET /playercards` - List all player cards
- `GET /playercards/{uuid}` - Get specific card

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Card name |
| `isHiddenIfNotOwned` | boolean | Hidden in collection |
| `themeUuid` | string | Theme UUID |
| `displayIcon` | string | Icon URL |
| `smallArt` | string | Small art URL |
| `wideArt` | string | Wide art URL |
| `largeArt` | string | Large art URL |

---

### Player Titles

**Endpoints:**
- `GET /playertitles` - List all titles
- `GET /playertitles/{uuid}` - Get specific title

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Title name |
| `titleText` | string | Title display text |
| `isHiddenIfNotOwned` | boolean | Hidden in collection |

---

### Seasons

**Endpoints:**
- `GET /seasons` - List all seasons
- `GET /seasons/{uuid}` - Get specific season
- `GET /seasons/competitive` - List competitive seasons
- `GET /seasons/competitive/{uuid}` - Get specific competitive season

**Season Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Season name (e.g., "EPISODE 9: ACT III") |
| `title` | string | Title text |
| `type` | string | Type (EAresSeasonType::Act) |
| `startTime` | string | ISO date start |
| `endTime` | string | ISO date end |
| `parentUuid` | string | Parent episode UUID |

**Competitive Season Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `startTime` | string | ISO date start |
| `endTime` | string | ISO date end |
| `seasonUuid` | string | Linked season UUID |
| `competitiveTiersUuid` | string | Tier set UUID |
| `borders` | array | Act rank borders |

---

### Sprays

**Endpoints:**
- `GET /sprays` - List all sprays
- `GET /sprays/{uuid}` - Get specific spray
- `GET /sprays/levels` - List spray levels
- `GET /sprays/levels/{uuid}` - Get specific spray level

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Spray name |
| `category` | string | Spray category |
| `themeUuid` | string | Theme UUID |
| `isNullSpray` | boolean | Is null/empty spray |
| `hideIfNotOwned` | boolean | Hidden in collection |
| `displayIcon` | string | Icon URL |
| `fullIcon` | string | Full icon URL |
| `fullTransparentIcon` | string | Transparent icon URL |
| `animationPng` | string | Animation PNG URL |
| `animationGif` | string | Animation GIF URL |
| `levels` | array | Spray level objects |

---

### Themes

**Endpoints:**
- `GET /themes` - List all themes
- `GET /themes/{uuid}` - Get specific theme

Skin collection themes (e.g., "Prime", "Elderflame", "Reaver").

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Theme name |
| `displayIcon` | string | Icon URL |
| `storeFeaturedImage` | string | Store featured image URL |

---

### Weapons

**Endpoints:**
- `GET /weapons` - List all weapons
- `GET /weapons/{uuid}` - Get specific weapon
- `GET /weapons/skins` - List all skins
- `GET /weapons/skins/{uuid}` - Get specific skin
- `GET /weapons/skinlevels` - List all skin levels
- `GET /weapons/skinlevels/{uuid}` - Get specific skin level
- `GET /weapons/skinchromas` - List all chromas
- `GET /weapons/skinchromas/{uuid}` - Get specific chroma

**Weapon List:**
- Sidearms: Classic, Shorty, Frenzy, Ghost, Sheriff
- SMGs: Stinger, Spectre
- Shotguns: Bucky, Judge
- Rifles: Bulldog, Guardian, Phantom, Vandal
- Snipers: Marshal, Outlaw, Operator
- Machine Guns: Ares, Odin
- Melee: Melee

**Weapon Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Weapon name |
| `category` | string | Weapon category |
| `defaultSkinUuid` | string | Default skin UUID |
| `displayIcon` | string | Icon URL |
| `killStreamIcon` | string | Kill stream icon URL |
| `weaponStats` | object | Weapon statistics |
| `shopData` | object | Shop cost and category |
| `skins` | array | Array of skin objects |

**Weapon Stats Object:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `fireRate` | number | Fire rate |
| `magazineSize` | number | Magazine size |
| `runSpeedMultiplier` | number | Run speed multiplier |
| `equipTimeSeconds` | number | Equip time |
| `reloadTimeSeconds` | number | Reload time |
| `firstBulletAccuracy` | number | First bullet accuracy |
| `shotgunPelletCount` | number | Pellet count (shotguns) |
| `wallPenetration` | string | Wall penetration level |
| `damageRanges` | array | Damage at various ranges |
| `adsStats` | object | ADS statistics |

**Skin Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Skin name |
| `themeUuid` | string | Theme UUID |
| `contentTierUuid` | string | Rarity tier UUID |
| `displayIcon` | string | Icon URL |
| `wallpaper` | string | Wallpaper URL |
| `chromas` | array | Chroma variants |
| `levels` | array | Upgrade levels |

**Skin Level Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Level name |
| `levelItem` | string | Level item type |
| `displayIcon` | string | Icon URL |
| `streamedVideo` | string | Video preview URL |

**Chroma Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `uuid` | string | Unique identifier |
| `displayName` | string | Chroma name |
| `displayIcon` | string | Icon URL |
| `fullRender` | string | Full render URL |
| `swatch` | string | Color swatch URL |
| `streamedVideo` | string | Video preview URL |

---

### Version

**Endpoint:**
- `GET /version` - Get current game version

**Response Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `manifestId` | string | Manifest ID |
| `branch` | string | Version branch (e.g., "release-11.11") |
| `version` | string | Full version (e.g., "11.11.00.4026545") |
| `buildVersion` | string | Build version |
| `engineVersion` | string | Engine version |
| `riotClientVersion` | string | Riot client version |
| `riotClientBuild` | string | Riot client build |
| `buildDate` | string | ISO build date |

**Example Response:**
```json
{
    "status": 200,
    "data": {
        "manifestId": "928714CD6908D6FC",
        "branch": "release-11.11",
        "version": "11.11.00.4026545",
        "buildVersion": "9",
        "engineVersion": "5.3.2.0",
        "riotClientVersion": "release-11.11-shipping-9-4026545",
        "riotClientBuild": "123.0.0.3932.0",
        "buildDate": "2025-11-13T21:16:13Z"
    }
}
```

---

## Reference Data

### Quick UUID Lookups

**Most Common Use Cases:**

```python
# Get skin name from store
skin_uuid = "89baf0f4-4648-69fc-f0af-2fbc69b97b80"
response = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{skin_uuid}")
skin_name = response.json()['data']['displayName']

# Get bundle info
bundle_uuid = "some-bundle-uuid"
response = requests.get(f"https://valorant-api.com/v1/bundles/{bundle_uuid}")
bundle = response.json()['data']

# Get agent by name (search all)
response = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true")
agents = response.json()['data']
jett = next(a for a in agents if a['displayName'] == 'Jett')

# Get current game version (for API requests)
response = requests.get("https://valorant-api.com/v1/version")
client_version = response.json()['data']['riotClientVersion']
```

### Media URLs

All media assets are hosted at:
```
https://media.valorant-api.com/{type}/{uuid}/{asset}.png
```

Example:
```
https://media.valorant-api.com/agents/{uuid}/displayicon.png
https://media.valorant-api.com/weaponskinlevels/{uuid}/displayicon.png
https://media.valorant-api.com/competitivetiers/{uuid}/tiers/{tier}/largeicon.png
```

---

## Usage in This Project

This API is used in our scripts for:

1. **`get_current_item_store.py`**: Resolving skin UUIDs to display names
2. **`get_valo_mmr.py`**: Could be used for rank icons and act names
3. **`valo_api_utils.py`**: Getting current client version

**Example Integration:**
```python
import requests

def get_skin_name(skin_level_uuid):
    """Get skin name from valorant-api.com"""
    url = f"https://valorant-api.com/v1/weapons/skinlevels/{skin_level_uuid}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['displayName']
    return None

def get_client_version():
    """Get current client version for API headers"""
    url = "https://valorant-api.com/v1/version"
    response = requests.get(url)
    return response.json()['data']['riotClientVersion']
```
