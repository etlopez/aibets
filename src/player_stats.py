import pandas as pd
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import playergamelog, teamgamelog, leaguedashteamstats, commonplayerinfo


class PlayerStats:
    def __init__(self, player_name):
        self.player_name = player_name
        self.player_id = self.get_player_id_by_full_name()
        self.player_team_id = self.get_player_team_id()

    def get_player_id_by_full_name(self):
        player_data = players.find_players_by_full_name(self.player_name)
        if player_data:
            return player_data[0]['id']
        else:
            return None

    @staticmethod
    def get_team_id_by_abbreviation(team_abbreviation):
        team_data = [team for team in teams.get_teams() if team['abbreviation'].lower() == team_abbreviation.lower()]
        if team_data:
            return team_data[0]['id']
        else:
            return None

    def get_player_team_id(self):
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=self.player_id).get_data_frames()[0]
        return player_info['TEAM_ID'].iloc[0]

    def get_data_for_prediction(self, opponent_name="BOS"):
        opp_team_id = self.get_team_id_by_abbreviation(opponent_name)
        gamelog = playergamelog.PlayerGameLog(player_id=self.player_id).get_data_frames()[0]
        team_log = teamgamelog.TeamGameLog(team_id=self.player_team_id).get_data_frames()[0]
        opp_log = teamgamelog.TeamGameLog(team_id=opp_team_id).get_data_frames()[0]
        league_stats = leaguedashteamstats.LeagueDashTeamStats().get_data_frames()[0]
        
        avg_pts_last_3 = gamelog['PTS'].head(3).mean()
        fg_pct_last_3 = gamelog['FG_PCT'].head(3).mean()
        avg_min_last_5 = gamelog['MIN'].head(5).mean()
        avg_plus_minus_last_3 = gamelog['PLUS_MINUS'].head(3).mean()
        team_avg_pts_last_5 = team_log['PTS'].head(5).mean()
        team_win_rate_last_10 = (team_log['WL'].head(10) == "W").sum() / 10.0
        opp_def_rating_last_5 = league_stats[league_stats['TEAM_ID'] == opp_team_id]['PTS_RANK'].values[0]
        opp_avg_pts_against_last_10 = opp_log['PTS'].head(10).mean()
        matchups_this_season = gamelog[gamelog['MATCHUP'].str.contains(opponent_name.split()[-1])].shape[0]
        avg_pts_against_opp_this_season = gamelog[gamelog['MATCHUP'].str.contains(opponent_name.split()[-1])]['PTS'].mean()
        home_or_away = "Home" if gamelog.iloc[0]['MATCHUP'].split()[-2] == 'vs.' else "Away"
        if len(gamelog) >= 2:
            days_of_rest = (pd.to_datetime(gamelog.iloc[1]['GAME_DATE']) - pd.to_datetime(gamelog.iloc[0]['GAME_DATE'])).days
        else:
            days_of_rest = None
        back_to_back = days_of_rest == 1
        data = {
            'Player Average Points (Last 3)': avg_pts_last_3,
            'Player FG% (Last 3)': fg_pct_last_3,
            'Player Avg Minutes (Last 5)': avg_min_last_5,
            'Player Avg Plus/Minus (Last 3)': avg_plus_minus_last_3,
            'Team Average Points (Last 5)': team_avg_pts_last_5,
            'Team Win Rate (Last 10)': team_win_rate_last_10,
            'Opponent Defensive Rating (Last 5)': opp_def_rating_last_5,
            'Opponent Avg Points Against (Last 10)': opp_avg_pts_against_last_10,
            'Matchups with Opponent this Season': matchups_this_season,
            'Average Points Against Opponent this Season': avg_pts_against_opp_this_season,
            'Home or Away': home_or_away,
            'Days of Rest': days_of_rest,
            'Back to Back Game': back_to_back
        }

        return data