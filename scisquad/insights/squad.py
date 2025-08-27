from dataclasses import asdict
from typing import Tuple
from datetime import datetime

import pandas as pd

from scisquad.model.entities import SciSportsTeam


class SquadTransferInsights:
    """Insights generator to analyze typical transfer patterns of a team.

    Extra information
    -----------------
    Within the context of squad management, this is one of the components to help determine the best search strategy
    for new players, as well as to optimize decision strategies. A club's history of inbound and outbound transfers
    typically shows their preference for certain markets, their typical spend, as well as the likelihood to buy or
    sell certain players.

    Parameters
    ----------
    team: SciSportsTeam
        A SciSports team object, including transfer history of the team.

    Methods
    -------
    analyze_inbound() -> dict:
        Analyze the characteristics of inbound transfers, to determine typical transfer patterns like fee spend.
    analyze_outbound() -> dict:
        Analyze the characteristics of outbound transfers, to determine typical transfer patterns like fee earned.
    """

    def __init__(self, team: SciSportsTeam):
        """Inits SquadTransferInsights with a SciSportsTeam object."""
        self._team = team
        self._data = pd.DataFrame([asdict(t) for t in team.transfers])
        self._preprocess()

    def _preprocess(self):
        """Preprocess transfer data for analysis."""
        self._data['is_end_loan'] = self._data['is_end_loan'].fillna(False).astype(bool)
        self._data['is_loan'] = self._data['is_loan'].fillna(False).astype(bool)
        self._data = self._data[~self._data['is_end_loan']].sort_values("transfer_date", ascending=False)
        self._data['fee'] = self._data['fee'].fillna(0).astype("int")
        self._data['market_value'] = self._data['market_value'].fillna(0).astype("int")
        self._data['incoming'] = self._data['to_team_id'] == self._team.team_id
        self._data['contract_date'] = self._data['contract_date'].fillna(self._data['transfer_date'])
        self._data['contract_years_left'] = (pd.to_datetime(self._data['contract_date']) - pd.to_datetime(
            self._data['transfer_date'])).dt.days / 365

    def analyze_inbound(self) -> dict:
        """Analyze the characteristics of inbound transfers, to determine typical transfer patterns like fee spend.

        Returns
        -------
        dict
            A json-like object containing aggregated KPIs related to fees spend on incoming transfers, typical
            contract duration left, and the main scouting markets targeted.
        """
        sample = self._data[self._data['incoming']].copy()
        loans_excluded = sample[~sample['is_loan']].copy()

        return {
            "team_id": self._team.team_id,
            "team_name": self._team.name,
            "total_transfers": sample.shape[0],
            "total_spend": loans_excluded['fee'].sum(),
            "percentage_loans": sample['is_loan'].mean(),
            "percentage_free": len(loans_excluded[loans_excluded['fee'] == 0]) / len(loans_excluded),
            "fee_range": {
                "min": loans_excluded['fee'].min(),
                "mean": loans_excluded['fee'].mean(),
                "max": loans_excluded['fee'].max(),
            },
            "market_value_range": {
                "min": loans_excluded['market_value'].min(),
                "mean": loans_excluded['market_value'].mean(),
                "max": loans_excluded['market_value'].max(),
            },
            "contract_years_left_range": {
                "min": loans_excluded['contract_years_left'].min(),
                "mean": loans_excluded['contract_years_left'].mean(),
                "max": loans_excluded['contract_years_left'].max(),
            },
            "inbound_market_shares": sample['from_league_nation'].value_counts(normalize=True).to_dict(),
        }

    def analyze_outbound(self) -> dict:
        """Analyze the characteristics of outbound transfers, to determine typical transfer patterns like fee earned.

        Returns
        -------
        dict
            A json-like object containing aggregated KPIs related to fees earned on outgoing transfers, typical
            contract duration left, and the main selling markets targeted.
        """
        sample = self._data[~self._data['incoming']].copy()
        loans_excluded = sample[~sample['is_loan']].copy()

        return {
            "team_id": self._team.team_id,
            "team_name": self._team.name,
            "total_transfers": sample.shape[0],
            "total_earned": loans_excluded['fee'].sum(),
            "percentage_loans": sample['is_loan'].mean(),
            "percentage_free": len(loans_excluded[loans_excluded['fee'] == 0]) / len(loans_excluded),
            "fee_range": {
                "min": loans_excluded['fee'].min(),
                "mean": loans_excluded['fee'].mean(),
                "max": loans_excluded['fee'].max(),
            },
            "market_value_range": {
                "min": loans_excluded['market_value'].min(),
                "mean": loans_excluded['market_value'].mean(),
                "max": loans_excluded['market_value'].max(),
            },
            "contract_years_left_range": {
                "min": loans_excluded['contract_years_left'].min(),
                "mean": loans_excluded['contract_years_left'].mean(),
                "max": loans_excluded['contract_years_left'].max(),
            },
            "outbound_market_shares": sample['to_league_nation'].value_counts(normalize=True).to_dict(),
        }


