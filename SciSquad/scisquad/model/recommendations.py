from enum import Enum
from dataclasses import dataclass
from typing import List
from typing import Optional

from scisquad.model.entities import Position


class AlertPriority(Enum):
    """Priority levels for alerts."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AlertType(Enum):
    """Types of alerts."""
    PAST_PEAK_AGE = 1
    CONTRACT_ENDING = 2
    LOAN_ENDING = 3
    WEAK_SPOT_STARTER = 4
    WEAK_SPOT_BACK_UP = 5
    WEAK_SPOT_SECONDARY = 6
    LACK_OF_DEPTH = 7
    CONTRACT_OR_LOAN_EXPIRED = 8


@dataclass
class Alert:
    """Squad alert."""
    alert_type: AlertType
    position: Position
    alert_priority: AlertPriority
    player: Optional[str] = None


@dataclass
class SquadAlerts:
    """Squad alerts."""
    alerts: List[Alert]
