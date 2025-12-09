"""
Get the current Valorant store (daily shop, bundles, night market) and item prices.

Endpoints used:
- POST Storefront v3: https://pd.{shard}.a.pvp.net/store/v3/storefront/{puuid}
  (Note: v2 GET and /offers/ endpoint are deprecated)
"""

import json
import requests
from datetime import timedelta
from typing import Optional

from valo_api_utils import (
    CLIENT_PLATFORM,
    CURRENCY_IDS,
    ITEM_TYPE_IDS,
    get_entitlement_token,
    get_client_version,
    get_player_region,
    region_to_shard,
    get_player_info,
    format_currency,
    cookie_reauth,
)


def get_storefront(puuid: str, access_token: str, entitlement_token: str, shard: str) -> Optional[dict]:
    """
    Get the player's current store (daily shop, bundles, night market).
    
    Returns the raw storefront response including:
    - FeaturedBundle: Current featured bundle(s)
    - SkinsPanelLayout: Daily rotating shop (4 skins)
    - AccessoryStore: Accessories shop
    - BonusStore: Night market (if available)
    
    Note: This only works for the authenticated account's store.
    You cannot view other players' stores.
    
    Returns None if the store is unavailable (404 error).
    This can happen if:
    - The account has never opened the store in-game
    - The API is temporarily unavailable
    - Regional restrictions apply
    """
    client_version = get_client_version()
    url = f"https://pd.{shard}.a.pvp.net/store/v3/storefront/{puuid}"
    headers = {
        "X-Riot-ClientPlatform": CLIENT_PLATFORM,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    res = requests.post(url, headers=headers, json={})
    if res.status_code == 404:
        return {"error": "STORE_NOT_AVAILABLE", "message": "Store data unavailable. Please open Valorant and view the Store tab in-game first."}
    if res.status_code != 200:
        print(f"Storefront request failed: {res.status_code}")
        print(f"Response: {res.text[:500] if res.text else 'Empty'}")
        return None
    return res.json()


def get_prices(access_token: str, entitlement_token: str, shard: str) -> Optional[dict]:
    """
    Get all item prices in the store.
    
    NOTE: The /store/v1/offers/ endpoint is deprecated/dead.
    Prices are now included directly in the storefront v3 response.
    This function is kept for backwards compatibility but returns None.
    """
    # The offers endpoint is dead - prices are now in the storefront response
    return {"error": "DEPRECATED", "message": "Prices endpoint is deprecated. Use storefront v3 which includes prices."}


def get_skin_name(skin_uuid: str) -> str:
    """Get skin name from valorant-api.com."""
    try:
        # Try weapon skin level first (most common in store)
        url = f"https://valorant-api.com/v1/weapons/skinlevels/{skin_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", skin_uuid)
        
        # Try weapon skin
        url = f"https://valorant-api.com/v1/weapons/skins/{skin_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", skin_uuid)
    except Exception:
        pass
    return skin_uuid


def get_bundle_name(bundle_uuid: str) -> str:
    """Get bundle name from valorant-api.com."""
    try:
        url = f"https://valorant-api.com/v1/bundles/{bundle_uuid}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["data"].get("displayName", bundle_uuid)
    except Exception:
        pass
    return bundle_uuid