class SquadPerformanceInsights:
    """Insights generator to analyze typical performance characteristics of a team.

    Extra information
    -----------------
    Within the context of squad management, this is one of the components to help assess the quality of the squad
    and the overall performance achieved by the team in terms of results on the field.

    Parameters
    ----------
    team: SciSportsTeam
        A SciSports team object, including transfer history of the team.

    Methods
    -------
    get_team_formations() -> Tuple[str, str]:
        Get the team's primary and secondary formations.
    get_team_performance_insights() -> dict:
        Aggregate the team performance KPIs.
    """
    def __init__(self, team: SciSportsTeam):
        """Inits SquadPerformanceInsights with a SciSportsTeam object."""
        self._team = team
        self._matches = pd.DataFrame(self._team.match_team_attributes)
        self._squad = pd.DataFrame(self._team.squad)
        self._preprocess()

    def _preprocess(self):
        """Preprocessing wrapper."""
        self._preprocess_matches()
        self._preprocess_squad()

    def _preprocess_matches(self):
        """Preprocess match data for analysis."""
        self._matches.loc[self._matches['goals_scored'] > self._matches['goals_conceded'], "points"] = 3
        self._matches.loc[self._matches['goals_scored'] == self._matches['goals_conceded'], "points"] = 1
        self._matches.loc[self._matches['goals_scored'] < self._matches['goals_conceded'], "points"] = 0

    def _preprocess_squad(self):
        """Preprocess squad data for analysis."""
        df_match_team_players = pd.DataFrame(self._team.match_team_players).groupby("player_id").agg(
            total_minutes=("minutes_played", "sum"),
            avg_minutes=("minutes_played", "mean"),
            total_games=("match_id", "count")
        ).reset_index()
        available_minutes = self._matches['match_duration'].sum()
        self._squad = self._squad.merge(df_match_team_players, on="player_id", how="left")
        self._squad['usage'] = round(self._squad['total_minutes'] / available_minutes * 100, 1)
        self._squad.sort_values("usage", ascending=False, inplace=True)

    def get_team_formations(self) -> Tuple[str, str]:
        """Get the team's primary and secondary formations.

        Returns
        -------
        primary_formation: str
            The most used formation by a team.
        secondary_formation: str
            The second most used formation by a team.
        """
        formations = self._matches['formation'].value_counts()
        if len(formations) > 1:
            primary_formation = formations.index[0]
            secondary_formation = formations.index[1]
        else:
            primary_formation = formations.index[0]
            secondary_formation = formations.index[0]

        return primary_formation, secondary_formation

    def get_team_performance_insights(self) -> dict:
        """Aggregate the team performance KPIs."""
        primary_formation, secondary_formation = self.get_team_formations()

        return {
            "team_id": self._team.team_id,
            "team_name": self._team.name,
            "primary_formation": primary_formation,
            "secondary_formation": secondary_formation,
            "goals_scored": self._matches['goals_scored'].sum(),
            "goals_conceded": self._matches['goals_conceded'].sum(),
            "matches_won": len(self._matches[self._matches['points'] == 3]),
            "matches_drawn": len(self._matches[self._matches['points'] == 1]),
            "matches_lost": len(self._matches[self._matches['points'] == 0]),
            "goals_scored_per_game": round(self._matches['goals_scored'].mean(), 1),
            "goals_conceded_per_game": round(self._matches['goals_conceded'].mean(), 1),
            "total_points": self._matches['points'].sum(),
            "points_per_game": round(self._matches['points'].mean(), 1),
            "mean_sciskill": round(self._squad['sciskill'].mean(), 1),
            "mean_potential": round(self._squad['potential'].mean(), 1),
            "mean_sciskill_top_15": round(self._squad.head(15)['sciskill'].mean(), 1),
            "mean_potential_top_15": round(self._squad.head(15)['potential'].mean(), 1),
            "mean_sciskill_dev": round(self._squad['sciskill_dev'].mean(), 1),
        }


