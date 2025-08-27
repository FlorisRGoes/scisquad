from typing import Dict
from typing import List

import pandas as pd

from scisquad.api.player_search import GuidedSearchAPI
from scisquad.api.management import CollaborationAPI


class ScoutingPlanner:
    """Planner to create lists with scouting targets per scouting task.

    Extra information
    -----------------
    The planner basically creates a scouting plan based on a set of predefined tasks, executes the search for
    every task, and returns the output to the application via the collaboration tools.

    Parameters
    ----------
    scouting_tasks: pd.DataFrame
        All scouting tasks to be completed.
    search_api: GuidedSearchAPI
        Player search API to retrieve players using search criteria.
    labels_api: CollaborationAPI
        Interface to manage labels, comments, and shortlists.
    squad: pd.DataFrame
        Current squad to compare against.
    transfer_insights: dict
        Aggregated kpi's on inbound transfer patterns for the team at hand.
    performance insights: dict
        Aggregated kpi's reflecting the current quality of the team.

    Attributes
    ---------
    scouting_lists: Dict[str, List[int]]
        List of players to be scouted per scouting task.

    Methods
    ------
    create_scouting_plan():
        Create the scouting plan for the upcoming transfer window.
    """
    def __init__(
            self,
            scouting_tasks: pd.DataFrame,
            search_api: GuidedSearchAPI,
            labels_api: CollaborationAPI,
            squad: pd.DataFrame,
            transfer_insights: dict,
            performance_insights: dict,
    ):
        """Inits ScoutingPlanner with tasks, api-connections and the current squad."""
        self._search_api = search_api
        self._labels_api = labels_api
        self._scouting_tasks = scouting_tasks.copy()
        self._map_positions()
        self._squad = squad.copy()
        self.scouting_lists: Dict[str, List[int]] = {}
        self._transfer_insights = transfer_insights
        self._performance_insights = performance_insights

    def _map_positions(self):
        """Map the main position names to the position names used in the search API."""
        self._scouting_tasks['position'] = self._scouting_tasks['position'].map({
            "Goalkeeper": "Goalkeeper",
            "Centre back": "CentreBack",
            "Left back": "LeftBack",
            "Right back": "RightBack",
            "Defensive midfield": "DefensiveMidfield",
            "Centre midfield": "CentreMidfield",
            "Attacking midfield": "AttackingMidfield",
            "Centre forward": "CentreForward",
            "Left wing": "LeftWing",
            "Right wing": "RightWing",
        })

    def _execute_task(self, task: dict):
        """Execute the search for a single scouting task."""
        if len(list(self._transfer_insights.get("inbound_market_shares").keys())) > 10:
            self._search_api.set_league_selection(list(self._transfer_insights.get("inbound_market_shares").keys())[:10])
        else:
            self._search_api.set_league_selection(list(self._transfer_insights.get("inbound_market_shares").keys()))
        recommendations = self._search_api.find_recommended_players(
            benchmark=self._performance_insights.get("mean_sciskill_top_15"),
            budget=self._transfer_insights.get("fee_range").get("max")
        )

        print(f"{len(recommendations)} compatible players found for {task.get('position')} - {task.get('level')}")
        if not len(recommendations) == 0:
            self.scouting_lists.update({
                task.get("position") + "_" + task.get("level"): recommendations['info.id'].values.tolist()
            })

    def _create_label(self, task: dict):
        """Set the label for the scouting task."""
        print(f'Setting new Label:: Virtual Director: {task.get("position") + "_" + task.get("level")}')
        self._labels_api.add_label(f'Virtual Director: {task.get("position") + "_" + task.get("level")}')

    def _assign_labels(self, task: dict):
        """Assign a label to every player in the scouting task."""
        if self.scouting_lists.get(task.get("position") + "_" + task.get("level")) is not None:
            self._labels_api.put_player_labels(
                f'Virtual Director: {task.get("position") + "_" + task.get("level")}',
                self.scouting_lists.get(task.get("position") + "_" + task.get("level"))
            )

    def create_scouting_plan(self):
        """Create the scouting plan for the upcoming transfer window."""
        for task in self._scouting_tasks.to_dict('records'):
            self._execute_task(task)
            self._create_label(task)
            self._assign_labels(task)
