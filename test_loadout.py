from get_player_loadout import get_player_loadout_data, display_loadout

# Get your own loadout (no args)
result = get_player_loadout_data()

# Or with verification parameters
result = get_player_loadout_data(
    player_name="VenatorGamerALT",
    player_tag="fear",
    player_region="ap",
    platform="pc"
)

if result["success"]:
    data = result["data"]
    # data["player"], data["loadout"], data["raw"]
    display_loadout(result)
else:
    print(f"Error: {result['error']}")
    print(f"Code: {result['error_code']}")