class SquadRevenueInsights:
    """Insights generator to analyze typical revenue characteristics of a team.

    Extra information
    -----------------
    Within the context of squad management, this is one of the components to help assess the financial output
    of the squad in terms of transfer revenue generated.

    Parameters
    ----------
    team: SciSportsTeam
        A SciSports team object, including transfer history of the team.

    Methods
    -------
    get_squad_revenue_insights() -> dict:
        Aggregate the team revenue KPIs.
    """
    def __init__(self, team: SciSportsTeam):
        """Inits SquadRevenueInsights with a SciSportsTeam object."""
        self._team = team
        self._squad = pd.DataFrame(self._team.squad)
        self._transfers = pd.DataFrame([asdict(t) for t in team.transfers])
        self._preprocess()

    def _preprocess(self):
        """Preprocessing wrapper."""
        df_transfers = self._preprocess_transfers()
        self._squad = self._squad.merge(df_transfers, on="player_id", how="left")
        self._preprocess_squad()

    def _preprocess_squad(self):
        """Preprocess squad data for analysis."""
        self._squad['academy_player'] = self._squad['academy_player'].fillna(False).astype(bool)
        self._squad.loc[self._squad['on_loan'], 'contract_end'] = self._squad['loan_end']
        self._squad['months_left'] = pd.to_datetime(self._squad['contract_end']).apply(
            lambda x: ((datetime.now().year - x.year) * 12 + datetime.now().month - x.month) if pd.notnull(x) else None
        )
        self._squad['paid_fee'] = self._squad['paid_fee'].fillna(0).astype('int')
        self._squad['etv_current'] = self._squad['etv_current'] // 1000 * 1000
        self._squad['etv_dev'] = self._squad['etv_dev'] // 1000 * 1000
        self._squad.loc[~self._squad['on_loan'], 'etv_revenue'] = self._squad['etv_current'] - self._squad['paid_fee']
        self._squad.loc[
            ~self._squad['on_loan'], 'value_added'] = self._squad['market_value'] - self._squad['starting_market_value']
        self._squad['etv_revenue'] = self._squad['etv_revenue'] // 1000 * 1000
        self._squad['etv_revenue'] = self._squad['etv_revenue'].fillna(0).astype('int')
        self._squad['value_added'] = self._squad['value_added'].fillna(0).astype('int')

    def _preprocess_transfers(self) -> pd.DataFrame:
        """Preprocess transfer data for analysis."""
        if not self._transfers.empty:
            self._transfers['incoming'] = self._transfers['to_team_id'] == self._team.team_id
            self._transfers = self._transfers[self._transfers['incoming']].copy()
            self._transfers['is_end_loan'] = self._transfers['is_end_loan'].fillna(False).astype(bool)
            self._transfers['is_loan'] = self._transfers['is_loan'].fillna(False).astype(bool)
            self._transfers = self._transfers[~self._transfers['is_end_loan']].sort_values("transfer_date", ascending=False)
            self._transfers = self._transfers.drop_duplicates("player_id", keep="first")
            self._transfers['fee'] = self._transfers['fee'].fillna(0).astype("int")
            self._transfers['market_value'] = self._transfers['market_value'].fillna(0).astype("int")

            return self._transfers[[
                "fee",
                "is_internal",
                "market_value",
                "player_id",
            ]].rename(columns={
                "fee": "paid_fee",
                "is_internal": "academy_player",
                "market_value": "starting_market_value",
            })
        else:
            return pd.DataFrame()

    @staticmethod
    def _round_big_numbers(x: int) -> int:
        """Round big numbers to the nearest thousand."""
        return int(x // 1000 * 1000)

    def get_squad_revenue_insights(self) -> dict:
        """Aggregate the team revenue KPIs."""
        return {
            "team_id": self._team.team_id,
            "team_name": self._team.name,
            "mean_age": round(self._squad['age'].mean(), 1),
            "mean_etv": self._round_big_numbers(self._squad['etv_current'].mean()),
            "total_etv": self._round_big_numbers(self._squad['etv_current'].sum()),
            "mean_market_value": self._round_big_numbers(self._squad['market_value'].mean()),
            "total_market_value": self._round_big_numbers(self._squad['market_value'].sum()),
            "mean_etv_dev": self._round_big_numbers(self._squad['etv_dev'].mean()),
            "total_etv_dev": self._round_big_numbers(self._squad['etv_dev'].sum()),
            "mean_etv_revenue": self._round_big_numbers(self._squad['etv_revenue'].mean()),
            "total_etv_revenue": self._round_big_numbers(self._squad['etv_revenue'].sum()),
            "mean_value_added": self._round_big_numbers(self._squad['value_added'].mean()),
            "total_value_added": self._round_big_numbers(self._squad['value_added'].sum()),
            "total_academy_etv": self._round_big_numbers(self._squad[self._squad['academy_player']]['etv_current'].sum()),
            "total_academy_etv_dev": self._round_big_numbers(self._squad[self._squad['academy_player']]['etv_dev'].sum())
        }