def format_time_remaining(seconds: int) -> str:
    """Format seconds into readable time remaining."""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if td.days > 0:
        return f"{td.days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def parse_storefront(storefront: dict, prices_map: Optional[dict] = None) -> dict:
    """
    Parse storefront response into a more readable format.
    
    Args:
        storefront: Raw storefront response
        prices_map: Optional dict mapping offer IDs to prices
    
    Returns:
        Parsed store data with item names and prices
    """
    result = {
        "daily_shop": [],
        "featured_bundle": None,
        "night_market": None,
        "accessory_store": [],
    }
    
    # Parse daily shop (SkinsPanelLayout)
    skins_panel = storefront.get("SkinsPanelLayout", {})
    single_offers = skins_panel.get("SingleItemStoreOffers", [])
    time_remaining = skins_panel.get("SingleItemOffersRemainingDurationInSeconds", 0)
    
    for offer in single_offers:
        rewards = offer.get("Rewards", [])
        cost = offer.get("Cost", {})
        
        for reward in rewards:
            item_id = reward.get("ItemID", "")
            item_type_id = reward.get("ItemTypeID", "")
            
            # Get item name
            item_name = get_skin_name(item_id)
            
            # Get price
            price_str = ""
            for currency_id, amount in cost.items():
                price_str = format_currency(amount, currency_id)
                break
            
            result["daily_shop"].append({
                "name": item_name,
                "uuid": item_id,
                "type": ITEM_TYPE_IDS.get(item_type_id, "Unknown"),
                "price": price_str,
                "offer_id": offer.get("OfferID", ""),
            })
    
    result["daily_shop_time_remaining"] = format_time_remaining(time_remaining)
    
    # Parse featured bundle
    featured = storefront.get("FeaturedBundle", {})
    bundle = featured.get("Bundle", {})
    if bundle:
        bundle_id = bundle.get("DataAssetID", "")
        bundle_name = get_bundle_name(bundle_id)
        
        total_cost = bundle.get("TotalDiscountedCost") or bundle.get("TotalBaseCost") or {}
        price_str = ""
        for currency_id, amount in total_cost.items():
            price_str = format_currency(amount, currency_id)
            break
        
        bundle_items = []
        for item in bundle.get("Items", []):
            item_data = item.get("Item", {})
            item_id = item_data.get("ItemID", "")
            item_type_id = item_data.get("ItemTypeID", "")
            
            # Get individual item price
            item_price = item.get("DiscountedPrice", item.get("BasePrice", 0))
            item_currency = item.get("CurrencyID", "")
            
            bundle_items.append({
                "name": get_skin_name(item_id) if item_type_id == "e7c63390-eda7-46e0-bb7a-a6abdacd2433" else item_id,
                "uuid": item_id,
                "type": ITEM_TYPE_IDS.get(item_type_id, "Unknown"),
                "price": format_currency(item_price, item_currency) if item_currency else str(item_price),
            })
        
        result["featured_bundle"] = {
            "name": bundle_name,
            "uuid": bundle_id,
            "price": price_str,
            "items": bundle_items,
            "time_remaining": format_time_remaining(featured.get("BundleRemainingDurationInSeconds", 0)),
        }
    
    # Parse night market (BonusStore) if available
    bonus_store = storefront.get("BonusStore")
    if bonus_store:
        night_market_offers = []
        for offer in bonus_store.get("BonusStoreOffers", []):
            inner_offer = offer.get("Offer", {})
            rewards = inner_offer.get("Rewards", [])
            discount_costs = offer.get("DiscountCosts", {})
            original_cost = inner_offer.get("Cost", {})
            discount_percent = offer.get("DiscountPercent", 0)
            
            for reward in rewards:
                item_id = reward.get("ItemID", "")
                item_type_id = reward.get("ItemTypeID", "")
                
                # Get prices
                original_price = ""
                discounted_price = ""
                for currency_id, amount in original_cost.items():
                    original_price = format_currency(amount, currency_id)
                    break
                for currency_id, amount in discount_costs.items():
                    discounted_price = format_currency(amount, currency_id)
                    break
                
                night_market_offers.append({
                    "name": get_skin_name(item_id),
                    "uuid": item_id,
                    "type": ITEM_TYPE_IDS.get(item_type_id, "Unknown"),
                    "original_price": original_price,
                    "discounted_price": discounted_price,
                    "discount_percent": discount_percent,
                })
        
        result["night_market"] = {
            "offers": night_market_offers,
            "time_remaining": format_time_remaining(bonus_store.get("BonusStoreRemainingDurationInSeconds", 0)),
        }
    
    # Parse accessory store
    accessory_store = storefront.get("AccessoryStore", {})
    for offer in accessory_store.get("AccessoryStoreOffers", []):
        inner_offer = offer.get("Offer", {})
        rewards = inner_offer.get("Rewards", [])
        cost = inner_offer.get("Cost", {})
        
        for reward in rewards:
            item_id = reward.get("ItemID", "")
            item_type_id = reward.get("ItemTypeID", "")
            
            price_str = ""
            for currency_id, amount in cost.items():
                price_str = format_currency(amount, currency_id)
                break
            
            result["accessory_store"].append({
                "uuid": item_id,
                "type": ITEM_TYPE_IDS.get(item_type_id, "Unknown"),
                "price": price_str,
            })
    
    result["accessory_store_time_remaining"] = format_time_remaining(
        accessory_store.get("AccessoryStoreRemainingDurationInSeconds", 0)
    )
    
    return result


