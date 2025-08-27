from typing import List
from typing import Union
from datetime import datetime

import pandas as pd
from tqdm import tqdm

from scisquad.api.base import RecruitmentAPI
from scisquad.api.domain import ApiCredentials
from scisquad.model.entities import Gender


class GuidedSearchAPI(RecruitmentAPI):
    """API interface for a guided player search using recommended filters.

    Extra information
    -----------------
    After initial analysis of squad characteristics and creating of a scouting plan, this is the main step for
    generating actual scouting targets.

    Parameters
    ----------
    credentials: ApiCredentials
        User credentials to pass for API authorization.

    Methods
    -------
    set_league_selection(nations: List[str]):
        Add league ids as filter parameters for the guided search.
    set_position_players(position: str = "LeftBack"):
        Get a list of all players in a given position.
    find_recommended_players(
            starter: bool = True,
            benchmark: float = 50.0,
            position: str = "LeftBack",
            budget: int = 0,
            age_lower: int = 18,
            age_upper: int = 35,
    ):
        Search for players on a given position using recommended filter criteria.

    See also
    --------
    https://developers.scisports.app/recruitment-center/api-reference
    """
    def __init__(self, credentials: ApiCredentials):
        """Inits GuidedSearchAPI with API credentials."""
        super().__init__(credentials)
        self._search_results: Union[pd.DataFrame, List[pd.DataFrame]] = []
        self._current_league_ids = []

    def set_league_selection(self, nations: List[str]):
        """Add league ids as filter parameters for the guided search."""
        for nat in nations:
            payload = self.get_request(
                "v2/Leagues",
                params={
                    "Limit": 1000,
                    "Genders": Gender.MALE.gender_id,
                    "isActive": True,
                    "NationCode": nat,
                    "HasPriority": True,
                }
            )
            self._current_league_ids += [l.get("id") for l in payload.get("items")]


    def set_position_players(self, position: str = "LeftBack"):
        """Get a list of all players in a given position."""
        self._search_results = []
        payload = self.get_request(
            "v2/Players",
            params={
                "Positions": position,
                "Context": "Male",
                "Genders": "Male",
                "PlayerStates": True,
                "VisibleInRecruitment": True,
                "CurrentLeagueIds": self._current_league_ids,
                "Limit": 1000,
                "Offset": 0
            }
        )
        n_items = payload.get("total")
        for n in tqdm(range(0, n_items, 1000), f"PROCESSING RECORDS {0}:{n_items}"):
            payload = self.get_request(
                "v2/Players",
                params={
                    "Positions": position,
                    "Context": "Male",
                    "Genders": "Male",
                    "PlayerStates": True,
                    "VisibleInRecruitment": True,
                    "Limit": 1000,
                    "Offset": n
                }
            )
            if payload.get("total") > 0:
                self._search_results.append(pd.json_normalize(payload.get("items")))

        self._search_results = pd.concat(self._search_results)

    def _set_contract_months_left(self):
        """Set the contract months left for each player."""
        self._search_results['contract_ends'] = pd.to_datetime(
            self._search_results['contract.contractEnd'],
            format='%Y-%m-%dT%H:%M:%S'
        )
        # Get current date
        current_date = datetime.now()
        # Calculate months left on contract
        self._search_results['contract_months_left'] = self._search_results['contract_ends'].apply(
            lambda end_date: max(0, ((end_date.year - current_date.year) * 12 +
                                     end_date.month - current_date.month +
                                     (1 if end_date.day >= current_date.day else 0)))
        )

    def _set_sciskill(self, plr: dict) -> dict:
        """Set the sciskill and potential for each player."""
        payload = self.get_request(
            "v2/metrics/players/sciskill",
            params={
                "PlayerIds": plr.get("info.id")
            }
        )
        if payload.get("total") > 0:
            plr.update({
                'metrics.sciskill': payload.get("items")[0].get("sciskill", 0),
                'metrics.potential': payload.get("items")[0].get("potential", 0),
            })

        return plr

    def _pre_filter_selection(self, budget: float = 0, age_lower: int = 18, age_upper: int = 35):
        """Filter the selection of players based on the provided basic criteria."""
        start = len(self._search_results)
        # basic
        self._search_results = self._search_results[
            (self._search_results['info.age'].between(age_lower, age_upper))
        ].copy()
        # contract & budget
        self._set_contract_months_left()
        if budget != 0:
            self._search_results = self._search_results[
                (
                        (self._search_results['contract_months_left'].between(0, 36)) &
                        (self._search_results['contract.marketValue'] <= budget)
                ) |
                (self._search_results['contract.isFreeAgent']) |
                (
                        (self._search_results['contract_months_left'].between(0, 11)) &
                        (self._search_results['contract.marketValue'] <= 1.5 * budget)
                )
                ].copy()
        else:
            self._search_results = self._search_results[
                (self._search_results['contract.isFreeAgent']) |
                (self._search_results['contract_months_left'].between(0, 7))
                ].copy()
        end = len(self._search_results)
        print(f"Filtered selection from {start} to {end} players.")

    def find_recommended_players(
            self,
            starter: bool = True,
            benchmark: float = 50.0,
            position: str = "LeftBack",
            budget: int = 0,
            age_lower: int = 18,
            age_upper: int = 35,
    ) -> pd.DataFrame:
        """Search for players on a given position using recommended filter criteria.

        Parameters
        ---------
        starter: bool = True
            Determines if you are looking for a player who is an immediate addition to the team or a future one.
        benchmark: float = 50.0
            Sets the lower performance level based on SciSkill of the current squad.
        position: str = "LeftBack"
            Position to search for.
        budget: int = 0
            Determines the budget based on historic spending.
        age_lower: int = 18
            Lower age limit for the search.
        age_upper: int = 35
            Upper age limit for the search.

        Returns
        -------
        df: pd.DataFrame
            A dataframe with recommended players for further scouting.
        """
        self.set_position_players(position)
        self._pre_filter_selection(0.75 * budget, age_lower, age_upper)
        res = []
        benchmark *= .95
        for plr in tqdm(self._search_results.to_dict("records"), "COLLECTING METRICS"):
            plr = self._set_sciskill(plr)
            if plr.get("metrics.sciskill") is not None:
                if starter and plr.get("metrics.sciskill", 0) >= benchmark:
                    res.append(plr)
                elif not starter and plr.get("metrics.potential", 0) >= benchmark:
                    res.append(plr)
                else:
                    continue

        print(f"Filtered selection from {len(self._search_results)} to {len(res)} players.")

        return pd.DataFrame(res)
