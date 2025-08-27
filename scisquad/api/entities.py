from typing import Optional
from typing import List
from typing import Tuple
from datetime import timedelta
from datetime import datetime

from scisquad.api.base import RecruitmentAPI
from scisquad.api.domain import ApiCredentials
from scisquad.model.entities import LeagueType
from scisquad.model.entities import Gender
from scisquad.model.entities import AgeGroup
from scisquad.model.entities import SciSportsLeague
from scisquad.model.entities import SciSportsSeason
from scisquad.model.entities import SciSportsMatch
from scisquad.model.entities import SciSportsTeam
from scisquad.model.entities import Nations
from scisquad.model.entities import Transfer
from scisquad.model.entities import SquadPlayer


class PlayersAPI(RecruitmentAPI):
    """API interface for interaction with the SciSports players and related endpoints.

    Extra information
    -----------------
    This class mainly functions as a entry point to get player metrics and attributes from the SciSports API.

    Parameters
    ----------
    credentials: ApiCredentials
        User credentials to pass for API authorization.

    Methods
    -------
    get_player(plr: dict, team_id: int) -> SquadPlayer:
        Process a player object from the SciSports API into a SquadPlayer dataclass object.

    See also
    --------
    https://developers.scisports.app/recruitment-center/api-reference
    """
    def __init__(self, credentials: ApiCredentials):
        """Inits PlayersAPI with API credentials."""
        super().__init__(credentials)

    def _get_sciskill(self, plr_id: int) -> Tuple[float, float, float]:
        """Get the player's sciskill metrics."""
        payload = self.get_request(
            f"v2/metrics/players/sciskill",
            params={
                "PlayerIds": [plr_id]
            }
        )
        if payload.get("total") > 0:
            payload = payload.get("items")[0]
        else:
            payload = {
                "sciskill": 0,
                "potential": 0,
                "sciskillDevelopmentSixMonths": 0
            }

        return payload.get("sciskill"), payload.get("potential"), payload.get("sciskillDevelopmentSixMonths")

    def _get_etv(self, plr_id: int) -> Tuple[int, int]:
        """Get the etv metrics for a player"""
        payload = self.get_request(
            f"v2/metrics/players/transfer-fees",
            params={
                "PlayerIds": [plr_id],
                "DateBiggerThan": (datetime.now() - timedelta(weeks=26)).strftime('%Y-%m-%dT%H:%M:%S'),
                "Limit": 100,
                "OrderBy": "date",
                "SortOrder": "descending"

            }
        ).get("items")
        if len(payload) > 0:
            current_etv = payload[0].get("valueEstimateEur")
            etv_dev = payload[0].get("valueEstimateEur") - payload[-1].get("valueEstimateEur")
        else:
            current_etv = 0
            etv_dev = 0

        return current_etv, etv_dev

    def get_player(self, plr: dict, team_id: int) -> SquadPlayer:
        """Process a player object from the SciSports API into a SquadPlayer dataclass object."""
        sciskill, potential, sciskill_dev = self._get_sciskill(plr.get("info").get("id"))
        etv, etv_dev = self._get_etv(plr.get("info").get("id"))

        positions = plr.get("info").get("positions")
        nations = plr.get("info").get("nationalities")
        # positions
        if len(positions) >= 1:
            first_position = positions[0]
        else:
            first_position = ""
        if len(positions) >= 2:
            second_position = positions[1]
        else:
            second_position = ""
        if len(positions) >= 3:
            third_position = positions[2]
        else:
            third_position = ""
        # nationality
        if len(nations) >= 1:
            first_nation = nations[0].get('alpha3Code')
        else:
            first_nation = ""
        if len(nations) >= 2:
            second_nation = nations[1].get('alpha3Code')
        else:
            second_nation = ""
        # contract
        contract_end = plr.get('contract', {}).get('contractEnd')
        if contract_end is not None:
            contract = datetime.strptime(contract_end, "%Y-%m-%dT%H:%M:%S")
        else:
            contract = datetime(1990, 1, 1)
        loan_end = plr.get('contract', {}).get('onLoanUntil')
        if loan_end is not None:
            on_loan = True
            loan = datetime.strptime(loan_end, "%Y-%m-%dT%H:%M:%S")
        else:
            on_loan = False
            loan = datetime(1990, 1, 1)
        if plr.get("info").get('birthDate') is not None:
            birth_date = datetime.strptime(plr.get("info").get('birthDate'), "%Y-%m-%dT%H:%M:%S")
            age = (datetime.now() - birth_date).days // 365
        else:
            birth_date = datetime(1990, 1, 1)
            age = 0

        return SquadPlayer(
            player_id=plr.get("info").get("id"),
            team_id=team_id,
            name=plr.get("info").get("name"),
            age=age,
            height=plr.get("info").get("height"),
            birth_date=birth_date,
            first_nationality=first_nation,
            second_nationality=second_nation,
            image_url=plr.get("info").get("imageUrl"),
            first_name=plr.get("info").get("firstName"),
            last_name=plr.get("info").get("lastName"),
            football_name=plr.get("info").get("footballName"),
            preferred_foot=plr.get("info").get("preferredFoot"),
            first_position=first_position,
            second_position=second_position,
            third_position=third_position,
            contract_end=contract,
            loan_end=loan,
            on_loan=on_loan,
            market_value=plr.get("contract", {}).get("marketValue", 0),
            etv_current=etv,
            etv_dev=etv_dev,
            sciskill=sciskill,
            sciskill_dev=sciskill_dev,
            potential=potential,
        )


