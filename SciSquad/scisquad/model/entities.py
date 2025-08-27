from enum import Enum
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import List
from typing import Optional


class Gender(Enum):
    """Genders supported in the SciSports entity framework."""
    MALE = (0, "male")
    FEMALE = (1, "female")

    def __init__(self, gender_id: int, gender_name: str):
        self.gender_id = gender_id
        self.gender_name = gender_name


class LeaguePriority(Enum):
    """Entity league priority level"""
    LOW = (0, "low")
    MEDIUM = (1, "medium")
    HIGH = (2, "high")

    def __init__(self, priority_id: int, priority_name: str):
        self.priority_id = priority_id
        self.priority_name = priority_name


class LeagueType(Enum):
    """League types supported in the SciSports entity framework."""
    DOMESTIC_PLAYOFFS = (1, "domestic_playoffs")
    DOMESTIC_LEAGUE = (2, "domestic_league")
    DOMESTIC_CUP = (3, "domestic_cup")
    DOMESTIC_SUPERCUP = (4, "domestic_supercup")
    INTERNATIONAL_CUP = (5, "international_cup")
    INTERNATIONAL_SUPERCUP = (6, "international_supercup")

    def __init__(self, league_type_id: int, league_type_name: str):
        self.league_type_id = league_type_id
        self.league_type_name = league_type_name


class AgeGroup(Enum):
    """Age groups supported in the SciSports entity framework."""
    THIRTEEN = 13
    FOURTEEN = 14
    FIFTEEN = 15
    SIXTEEN = 16
    SEVENTEEN = 17
    EIGHTEEN = 18
    NINETEEN = 19
    TWENTY = 20
    TWENTY_ONE = 21
    TWENTY_TWO = 22
    TWENTY_THREE = 23


