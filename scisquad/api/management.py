from typing import Optional
from typing import List

from scisquad.api.base import RecruitmentAPI
from scisquad.api.domain import ApiCredentials


class CollaborationAPI(RecruitmentAPI):
    """API interface for interaction with RC Shortlists, Labels & Comments.

    Extra information
    ----------------
    This class serves as the API interface for staff collaboration via the Recruitment Center, and allows for
    (automated) creation and management of shortlists, labels and comments. Within the squad management context,
    the data-analyst will typically use the guided search to find players and evaluate decisions, after which
    the output is presented to the front end of the organization via collaboration tools in the Recruitment Center.

    Parameters
    ----------
    credentials: ApiCredentials
        User credentials to pass for API authorization.
    account_id: Optional[str] = None
        Client account id.

    Methods
    -------
    get_shortlist(name: str, user_id: str) -> Optional[str]:
        Get a shortlist id based on a name, will return void if not found.
    delete_shortlist(shortlist_id: str):
        Delete a shortlist based on a shortlist id.
    add_shortlist(user_id: str, name: str, private: bool = True):
        Create a new shortlist for a given user.
    add_players_to_shortlist(user_id: str, shortlist_name: str, players: List[int]):
        Update a shortlist with a list of players.
    set_comment(comment: str, plr_id: int) -> Optional[str]:
        Set a comment to a player.
    get_label(name: str) -> Optional[str]:
        Get a label id based on a name, will return void if not found.
    delete_label(label_name: str):
        Delete a label based on a label id.
    add_label(name: str):
        Create a new label with a given name.
    put_player_labels(label_name: str, players: List[int]):
        Assign a label to a list of players.

    See also
    --------
    https://developers.scisports.app/recruitment-center/api-reference
    """
    def __init__(self, credentials: ApiCredentials, account_id: Optional[str] = None):
        """Inits CollaborationAPI with API credentials."""
        super().__init__(credentials)
        self._account_id = account_id

    def get_shortlist(self, name: str, user_id: str) -> Optional[str]:
        """Get a shortlist id based on a name, will return void if not found."""
        payload = self.get_request(
            endpoint="v1/shortlists",
            params={
                "Limit": 100,
                "Name": name,
                "UserId": user_id,
                "includePlayers": False
            }
        )
        if payload.get("total") == 0:
            return None
        else:
            return payload.get("items")[0].get("id")

    def delete_shortlist(self, shortlist_id: str):
        """Delete a shortlist based on a shortlist id."""
        print(f"Deleting shortlist: {shortlist_id} from account: {self._account_id} ...")
        self.delete_request(f"v1/shortlists/{shortlist_id}?accountId={self._account_id}")

    def add_shortlist(self, user_id: str, shortlist_name: str, private: bool = True):
        """Create a new shortlist for a given user.

        Parameters
        ----------
        user_id: str
            Owner of the shortlist.
        shortlist_name: str
            Title of the shortlist.
        private: bool = True
            Sets the permissions of other users within the account. When set to True,
            only the owner can view/edit the shortlist.
        """
        print(f"Creating new shortlist: {shortlist_name} for user: {user_id}")
        existing_shortlist = self.get_shortlist(shortlist_name, user_id)
        if existing_shortlist is not None:
            self.delete_shortlist(existing_shortlist)
        payload = {
            "userId": user_id,
            "name": shortlist_name,
            "isPrivateViewing": private,
            "isPrivateEditing": private,
            "players": []
        }
        self.post_request(
            endpoint=f"v1/shortlists?accountId={self._account_id}",
            data=payload,
        )

    def add_players_to_shortlist(self, user_id: str, shortlist_name: str, players: List[int]):
        """Update a shortlist with a list of players.

        Parameters
        ----------
        user_id: str
            User id of the user adding the players to the shortlist.
        shortlist_name: str
            Title of the shortlist.
        players: List[int]
            Entity ids of the players to add to the shortlist.
        """
        shortlist_id = self.get_shortlist(shortlist_name, user_id)
        if shortlist_id is None:
            raise ValueError(f"Shortlist {shortlist_name} does not exist.")
        print(f"Adding {len(players)} players to shortlist: {shortlist_id} on account {self._account_id}...")
        self.post_request(
            endpoint=f"v1/shortlists/{shortlist_id}/players",
            data={"playerIds": players},
        )

    def set_comment(self, comment: str, plr_id: int) -> Optional[str]:
        """Set a comment to a player.

        Parameters
        ---------
        comment: str
            Text to comment on the player.
        plr_id: int
            Entity id of the player to comment on.
        """
        self.post_request(
            endpoint="v1/comments?context=male",
            data={"text": comment, "referenceId": plr_id},
        )

    def get_label(self, name: str) -> Optional[str]:
        """Get a label id based on a name, will return void if not found."""
        payload = self.get_request(
            endpoint="v1/Labels",
            params={
                "Limit": 100,
                "Name": name,
                "AccountId": self._account_id,
            }
        )
        if payload.get("total") == 0:
            return None
        else:
            return payload.get("items")[0].get("id")

    def delete_label(self, label_name: str):
        """Delete a label based on label name."""
        print(f"Deleting label: {label_name} from account: {self._account_id} ...")
        label_id = self.get_label(label_name)
        if label_id is not None:
            self.delete_request(f"v1/Labels/{label_id}")

    def add_label(self, name: str):
        """Create a new label with a given name."""
        print(f"Creating label if it does not exist yet: {name}")
        existing = self.get_label(name)
        if existing is not None:
            self.delete_label(existing)
        payload = {
            "name": name,
            "color": "blue-700",
            "accountId": self._account_id,
        }
        self.post_request(
            endpoint=f"v1/labels",
            data=payload,
        )

    def put_player_labels(self, label_name: str, players: List[int]):
        """Assign a label to a list of players.

        Parameters
        ----------
        label_name: str
            Name of the label, used to get the label id.
        players: List[int]
            List of entity ids to assign the label to.
        """
        label_id = self.get_label(label_name)
        if label_id is None:
            raise ValueError(f"Label '{label_name}' does not exist.")
        print(f"Adding label {label_name} for {len(players)} players:...")
        for plr in players:
            self.put_request(
                endpoint=f"v2/Players/{plr}/labels",
                data={"labelIds": [label_id]},
            )