class TeamsAPI(RecruitmentAPI):
    """API interface for interaction with the SciSports teams and related endpoints.

    Parameters
    ----------
    credentials: ApiCredentials
        User credentials to pass for API authorization.

    Methods
    -------
    get_team(team_id: int, account_id: Optional[str] = None) -> SciSportsTeam:
        Get a SciSports team by id.
    get_team_players(team_id: int) -> List[SquadPlayer]:
        Get team players object for the squad.
    get_team_stats(self):
        Get aggregated performance stats for the team.

    See also
    --------
    https://developers.scisports.app/recruitment-center/api-reference
    """
    def __init__(self, credentials: ApiCredentials):
        """Inits TeamsAPI with API credentials."""
        super().__init__(credentials)
        self._pAPI = PlayersAPI(credentials)

    def get_team(self, team_id: int, account_id: Optional[str] = None) -> SciSportsTeam:
        """Get a SciSports team by id.

        Parameters
        ----------
        team_id: int
            Entity id for the team to query.
        account_id: Optional[str] = None
            Account id, optional parameter, only required for private players with limited visibility.

        Returns
        -------
        SciSportsTeam
            Dataclass object representing the team.

        See also
        --------
        scisquad.model.entities.SciSportsTeam
        """
        payload = self.get_request(
            f"v2/Teams/{team_id}",
            params={
                "accountId": account_id,
            }
        )

        return SciSportsTeam(
            team_id=payload.get("id"),
            name=payload.get("name"),
            logo=payload.get("imageUrl"),
            seasons=self._get_team_seasons(team_id),
            transfers=self._get_team_transfers(team_id),
            match_sheets=self._get_match_sheets(team_id),
            squad=self.get_team_players(team_id),
            team_type=payload.get("teamType"),
            age_group=payload.get("ageGroup", 24),
            )

    def get_team_players(self, team_id: int) -> List[SquadPlayer]:
        """Get team players object for the squad."""
        payload = self.get_request(
            f"v2/Players",
            params={
                "Limit": 1000,
                "CurrentTeamIds": team_id,
                "PlayerStates": True,
                "VisibleInRecruitment": True
            }
        )

        return [self._pAPI.get_player(plr, team_id) for plr in payload.get("items")]


    def _get_team_seasons(self, team_id: int, delta: timedelta = timedelta(days=365)) -> List[SciSportsSeason]:
        """Get all seasons for a given league starting between today and today - delta.

        Parameters
        ----------
        team_id: int
            The team to get seasons for.
        delta: timedelta = timedelta(days=365)
            The delta window to include in the search.

        Returns
        -------
        List[SciSportsSeason]
            List of all seasons in a league, including basic season attributes

        See also
        --------
        scisquad.model.entities.SciSportsSeason
        """
        res = []
        season_groups = self.get_season_groups(delta)
        groups = ""
        for group in season_groups:
            groups += f"&SeasonGroupIds={group}"
        payload = self.get_request(
            f"v2/Seasons?TeamIds={team_id}{groups}",
            params={
                "Limit": 1000
            }
        )
        for season in payload.get("items"):
            res.append(SciSportsSeason(
                league_id=season.get('league').get('id'),
                league_name=season.get('league').get('id'),
                league_gender=season.get('league').get('gender'),
                league_nation_id=season.get('league').get('nation').get('id'),
                league_logo=season.get('league').get('imageUrl'),
                season_id=season.get('id'),
                season_name=season.get('name'),
                season_group_id=season.get('group').get('id'),
                start_date=datetime.strptime(season.get('startDate'), "%Y-%m-%dT%H:%M:%S"),
                end_date=datetime.strptime(season.get('endDate'), "%Y-%m-%dT%H:%M:%S"),
                fixtures=self._get_team_season_matches(team_id, season.get('id')),
            ))

        return res

    def _get_match_sheets(self, team_id: int, delta: timedelta = timedelta(days=365)) -> List[dict]:
        """Get all match sheets for a given team starting between today and today - delta."""
        res = []

        season_groups = self.get_season_groups(delta)
        groups = ""
        for group in season_groups:
            groups += f"&SeasonGroupIds={group}"
        payload = self.get_request(
            f"v2/Seasons?TeamIds={team_id}{groups}",
            params={
                "Limit": 1000
            }
        )
        matches = self.get_request(
            f"v2/Matches",
            params={
                "Limit": 1000,
                "SeasonIds": [s.get('id') for s in payload.get("items")],
                "TeamIds": team_id,
            }
        )

        for m in matches.get('items'):
            sheet = self.get_request(
                f"v2/Matches/{m.get('id')}/sheet",
                params={
                    "includeNotMappedPlayers": False
                }
            )
            res.append(sheet)

        return res

    def _get_team_transfers(self, team_id: int) -> List[Transfer]:
        """Get the last 100 incoming and outgoing transfers for a team."""
        res = []
        transfers = []
        # last 100 incoming transfers
        incoming = self.get_request(
            f"v2/Transfers",
            params={
                "Limit": 100,
                "ToTeamIds": team_id,
                "OrderBy": "transferDate",
                "SortOrder": "descending"
            }
        )
        transfers += incoming.get("items")
        # last 100 outgoing transfers
        outgoing = self.get_request(
            f"v2/Transfers",
            params={
                "Limit": 100,
                "FromTeamIds": team_id,
                "OrderBy": "transferDate",
                "SortOrder": "descending"
            }
        )
        transfers += outgoing.get("items")

        for t in transfers:
            if t.get("fromLeague") is None:
                t.update({
                    "fromLeague":
                        {
                            "id": 0,
                            "name": "Without Contract",
                            "nation": {}
                        }
                }
                )
            if t.get("fromLeague", {}).get("nation") is None:
                t["fromLeague"]["nation"] = {}
            if t.get("toLeague") is None:
                t.update({
                    "toLeague":
                        {
                            "id": 0,
                            "name": "Without Contract",
                            "nation": {}
                        }
                }
                )
            if t.get("toLeague", {}).get("nation") is None:
                t["toLeague"]["nation"] = {}
            res.append(Transfer(
                player_id=t.get("player").get("id"),
                player_name=t.get("player").get("name"),
                from_team_id=t.get("fromTeam", {}).get("id"),
                from_team_name=t.get("fromTeam", {}).get("name"),
                from_league_id=t.get("fromLeague", {}).get("id"),
                from_league_name=t.get("fromLeague", {}).get("name"),
                from_league_nation=t.get("fromLeague", {}).get("nation", {}).get("alpha3Code"),
                to_team_id=t.get("toTeam").get("id"),
                to_team_name=t.get("toTeam").get("name"),
                to_league_id=t.get("toLeague").get("id"),
                to_league_name=t.get("toLeague").get("name"),
                to_league_nation=t.get("toLeague").get("nation").get("alpha3Code"),
                fee=t.get("fee", 0),
                is_internal=t.get("isInternal"),
                is_end_loan=t.get("isEndLoan"),
                is_loan=t.get("isLoan"),
                market_value=t.get("marketValue", 0),
                transfer_date=t.get("transferDate"),
                contract_date=t.get("contractEndDate"),
            ))

        return res

    def _get_team_season_matches(self, team_id: int, season_id: int) -> List[SciSportsMatch]:
        """Get all matches for a team in a season.

        Parameters
        ----------
        team_id: int
            Team to get the matches for.
        season_id: int
            SciSports entity id for the season.

        Returns
        -------
        List[SciSportsMatch]
            List of all matches in a season, including basic match attributes.
        """
        res = []

        payload = self.get_request(
            f"v2/Matches",
            params={
                "Limit": 1000,
                "SeasonIds": season_id,
                "TeamIds": team_id,
            }
        )

        for m in payload.get('items'):
            res.append(SciSportsMatch(
                match_id=m.get('id'),
                match_name=m.get('name'),
                league_id=m.get('league').get('id'),
                league_name=m.get('league').get('name'),
                league_nation=m.get('league').get('nation').get('alpha3Code'),
                season_id=m.get('season').get('id'),
                season_name=m.get('season').get('name'),
                match_day=m.get('round', {}).get('matchDay'),
                home_team_id=m.get('homeTeam').get('id'),
                home_team_name=m.get('homeTeam').get('name'),
                home_team_logo=m.get('homeTeam').get('imageUrl'),
                home_team_goals=m.get("homeTeamGoals", 0),
                away_team_id=m.get('awayTeam').get('id'),
                away_team_name=m.get('awayTeam').get('name'),
                away_team_logo=m.get('awayTeam').get('imageUrl'),
                away_team_goals=m.get("awayTeamGoals", 0),
                kick_off_date=m.get('kickOffDate'),
            ))

        return res

    #TODO: add team stats once endpoints are released to production
    def get_team_stats(self):
        """Get aggregated performance stats for the team."""
        pass