def get_current_store(region: str = "") -> dict:
    """
    Get the current store for the authenticated player.
    
    Args:
        region: Region override (na/eu/ap/kr) or empty for auto-detect
    
    Returns:
        Dict with store data or error response
    """
    tokens = cookie_reauth()
    if not tokens or not tokens.get("access_token"):
        return {
            "status": 500,
            "error": "auth_failed",
            "message": "Failed to authenticate. Please refresh your cookies."
        }
    
    access_token = tokens["access_token"]
    id_token = tokens.get("id_token", "")
    
    entitlement = get_entitlement_token(access_token)
    if not entitlement:
        return {
            "status": 500,
            "error": "entitlement_failed",
            "message": "Failed to get entitlement token."
        }
    
    # Get player info
    player_info = get_player_info(access_token)
    if not player_info:
        return {
            "status": 500,
            "error": "player_info_failed",
            "message": "Failed to get player info."
        }
    
    puuid = player_info.get("sub")
    if not puuid:
        return {
            "status": 500,
            "error": "puuid_not_found",
            "message": "PUUID not found in player info."
        }
    
    detected_region = region or get_player_region(access_token, id_token) or "na"
    shard = region_to_shard(detected_region)
    
    # Get storefront
    storefront = get_storefront(puuid, access_token, entitlement, shard)
    if not storefront:
        return {
            "status": 502,
            "error": "storefront_failed",
            "message": "Failed to fetch storefront. This can happen if: 1) The account has never opened Valorant, 2) The account is banned/restricted, 3) Region mismatch. Note: You can only view YOUR OWN store - not other players' stores."
        }
    
    # Check if storefront returned an error (404 case)
    if storefront.get("error") == "STORE_NOT_AVAILABLE":
        return {
            "status": 404,
            "error": "store_not_available",
            "message": storefront.get("message", "Store data unavailable. The store endpoint returns 404 - this can happen if the account has never opened the in-game store, or there are regional API restrictions. Try opening the store in-game first.")
        }
    
    # Parse and return
    return parse_storefront(storefront)


def get_all_prices(region: str = "") -> dict:
    """
    Get all item prices from the store.
    
    Args:
        region: Region override (na/eu/ap/kr) or empty for auto-detect
    
    Returns:
        Dict with all prices or error response
    """
    tokens = cookie_reauth()
    if not tokens or not tokens.get("access_token"):
        return {
            "status": 500,
            "error": "auth_failed",
            "message": "Failed to authenticate. Please refresh your cookies."
        }
    
    access_token = tokens["access_token"]
    id_token = tokens.get("id_token", "")
    
    entitlement = get_entitlement_token(access_token)
    if not entitlement:
        return {
            "status": 500,
            "error": "entitlement_failed",
            "message": "Failed to get entitlement token."
        }
    
    detected_region = region or get_player_region(access_token, id_token) or "na"
    shard = region_to_shard(detected_region)
    
    # Get prices
    prices = get_prices(access_token, entitlement, shard)
    if not prices:
        return {
            "status": 502,
            "error": "prices_failed",
            "message": "Failed to fetch prices."
        }
    
    # Check if prices returned an error (404 case)
    if prices.get("error") == "PRICES_NOT_AVAILABLE":
        return {
            "status": 404,
            "error": "prices_not_available",
            "message": prices.get("message", "Prices data unavailable. The prices endpoint returns 404 - this may be a temporary API issue or regional restriction.")
        }
    
    # Parse prices into a more usable format
    offers = prices.get("Offers", [])
    parsed_prices = []
    
    for offer in offers:
        cost = offer.get("Cost", {})
        rewards = offer.get("Rewards", [])
        
        price_str = ""
        for currency_id, amount in cost.items():
            price_str = format_currency(amount, currency_id)
            break
        
        for reward in rewards:
            item_id = reward.get("ItemID", "")
            item_type_id = reward.get("ItemTypeID", "")
            
            parsed_prices.append({
                "offer_id": offer.get("OfferID", ""),
                "item_id": item_id,
                "item_type": ITEM_TYPE_IDS.get(item_type_id, "Unknown"),
                "price": price_str,
                "is_direct_purchase": offer.get("IsDirectPurchase", False),
            })
    
    return {
        "total_offers": len(parsed_prices),
        "offers": parsed_prices
    }


def main():
    """Main function to demonstrate store fetching."""
    print("Fetching current store...")
    store = get_current_store()
    
    if "error" in store:
        print(f"Error: {store['message']}")
        return
    
    print("\n" + "=" * 50)
    print("DAILY SHOP")
    print("=" * 50)
    print(f"Time remaining: {store['daily_shop_time_remaining']}")
    for i, item in enumerate(store["daily_shop"], 1):
        print(f"{i}. {item['name']} - {item['price']}")
    
    if store["featured_bundle"]:
        print("\n" + "=" * 50)
        print("FEATURED BUNDLE")
        print("=" * 50)
        bundle = store["featured_bundle"]
        print(f"Bundle: {bundle['name']}")
        print(f"Price: {bundle['price']}")
        print(f"Time remaining: {bundle['time_remaining']}")
        print(f"Items ({len(bundle['items'])}):")
        for item in bundle["items"]:
            print(f"  - {item['name']} ({item['type']}) - {item['price']}")
    
    if store["night_market"]:
        print("\n" + "=" * 50)
        print("NIGHT MARKET")
        print("=" * 50)
        nm = store["night_market"]
        print(f"Time remaining: {nm['time_remaining']}")
        for item in nm["offers"]:
            print(f"  - {item['name']}: {item['original_price']} -> {item['discounted_price']} ({item['discount_percent']}% off)")
    
    # Save full response
    with open("current_store.json", "w") as f:
        json.dump(store, f, indent=2)
    print("\nFull store data saved to current_store.json")


if __name__ == "__main__":
    main()
