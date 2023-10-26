from player_stats import PlayerStats

player = PlayerStats("Lebron James")
data = player.get_data_for_prediction("BOS")
for key, value in data.items():
    print(f"{key}: {value}")