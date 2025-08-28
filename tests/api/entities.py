import os

from dotenv import load_dotenv

from scisquad.api.domain import ApiCredentials
from scisquad.api.entities import LeaguesAPI
from scisquad.api.entities import TeamsAPI
from scisquad.api.management import CollaborationAPI
from scisquad.model.entities import LeagueType
from scisquad.model.entities import Gender
from scisquad.model.entities import Nations
from scisquad.insights.squad import SquadTransferInsights
from scisquad.insights.squad import SquadPerformanceInsights
from scisquad.api.player_search import GuidedSearchAPI
from scisquad.insights.league import SeasonTeamInsights


load_dotenv()

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
LA = SeasonTeamInsights(seasons[0], TeamsAPI(credentials))
df_performance_insights, df_inbound_transfer_insights, df_outbound_transfer_insights, df_revenue_insights = LA.analyze_teams()

'''
tAPI = TeamsAPI(credentials)
ajax = tAPI.get_team(1099)

transfer_insights = SquadTransferInsights(ajax).analyze_inbound()
performance_insights = SquadPerformanceInsights(ajax).get_team_performance_insights()

search = GuidedSearchAPI(credentials)
search.set_league_selection(list(transfer_insights.get("inbound_market_shares").keys())[:10])
recommendations = search.find_recommended_players(benchmark=70.6, budget=30000000)
'''

# cAPI = CollaborationAPI(credentials, os.getenv("SCISPORTS_ACCOUNT"))
