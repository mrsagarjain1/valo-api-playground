from valo_mmr import get_player_mmr_data

import json

result = get_player_mmr_data("Abu", "Fatum", "ap", "pc")


test = json.dumps(result, indent=4)

with open("my_valo.txt", "w") as f:
    f.write(test)

# print(json.dumps(player_data, indent=4))