class Nations(Enum):
    """Nations supported in the SciSports entity framework."""
    AFG = 1
    ALA = 2
    ALB = 3
    DZA = 4
    ASM = 5
    AND = 6
    AGO = 7
    AIA = 8
    AN = 9
    ATG = 10
    ARG = 11
    ARM = 12
    ABW = 13
    AUS = 14
    AUT = 15
    AZE = 16
    BHS = 17
    BHR = 18
    BGD = 19
    BRB = 20
    BLR = 21
    BEL = 22
    BLZ = 23
    BEN = 24
    BMU = 25
    BTN = 26
    BOL = 27
    BES = 28
    BIH = 29
    BWA = 30
    BVT = 31
    BRA = 32
    IOT = 33
    UMI = 34
    VGB = 35
    VIR = 36
    BRN = 37
    BGR = 38
    BFA = 39
    BDI = 40
    KHM = 41
    CMR = 42
    CAN = 43
    CPV = 44
    CYM = 45
    CAF = 46
    TCD = 47
    CHL = 48
    CHN = 49
    CXR = 50
    CCK = 51
    COL = 52
    COM = 53
    COG = 54
    COD = 55
    COK = 56
    CRI = 57
    HRV = 58
    CUB = 59
    CUW = 60
    CYP = 61
    CZE = 62
    DNK = 63
    DJI = 64
    DMA = 65
    DOM = 66
    ECU = 67
    EGY = 68
    SLV = 69
    GNQ = 70
    ERI = 71
    EST = 72
    ETH = 73
    FLK = 74
    FRO = 75
    FJI = 76
    FIN = 77
    FRA = 78
    GUF = 79
    PYF = 80
    ATF = 81
    GAB = 82
    GMB = 83
    GEO = 84
    DEU = 85
    GHA = 86
    GIB = 87
    GRC = 88
    GRL = 89
    GRD = 90
    GLP = 91
    GUM = 92
    GTM = 93
    GGY = 94
    GIN = 95
    GNB = 96
    GUY = 97
    HTI = 98
    HMD = 99
    VAT = 100
    HND = 101
    HKG = 102
    HUN = 103
    ISL = 104
    IND = 105
    IDN = 106
    CIV = 107
    IRN = 108
    IRQ = 109
    IRL = 110
    IMN = 111
    ISR = 112
    ITA = 113
    JAM = 114
    JPN = 115
    JEY = 116
    JOR = 117
    KAZ = 118
    KEN = 119
    KIR = 120
    KWT = 121
    KGZ = 122
    LAO = 123
    LVA = 124
    LBN = 125
    LSO = 126
    LBR = 127
    LBY = 128
    LIE = 129
    LTU = 130
    LUX = 131
    MAC = 132
    MKD = 133
    MDG = 134
    MWI = 135
    MYS = 136
    MDV = 137
    MLI = 138
    MLT = 139
    MHL = 140
    MTQ = 141
    MRT = 142
    MUS = 143
    MYT = 144
    MEX = 145
    FSM = 146
    MDA = 147
    MCO = 148
    MNG = 149
    MNE = 150
    MSR = 151
    MAR = 152
    MOZ = 153
    MMR = 154
    NAM = 155
    NRU = 156
    NPL = 157
    NLD = 158
    NCL = 159
    NZL = 160
    NIC = 161
    NER = 162
    NGA = 163
    NIU = 164
    NFK = 165
    PRK = 166
    MNP = 167
    NOR = 168
    OMN = 169
    PAK = 170
    PLW = 171
    PSE = 172
    PAN = 173
    PNG = 174
    PRY = 175
    PER = 176
    PHL = 177
    PCN = 178
    POL = 179
    PRT = 180
    PRI = 181
    QAT = 182
    KOS = 183
    REU = 184
    ROU = 185
    RUS = 186
    RWA = 187
    BLM = 188
    SHN = 189
    KNA = 190
    LCA = 191
    MAF = 192
    SPM = 193
    VCT = 194
    WSM = 195
    SMR = 196
    STP = 197
    SAU = 198
    SEN = 199
    SRB = 200
    SYC = 201
    SLE = 202
    SGP = 203
    SXM = 204
    SVK = 205
    SVN = 206
    SLB = 207
    SOM = 208
    ZAF = 209
    SGS = 210
    KOR = 211
    SSD = 212
    ESP = 213
    LKA = 214
    SDN = 215
    SUR = 216
    SJM = 217
    SWZ = 218
    SWE = 219
    CHE = 220
    SYR = 221
    TWN = 222
    TJK = 223
    TZA = 224
    THA = 225
    TLS = 226
    TGO = 227
    TKL = 228
    TON = 229
    TTO = 230
    TUN = 231
    TUR = 232
    TKM = 233
    TCA = 234
    TUV = 235
    UGA = 236
    UKR = 237
    ARE = 238
    GBR = 239
    USA = 240
    URY = 241
    UZB = 242
    VUT = 243
    VEN = 244
    VNM = 245
    WLF = 246
    ESH = 247
    YEM = 248
    ZMB = 249
    ZWE = 250
    EU = 251
    AS = 252
    AF = 253
    OC = 254
    NA = 256
    SA = 257
    SCO = 258
    ENG = 259
    WAL = 260
    NIR = 261
    WO = 263
    ANT = 266
    ZAR = 267


@dataclass
class SciSportsLeague:
    """SciSports League representation."""
    league_id: int
    league_name: str
    league_gender: str
    league_type: int
    league_nation_id: int
    league_age_group: str
    league_logo: str


@dataclass
class SciSportsMatch:
    """SciSports match representation."""
    match_id: int
    match_name: str
    league_id: int
    league_name: str
    league_nation: str
    season_id: int
    season_name: str
    match_day: int
    home_team_id: int
    home_team_name: str
    home_team_logo: str
    home_team_goals: int
    away_team_id: int
    away_team_name: str
    away_team_logo: str
    away_team_goals: int
    kick_off_date: str


