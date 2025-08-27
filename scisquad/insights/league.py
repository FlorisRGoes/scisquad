from typing import List
from typing import Tuple

from tqdm import tqdm
import pandas as pd

from scisquad.model.entities import SciSportsSeason
from scisquad.model.entities import SciSportsTeam
from scisquad.api.entities import TeamsAPI
from scisquad.insights.squad import SquadTransferInsights
from scisquad.insights.squad import SquadPerformanceInsights
from scisquad.insights.squad import SquadRevenueInsights


class SeasonTeamInsights:
    """Insights generator to analyze performance and transfer patterns for all teams in a given season.

    Extra information
    -----------------
    This insights generator is your starting point for benchmarking a team against other teams in a given season.

    Parameters
    ----------
    season: SciSportsSeason
        Processed season with all fixtures and other attributes.

    Attributes
    ----------
    teams: List[SciSportsTeam]
        Overview of all teams in a season, with their attributes and players.

    Methods
    -------
    analyze_teams(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        Analyze insights for all teams in a season.
    """
    def __init__(self, season: SciSportsSeason, teams_api: TeamsAPI):
        """Inits SeasonTeamInsights with a SciSportsSeason object and an API interface for team data."""
        self._season = season
        self._api = teams_api
        self.teams = self._set_teams()

    def _get_teams_in_season(self) -> List[int]:
        """Get a list of all teams in a season."""
        teams = []
        for fixture in self._season.fixtures:
            if fixture.home_team_id not in teams:
                teams.append(fixture.home_team_id)
            if fixture.away_team_id not in teams:
                teams.append(fixture.away_team_id)

        return teams

    def _set_teams(self) -> List[SciSportsTeam]:
        """Set a list of all teams in a season, with their attributes needed for insights."""
        season_teams = []
        for team_id in tqdm(
                self._get_teams_in_season(),
                f"Processing all teams in {self._season.league_name} ({self._season.season_name})"
        ):
            team = self._api.get_team(team_id)
            season_teams.append(team)

        return season_teams

    def analyze_teams(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Analyze insights for all teams in a season.

        Returns
        -------
        df_performance_insights: pd.DataFrame
            Aggregated performance insights for all teams.
        df_inbound_transfer_insights: pd.DataFrame
            Aggregated transfer insights for all teams.
        df_outbound_transfer_insights: pd.DataFrame
            Aggregated transfer insights for all teams.
        df_revenue_insights: pd.DataFrame
            Aggregated revenue insights for all teams.
        """
        performance_insights = []
        inbound_transfer_insights = []
        outbound_transfer_insights = []
        revenue_insights = []

        for team in tqdm(
                self.teams,
                f"Analyzing all teams in {self._season.league_name} ({self._season.season_name})"
        ):
            performance_insights.append(SquadPerformanceInsights(team).get_team_performance_insights())
            inbound_transfer_insights.append(SquadTransferInsights(team).analyze_inbound())
            outbound_transfer_insights.append(SquadTransferInsights(team).analyze_outbound())
            revenue_insights.append(SquadRevenueInsights(team).get_squad_revenue_insights())

        return pd.DataFrame(performance_insights), pd.DataFrame(inbound_transfer_insights), pd.DataFrame(outbound_transfer_insights), pd.DataFrame(revenue_insights)
