from typing import Union
from typing import List
from datetime import timedelta
from datetime import datetime
from dataclasses import asdict

import pandas as pd
from tqdm import tqdm

from scisquad.model.entities import Position
from scisquad.model.entities import SciSportsTeam
from scisquad.model.recommendations import AlertPriority
from scisquad.model.recommendations import AlertType
from scisquad.model.recommendations import Alert


class PlayerAlerts:
    """Alert constructor for player level alerts.

    Extra Information
    ----------------
    Alerts are set based on a set of heuristics related to the contract date, loan period and age.

    Parameters
    ----------
    team: SciSportsTeam
        A SciSports team object, including transfer history of the team.
    contract_delta: timedelta = timedelta(weeks=52)
        Parameter to define the cut-off for contract endings.
    loan_delta: timedelta = timedelta(weeks=26)
        Parameter to define the cut-off for loan endings.
    run_date: datetime = datetime.now()
        Date for which to simulate the squad.
    peak_age_limit: float = 28.0
        Parameter setting the limit for peak age.

    Attributes
    ----------
    alerts: List[Alert]
        Player-level alerts.

    Methods
    -------
    set_alerts():
        Set all alerts for the squad.
    """

    def __init__(
            self,
            team: SciSportsTeam,
            contract_delta: timedelta = timedelta(weeks=52),
            loan_delta: timedelta = timedelta(weeks=26),
            run_date: datetime = datetime.now(),
            peak_age_limit: float = 28.0,
    ):
        """Inits PlayerAlerts with data and temporal parameters."""
        self._team = team
        self._matches = pd.DataFrame(self._team.match_team_attributes)
        self._squad = pd.DataFrame(self._team.squad)
        self._transfers = pd.DataFrame([asdict(t) for t in team.transfers])
        self._preprocess()
        self.alerts = []
        self._contract_delta = contract_delta
        self._loan_delta = loan_delta
        self._run_date = run_date
        self._peak_age_limit = peak_age_limit
        self._move_squad_forward()

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

    def _preprocess(self):
        """Preprocessing wrapper."""
        df_transfers = self._preprocess_transfers()
        self._squad = self._squad.merge(df_transfers, on="player_id", how="left")
        self._preprocess_squad()


    def _move_squad_forward(self):
        """Move the squad forward in time to account for the current run date."""
        self._squad['age'] = self._run_date - self._squad['birth_date']
        self._squad['age'] = self._squad['age'].dt.days / 365.25
        self._squad['exclude'] = (
                (
                        (self._squad['contract_end'] < self._run_date) &
                        (~self._squad['on_loan'])
                ) |
                (
                        (self._squad['loan_end'] < self._run_date) &
                        (self._squad['on_loan'])
                )
        )
        for plr in self._squad[self._squad['exclude']].to_dict("records"):
            prio = self._get_player_priority(plr)
            self.alerts.append(Alert(
                alert_type=AlertType.CONTRACT_OR_LOAN_EXPIRED,
                alert_priority=prio,
                position=self._map_group(plr['first_position']),
                player=plr['name']
            ))
        self._squad = self._squad[~self._squad['exclude']].copy()

    @staticmethod
    def _map_group(group: str) -> Position:
        """Map position groups to their respective Position enum."""
        mapping = {
            "Goalkeeper": Position.GOALKEEPER,
            "CentreBack": Position.CENTRE_BACK,
            "LeftBack": Position.LEFT_BACK,
            "RightBack": Position.RIGHT_BACK,
            "DefensiveMidfield": Position.DEFENSIVE_MIDFIELDER,
            "CentreMidfield": Position.CENTRE_MIDFIELDER,
            "AttackingMidfield": Position.ATTACKING_MIDFIELDER,
            "RightWing": Position.RIGHT_WING,
            "LeftWing": Position.LEFT_WING,
            "CentreForward": Position.CENTRE_FORWARD
        }

        return mapping.get(group, Position.OTHER)

    @staticmethod
    def _get_player_priority(plr: dict) -> AlertPriority:
        """Determine alert priority based on the player usage."""
        if plr['usage'] > 75:
            return AlertPriority.CRITICAL
        elif 50 < plr['usage'] <= 75:
            return AlertPriority.HIGH
        elif 25 < plr['usage'] <= 50:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW

    @staticmethod
    def _get_player_alert_type(plr: dict) -> List[AlertType]:
        """Determine one or multiple alert types applicable to a player."""
        alerts = []
        if plr['contract_ends_alert']:
            alerts.append(AlertType.CONTRACT_ENDING)
        if plr['loan_ends_alert']:
            alerts.append(AlertType.LOAN_ENDING)
        if plr['age_alert']:
            alerts.append(AlertType.PAST_PEAK_AGE)

        return alerts

    def _set_player_alerts(self, row: dict):
        """Create all alerts for a single player."""
        prio = self._get_player_priority(row)
        alerts = self._get_player_alert_type(row)
        for alert in alerts:
            self.alerts.append(Alert(
                alert_type=alert,
                alert_priority=prio,
                position=self._map_group(row['first_position']),
                player=row['name']
            ))

    def _set_contract_action(self):
        """Set an alert for every contract terminating within the next n months."""
        self._squad['contract_ends_alert'] = (
                (self._squad['contract_end'] <= self._run_date + self._contract_delta) &
                (~self._squad['on_loan'])
        )

    def _set_loan_ending(self):
        """Set an alert for every loan ending within the next n months."""
        self._squad['loan_ends_alert'] = (
                (self._squad['loan_end'] <= self._run_date + self._loan_delta) &
                (self._squad['on_loan'])
        )

    def _set_age_issues(self):
        """Set an alert for any player that is past peak age and can be expected to decline."""
        self._squad['age_alert'] = self._squad['age'] > self._peak_age_limit

    def set_alerts(self):
        """Set all alerts for the squad."""
        self._set_contract_action()
        self._set_loan_ending()
        self._set_age_issues()
        for plr in tqdm(self._squad.to_dict("records"), "SET PLAYER ALERTS"):
            self._set_player_alerts(plr)