@dataclass
class SciSportsSeason:
    """SciSports season representation."""
    league_id: int
    league_name: str
    league_gender: str
    league_nation_id: int
    league_logo: str
    season_id: int
    season_name: str
    season_group_id: int
    start_date: datetime
    end_date: datetime
    fixtures: List[SciSportsMatch]


@dataclass
class Transfer:
    """Dataclass representation of a transfer."""
    player_id: int
    player_name: str
    from_team_id: int
    from_team_name: str
    from_league_id: int
    from_league_name: str
    from_league_nation: str
    to_team_id: int
    to_team_name: str
    to_league_id: int
    to_league_name: str
    to_league_nation: str
    fee: int
    is_internal: bool
    is_end_loan: bool
    is_loan: bool
    market_value: int
    transfer_date: datetime
    contract_date: datetime


@dataclass
class SquadPlayer:
    """Dataclass representation of a player in a SciSports squad."""
    player_id: int
    team_id: int
    name: str
    age: Optional[int] = 0
    height: Optional[int] = 0
    birth_date: Optional[datetime] = datetime(1900, 1, 1)
    first_nationality: Optional[str] = ""
    second_nationality: Optional[str] = ""
    image_url: str = ""
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    football_name: Optional[str] = ""
    preferred_foot: str = ""
    first_position: str = ""
    second_position: str = ""
    third_position: str = ""
    contract_end: Optional[datetime] = datetime(1900, 1, 1)
    loan_end: Optional[datetime] = datetime(1900, 1, 1)
    on_loan: bool = False
    market_value: Optional[int] = 0
    etv_current: float = 0.0
    etv_dev: float = 0.0
    sciskill: float = 0.0
    sciskill_dev: float = 0.0
    potential: float = 0.0


@dataclass
class SciSportsTeam:
    """Dataclass representation of a SciSports team."""
    team_id: int
    name: str
    logo: str
    seasons: List[SciSportsSeason]
    transfers: List[Transfer]
    match_sheets: List[dict]
    squad: List[SquadPlayer]
    team_type: str
    age_group: int = 24
    match_team_players: List[dict] = field(init=False)
    match_team_attributes: List[dict] = field(init=False)

    def __post_init__(self):
        self.match_team_players = self._set_match_team_players()
        self.match_team_attributes = self._set_match_team_attributes()

    def _set_match_team_players(self) -> List[dict]:
        res = []
        for sheet in self.match_sheets:
            if sheet.get("homeTeam").get("id") == self.team_id:
                team = "homeTeam"
            else:
                team = "awayTeam"
            for plr in sheet.get(team).get("players"):
                res.append({
                    "match_id": sheet.get("id"),
                    "name": sheet.get("name"),
                    "kick_off_date": sheet.get("kickOffDate"),
                    "player_id": plr.get("player").get("id"),
                    "minutes_played": plr.get("minutesPlayed")
                })

        return res

    def _set_match_team_attributes(self) -> List[dict]:
        res = []
        for sheet in self.match_sheets:
            if sheet.get("homeTeam").get("id") == self.team_id:
                team = "homeTeam"
                side = "Home"
                other_side = "Away"
            else:
                team = "awayTeam"
                side = "Away"
                other_side = "Home"
            match_duration = 0
            for plr in sheet.get(team).get("players"):
                if plr.get("minutesPlayed") > match_duration:
                    match_duration = plr.get("minutesPlayed")

            res.append({
                "match_id": sheet.get("id"),
                "name": sheet.get("name"),
                "kick_off_date": sheet.get("kickOffDate"),
                "formation": sheet.get(f"formation{side}"),
                "goals_scored": sheet.get(team).get("goals"),
                "goals_conceded": sheet.get(team).get("goals"),
                "formation_faced": sheet.get(f"formation{other_side}"),
                "match_duration": match_duration
            })

        return res