class LeaguesAPI(RecruitmentAPI):
    """API interface for interaction with the SciSports league and related endpoints.

    Extra information
    -----------------
    Entities represent the main objects with the SciSports data-model, and contain entities like leagues, seasons,
    teams, matches and players. The Leagues API provides a high-level interface for getting leagues from the API,
    including all underlying entities like seasons and matches.

    Parameters
    ----------
    credentials: ApiCredentials
        User credentials to pass for API authorization.

    Methods
    -------
    get_leagues(
            league_types: List[LeagueType],
            gender: List[Gender],
            search_text: Optional[str] = None,
            age_groups: Optional[List[AgeGroup]] = None,
            nations: Optional[List[Nations]] = None,
            limit: int = 10,
            offset: int = 0,
            date_modified: Optional[str] = "2024-01-01T00:00:00.000Z",
    ) -> List[SciSportsLeague]:
        Get a list of SciSports leagues with basic attributes.
    get_league_seasons(league: SciSportsLeague, delta: timedelta = timedelta(days=365)) -> List[SciSportsSeason]
        Get all seasons for a given league starting between today and today - delta.

    Examples
    --------
    This class will mainly be used to collect league information, including underlying seasons and matches.
    One would for example use this class to get a list of all Dutch leagues, and then get underlying entities for
    the first league that is returned as follows:

        credentials = ApiCredentials(
        username=os.getenv("API_USER"),
        password=os.getenv("API_PW"),
        client_id=os.getenv("API_CLIENT_ID"),
        client_secret=os.getenv("API_CLIENT_SECRET"),
        )
        API = LeaguesAPI(credentials)
        leagues = API.get_leagues(
            league_types=[LeagueType.DOMESTIC_LEAGUE],
            gender=[Gender.MALE],
            nations=[Nations.NLD]
        )
        seasons = API.get_league_seasons(leagues[0])

    See also
    --------
    https://developers.scisports.app/recruitment-center/api-reference
    """
    def __init__(self, credentials: ApiCredentials):
        """Inits EntitiesAPI with API credentials."""
        super().__init__(credentials)

    def get_leagues(
            self,
            league_types: List[LeagueType],
            gender: List[Gender],
            search_text: Optional[str] = None,
            age_groups: Optional[List[AgeGroup]] = None,
            nations: Optional[List[Nations]] = None,
            limit: int = 10,
            offset: int = 0,
            date_modified: Optional[str] = "2024-01-01T00:00:00.000Z",
    ) -> List[SciSportsLeague]:
        """Get a list of SciSports leagues with basic attributes.

        Parameters
        ----------
        league_types: List[LeagueType]
            Only return leagues that are part of the specified league types.
        gender: List[Gender]
            Only return leagues that are part of the specified genders.
        search_text: Optional[str] = None
            Search to the name of the league
        age_groups: Optional[List[AgeGroup]] = None
            If specified, only include leagues that are part of the specified age groups (range 13-23).
        nations: Optional[List[Nations]] = None
            If specified, only include leagues that are part of the specified nations.
        limit: int = 10
            Include no more than limit in the result, default limit is 10.
        offset: int = 0
            Omit the first offset from the result.
        date_modified: Optional[str] = "2024-01-01T00:00:00.000Z"
            Include in the list only items that were updated on or after the specified date.

        Returns
        -------
        List[SciSportsLeague]
            List of SciSports leagues, represented as SciSportsLeague dataclass objects.

        See also
        --------
            scisquad.model.entities.SciSportsLeague
        """
        payload = self.get_request(
            "v2/Leagues",
            params={
                "Limit": limit,
                "Offset": offset,
                "SearchText": search_text,
                "Genders": [g.gender_id for g in gender],
                "LeagueTypes": [l.league_type_id for l in league_types],
                "AgeGroups": [x.value for x in age_groups] if age_groups else None,
                "NationIds": [x.value for x in nations] if nations else None,
                "isActive": True,
                "HasPriority": True,
                "dateModifiedBiggerThan": date_modified
            }
        )

        return [SciSportsLeague(
            league_id=comp.get('id'),
            league_name=comp.get('name'),
            league_gender=comp.get('gender'),
            league_type=comp.get("leagueType"),
            league_nation_id=comp.get('nation', {}).get('id'),
            league_age_group=comp.get('ageGroup'),
            league_logo=comp.get('imageUrl'),
        ) for comp in payload.get('items') if not comp.get('nation') is None]

    def get_league_seasons(
            self,
            league: SciSportsLeague,
            delta: timedelta = timedelta(days=365)
    ) -> List[SciSportsSeason]:
        """Get all seasons for a given league starting between today and today - delta.

        Parameters
        ----------
        league: SciSportsLeague
            The league to get seasons for.
        delta: timedelta = timedelta(days=365)
            The delta window to include in the search.

        Returns
        -------
        List[SciSportsSeason]
            List of all seasons in a league, including basic season attributes

        See also
        --------
        scisquad.model.entities.SciSportsSeason
        """
        res = []
        season_groups = self.get_season_groups(delta)
        groups = ""
        for group in season_groups:
            groups += f"&SeasonGroupIds={group}"
        payload = self.get_request(
            f"v2/Seasons?LeagueIds={league.league_id}{groups}",
            params={
                "Limit": 1000
            }
        )
        for season in payload.get("items"):
            res.append(SciSportsSeason(
                league_id=league.league_id,
                league_name=league.league_name,
                league_gender=league.league_gender,
                league_nation_id=league.league_nation_id,
                league_logo=league.league_logo,
                season_id=season.get('id'),
                season_name=season.get('name'),
                season_group_id=season.get('group').get('id'),
                start_date=datetime.strptime(season.get('startDate'), "%Y-%m-%dT%H:%M:%S"),
                end_date=datetime.strptime(season.get('endDate'), "%Y-%m-%dT%H:%M:%S"),
                fixtures=self._get_season_matches(season.get('id')),
            ))

        return res

    def _get_season_matches(self, season_id: int) -> List[SciSportsMatch]:
        """Get all matches in a season.

        Parameters
        ----------
        season_id: int
            SciSports entity id for the season

        Returns
        -------
        List[SciSportsMatch]
            List of all matches in a season, including basic match attributes.
        """
        res = []

        payload = self.get_request(
            f"v2/Matches",
            params={
                "Limit": 1000,
                "SeasonIds": season_id
            }
        )

        for m in payload.get('items'):
            res.append(SciSportsMatch(
                match_id=m.get('id'),
                match_name=m.get('name'),
                league_id=m.get('league').get('id'),
                league_name=m.get('league').get('name'),
                league_nation=m.get('league').get('nation').get('alpha3Code'),
                season_id=m.get('season').get('id'),
                season_name=m.get('season').get('name'),
                match_day=m.get('round', {}).get('matchDay'),
                home_team_id=m.get('homeTeam').get('id'),
                home_team_name=m.get('homeTeam').get('name'),
                home_team_logo=m.get('homeTeam').get('imageUrl'),
                home_team_goals=m.get("homeTeamGoals", 0),
                away_team_id=m.get('awayTeam').get('id'),
                away_team_name=m.get('awayTeam').get('name'),
                away_team_logo=m.get('awayTeam').get('imageUrl'),
                away_team_goals=m.get("awayTeamGoals", 0),
                kick_off_date=m.get('kickOffDate'),
            ))

        return res