class PositionAlerts:
    """Alert constructor for position level alerts.

    Extra Information
    ----------------
    Alerts are set based on a set of heuristics related to the SciSkill ranking potential and number of players,
    all aggregated per position group.

    Parameters
    ----------
    team: SciSportsTeam
        A SciSports team object, including transfer history of the team.

    Attributes
    ----------
    alerts: List[Alert]
        Position-level alerts.

    Methods
    -------
    set_alerts():
        Set all alerts for the squad.

    See Also
    --------
    See insights.teams.squad_manager.squad.SquadManager for more information on the SquadManager class.
    """

    def __init__(self, team: SciSportsTeam):
        """Inits PositionAlerts with team data and sets alerts to an empty list."""
        self._team = team
        self._matches = pd.DataFrame(self._team.match_team_attributes)
        self._squad = pd.DataFrame(self._team.squad)
        self._preprocess()
        self.alerts = []
        self._benchmarks = []

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

    def _preprocess(self):
        """Preprocessing wrapper."""
        self._preprocess_squad()

    @staticmethod
    def _set_rank(df: pd.DataFrame, level: str = "starter", feature: str = "level"):
        """Assign the rank based on SciSkill sorting."""
        df.sort_values(f"{level}_{feature}", ascending=False, inplace=True)
        df.reset_index(inplace=True, drop=True)
        df.loc[:, f'{level}_{feature}_rank'] = df.index + 1

    @staticmethod
    def _map_group(group: Union[str, Position], reverse: bool = False) -> Union[Position, str]:
        """Map position groups to their respective Position enum."""
        mapping = {
            "Goalkeeper": Position.GOALKEEPER,
            "CentreBack": Position.CENTRE_BACK,
            "LeftBack": Position.LEFT_BACK,
            "RightBack": Position.RIGHT_BACK,
            "DefensiveMidfield": Position.DEFENSIVE_MIDFIELDER,
            "CentralMidfield": Position.CENTRE_MIDFIELDER,
            "AttackingMidfield": Position.ATTACKING_MIDFIELDER,
            "RightWing": Position.RIGHT_WING,
            "LeftWing": Position.LEFT_WING,
            "CentreForward": Position.CENTRE_FORWARD
        }
        if reverse:
            mapping = {v: k for k, v in mapping.items()}
            return mapping.get(group)
        else:
            return mapping.get(group, Position.OTHER)

    def _get_position_group(self, group: Position, include_secondary_positions: bool = True) -> pd.DataFrame:
        """Return all players on a given position.

        Extra Information
        -----------------
        If include_secondary_positions is True, secondary positions are included in the returned DataFrame, which
        means that players with a second or third position matching the conditions are included. Note that this could
        also result in players being returned as part of multiple position groups, which could hide alerts.
        """
        group = self._map_group(group, reverse=True)
        if include_secondary_positions:
            return self._squad[
                (self._squad['first_position'] == group) |
                (self._squad['second_position'] == group) |
                (self._squad['third_position'] == group)
                ].sort_values("sciskill", ascending=False).copy()
        else:
            return self._squad[self._squad['first_position'] == group].sort_values("sciskill", ascending=False).copy()

    def _set_position_benchmarks(self, group: Position):
        """Set benchmarks for a position group."""
        df = self._get_position_group(group)
        if len(df) > 0:
            starter_level = df['sciskill'].iloc[0]
            starter_potential = df['potential'].iloc[0]
        else:
            starter_level = 0
            starter_potential = 0
        if len(df) > 1:
            back_up_level = df['sciskill'].iloc[1]
            back_up_potential = df['potential'].iloc[1]
        else:
            back_up_level = 0
            back_up_potential = 0
        if len(df) > 2:
            secondary_back_up_level = df['sciskill'].iloc[2]
            secondary_back_up_potential = df['potential'].iloc[2]
        else:
            secondary_back_up_level = 0
            secondary_back_up_potential = 0

        self._benchmarks.append({
            "group": group,
            "starter_level": starter_level,
            "starter_potential": starter_potential,
            "back_up_level": back_up_level,
            "back_up_potential": back_up_potential,
            "secondary_back_up_level": secondary_back_up_level,
            "secondary_back_up_potential": secondary_back_up_potential
        })

    def _aggregate_groups(self):
        """Aggregate groups to set the position benchmarks."""
        for group in tqdm([
            "Goalkeeper",
            "CentreBack",
            "LeftBack",
            "RightBack",
            "DefensiveMidfield",
            "CentralMidfield",
            "AttackingMidfield",
            "RightWing",
            "LeftWing",
            "CentreForward"
        ], "CALCULATING POSITION BENCHMARKS"):
            position = self._map_group(group)
            self._set_position_benchmarks(position)

    def _get_set_group_kpis(self) -> pd.DataFrame:
        """Calculate group level KPI's to use as input for the alert calculations."""
        self._aggregate_groups()
        df_groups = pd.DataFrame(self._benchmarks)
        self._set_rank(df_groups, "starter", "level")
        self._set_rank(df_groups, "back_up", "level")
        self._set_rank(df_groups, "secondary_back_up", "level")
        self._set_rank(df_groups, "starter", "potential")
        self._set_rank(df_groups, "back_up", "potential")
        self._set_rank(df_groups, "secondary_back_up", "potential")

        return df_groups

    @staticmethod
    def _set_depth_issues(df_groups: pd.DataFrame) -> pd.DataFrame:
        """Set an alert for any position that lacks depth.

        Extra Information
        ----------------
        Depth is defined as the number of players per position group, and feature additional heuristics like age
        and SciSkill to define rules for depth quality.
        """
        for group in tqdm(df_groups.to_dict("records"), "CALCULATING DEPTH ISSUES"):
            if group['starter_level'] == 0 or group['back_up_level'] == 0 or group['secondary_back_up_level'] == 0:
                df_groups.loc[df_groups['group'] == group['group'], 'depth_alert'] = True
            else:
                df_groups.loc[df_groups['group'] == group['group'], 'depth_alert'] = False

        return df_groups

    @staticmethod
    def _set_strength_issues(df_groups: pd.DataFrame, level: str = "starter") -> pd.DataFrame:
        """Set an alert for any position that has a relatively low back-up or starting player level."""
        for group in tqdm(df_groups.to_dict("records"), f"CALCULATING STRENGTH ISSUES FOR {level}"):
            level_bottom = group[f'{level}_level_rank'] > df_groups[f'{level}_level_rank'].max() - 3
            potential_bottom = group[f'{level}_potential_rank'] > df_groups[f'{level}_potential_rank'].max() - 3
            if level_bottom and potential_bottom:
                df_groups.loc[df_groups['group'] == group['group'], f'weak_{level}_alert'] = True
            else:
                df_groups.loc[df_groups['group'] == group['group'], f'weak_{level}_alert'] = False

        return df_groups

    def _get_set_alerts(self) -> pd.DataFrame:
        """Set all alerts for the squad."""
        df_groups = self._get_set_group_kpis()
        df_groups = self._set_depth_issues(df_groups)
        df_groups = self._set_strength_issues(df_groups, "starter")
        df_groups = self._set_strength_issues(df_groups, "back_up")
        df_groups = self._set_strength_issues(df_groups, "secondary_back_up")

        return df_groups

    def _set_position_alerts(self, pos: dict):
        """Set the alerts for a position group."""
        if pos['depth_alert']:
            self.alerts.append(
                Alert(
                    alert_type=AlertType.LACK_OF_DEPTH,
                    alert_priority=AlertPriority.MEDIUM,
                    position=pos['group']
                )
            )
        if pos['weak_starter_alert']:
            self.alerts.append(
                Alert(
                    alert_type=AlertType.WEAK_SPOT_STARTER,
                    alert_priority=AlertPriority.HIGH,
                    position=pos['group']
                )
            )
        if pos['weak_back_up_alert']:
            self.alerts.append(
                Alert(
                    alert_type=AlertType.WEAK_SPOT_BACK_UP,
                    alert_priority=AlertPriority.MEDIUM,
                    position=pos['group']
                )
            )
        if pos['weak_secondary_back_up_alert']:
            self.alerts.append(
                Alert(
                    alert_type=AlertType.WEAK_SPOT_SECONDARY,
                    alert_priority=AlertPriority.LOW,
                    position=pos['group']
                )
            )

    def set_alerts(self):
        """Set all alerts for the squad."""
        df_groups = self._get_set_alerts()
        for pos in tqdm(df_groups.to_dict("records"), f"SET POSITION ALERTS"):
            self._set_position_alerts(pos)

        return df_groups