class PositionLine(Enum):
    """Enum class with position line encodings.

    Attributes:
    ----------
    line_id: int
        Integer representation of SciSports PositionLine.
    line_name: str
        String representation of SciSports PositionLine.
    """
    UNKNOWN = (-2, 'Unknown')
    NOT_APPLICABLE = (-1, 'Not Applicable')
    GOALKEEPER = (0, 'Goalkeeper')
    DEFENDER = (1, 'Defender')
    MIDFIELDER = (2, 'Midfielder')
    ATTACKER = (3, 'Attacker')
    OTHER = (4, 'Other')

    def __init__(self, line_id: int, line_name: str):
        """Inits PositionLine with a line id and a line name."""
        self.line_id = line_id
        self.line_name = line_name


class PositionGroup(Enum):
    """Enum class with position group encodings.

    Attributes:
    ----------
    group_id: int
        Integer representation of SciSports PositionGroup.
    group_name: str
        String representation of SciSports PositionGroup.
    group_line: PositionLine
        The line category the position group belongs to.
    """
    UNKNOWN = (-2, 'Unknown', PositionLine.UNKNOWN)
    NOT_APPLICABLE = (-1, 'Not Applicable', PositionLine.NOT_APPLICABLE)
    GOALKEEPERS = (0, 'Goalkeepers', PositionLine.GOALKEEPER)
    FULL_BACKS = (1, 'Full backs', PositionLine.DEFENDER)
    CENTRE_BACKS = (2, 'Centre backs', PositionLine.DEFENDER)
    CENTRE_MIDFIELDERS = (3, 'Centre midfielders', PositionLine.MIDFIELDER)
    ATTACKING_MIDFIELDERS = (4, 'Attacking midfielders', PositionLine.MIDFIELDER)
    WINGERS = (5, 'Wingers', PositionLine.ATTACKER)
    CENTRE_FORWARDS = (6, 'Centre forwards', PositionLine.ATTACKER)
    OTHER = (7, 'Other', PositionLine.OTHER)

    def __init__(self, group_id: int, group_name: str, group_line: PositionLine):
        """Inits PositionGroup with a group id, a group name and a group line."""
        self.group_id = group_id
        self.group_name = group_name
        self.group_line = group_line


class Position(Enum):
    """Enum class with position encodings.

    Attributes:
    ----------
    position_id: int
        Integer representation of SciSports Position.
    position_name: str
        String representation of SciSports Position.
    position_group: PositionGroup
        The position group category the position group belongs to.
    """
    UNKNOWN = (-2, 'Unknown', PositionGroup.UNKNOWN)
    NOT_APPLICABLE = (-1, 'Not Applicable', PositionGroup.NOT_APPLICABLE)
    GOALKEEPER = (0, 'Goalkeeper', PositionGroup.GOALKEEPERS)
    LEFT_BACK = (1, 'Left back', PositionGroup.FULL_BACKS)
    RIGHT_BACK = (2, 'Right back', PositionGroup.FULL_BACKS)
    CENTRE_BACK = (3, 'Centre back', PositionGroup.CENTRE_BACKS)
    DEFENSIVE_MIDFIELDER = (4, 'Defensive midfield', PositionGroup.CENTRE_MIDFIELDERS)
    CENTRE_MIDFIELDER = (5, 'Centre midfield', PositionGroup.CENTRE_MIDFIELDERS)
    ATTACKING_MIDFIELDER = (6, 'Attacking midfield', PositionGroup.ATTACKING_MIDFIELDERS)
    LEFT_WING = (7, 'Left wing', PositionGroup.WINGERS)
    RIGHT_WING = (8, 'Right wing', PositionGroup.WINGERS)
    CENTRE_FORWARD = (9, 'Centre forward', PositionGroup.CENTRE_FORWARDS)
    OTHER = (10, 'Other', PositionGroup.OTHER)

    def __init__(self, position_id: int, position_name: str, position_group: PositionGroup):
        """Inits Position with a position id, a position name and a position group."""
        self.position_id = position_id
        self.position_name = position_name
        self.position_group = position_group