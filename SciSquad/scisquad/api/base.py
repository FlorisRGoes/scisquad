import json
import requests
from typing import List
from typing import Optional
from datetime import datetime
from datetime import timedelta
from abc import ABC
from abc import abstractmethod

from scisquad.api.domain import ApiCredentials
from scisquad.api.domain import StatusCode


class SciSportsAPI(ABC):
    """Base class for interaction with client-facing SciSports APIs.

    Parameters
    ----------
    credentials: ApiCredentials
        User credentials to pass for API authorization.
    scope: str
        API scope to authenticate against.

    Methods
    -------
    set_base_url() -> str
        Set the base url for the API.
    get_request() -> dict
        Make a GET request to the API.
    delete_request(endpoint: str)
        Make a DELETE request to the API.
    post_request( endpoint: str, data: dict)
        Make a POST request to the API.
    put_request(endpoint: str, data: dict)
        Make a PUT request to the API.

    See Also
    --------
    - Refer to downstream implementations in child classes for more information.
    - See https://developers.scisports.app/ for documentation.
    """
    def __init__(self, credentials: ApiCredentials, scope: str = "api recruitment performance", endpoint: str = ""):
        """Inits SciSportsAPI with credentials and a scope."""
        self._scope = scope
        self._base_url = self.set_base_url()
        self._base_url += endpoint
        self._token = self._authenticate(credentials)

    @abstractmethod
    def set_base_url(self) -> str:
        """Set the base url for the API."""
        raise NotImplementedError

    def _authenticate(self, credentials: ApiCredentials) -> str:
        """Get an access token from the identity endpoint."""
        resp = json.loads(requests.post(
            'https://identity.scisports.app/connect/token',
            {
                "grant_type": "password",
                "username": credentials.username,
                "password": credentials.password,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scope": self._scope
            }).text)

        return f'Bearer {resp.get("access_token")}'

    @staticmethod
    def _validate_response(response: requests.Response):
        """Check if a response is valid."""
        if response.status_code not in [
            StatusCode.SUCCESS.value,
            StatusCode.CREATED.value,
            StatusCode.ACCEPTED.value,
            StatusCode.NO_CONTENT.value,
        ]:
            raise Exception(f"{response.status_code}: {response.text}")
        else:
            print(f"Request completed: {response.status_code}")

    def get_request(self, endpoint: str = "", params: Optional[dict] = None) -> dict:
        """Make a GET request to the API.

        Parameters
        ---------
        endpoint: str = ""
            The endpoint to make a GET request to (i.e. v1/datasets).
        params: dict = None
            key, value pairs with request parameters (i.e. limit: 15, offset: 5).

        Returns
        -------
        dict
            json response from the API. Note that the function throws an exception in case of a response
            other than status code 20*.
        """
        resp = requests.get(
            f"{self._base_url}{endpoint}",
            headers={
                "Accept": "*/*",
                "Authorization": self._token
            },
            params=params
        )
        self._validate_response(resp)

        return resp.json()

    def post_request(self, endpoint: str, data: dict):
        """Make a POST request to the API."""
        resp = requests.post(
            f"{self._base_url}{endpoint}",
            data=json.dumps(data),
            headers={
                "Accept": "application/json-patch+json",
                "Content-Type": "application/json-patch+json",
                "Authorization": self._token
            }
        )
        self._validate_response(resp)

    def delete_request(self, endpoint: str):
        """Make a DELETE request to the API."""
        resp = requests.delete(
            f"{self._base_url}{endpoint}",
            headers={
                "Accept": "*/*",
                "Authorization": self._token
            }
        )
        self._validate_response(resp)

    def put_request(self, endpoint: str, data: dict):
        """Make a PUT request to the API."""
        resp = requests.put(
            f"{self._base_url}{endpoint}",
            data=json.dumps(data),
            headers={
                "Accept": "application/json-patch+json",
                "Content-Type": "application/json-patch+json",
                "Authorization": self._token
            }
        )
        self._validate_response(resp)


class RecruitmentAPI(SciSportsAPI):
    """Interface class for interaction with the SciSports Recruitment API.

    Parameters
    ----------
    credentials: ApiCredentials
        User credentials to pass for API authorization.

    Methods
    -------
    set_base_url() -> str
        Set the base url for the API.
    get_request() -> dict
        Make a GET request to the API.
    delete_request(endpoint: str)
        Make a DELETE request to the API.
    post_request( endpoint: str, data: dict)
        Make a POST request to the API.
    put_request(endpoint: str, data: dict)
        Make a PUT request to the API.
    get_season_groups(self, delta: timedelta = timedelta(days=365)) -> List[int]:
        Get all season groups starting between today and today - delta, and ending between today and today + delta.

    See Also
    --------
    - Refer to the upstream base class for more information.
    - See https://developers.scisports.app/recruitment-center for documentation.
    """
    def __init__(self, credentials: ApiCredentials, endpoint: str = ""):
        """Inits RecruitmentAPI with credentials."""
        super().__init__(credentials, "api recruitment", endpoint)

    def set_base_url(self) -> str:
        """Set the base url for the API."""
        return f"https://api-recruitment.scisports.app/api/"

    def get_season_groups(self, delta: timedelta = timedelta(days=365)) -> List[int]:
        """Get all season groups starting between today and today - delta, and ending between today and today + delta.

        Parameters
        ----------
        delta: timedelta = timedelta(days=365)
            Delta window to include in the search.

        Returns
        -------
        List[int]
            List of season group ids, can be used for a refined season search.
        """
        today = datetime.now()
        start_date = today - delta
        end_date = today + timedelta(365)
        payload = self.get_request(
            f"v2/Seasons/groups",
            params={
                "Limit": 1000,
                "StartDateBiggerThan": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "StartDateSmallerThan": today.strftime("%Y-%m-%dT%H:%M:%S"),
                "EndDateSmallerThan": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        )

        return [i.get('id') for i in payload.get('items')]


class PerformanceAPI(SciSportsAPI):
    """Interface class for interaction with the SciSports Performance API.

    Parameters
    ----------
    credentials: ApiCredentials
        User credentials to pass for API authorization.

    Methods
    -------
    set_base_url() -> str
        Set the base url for the API.
    get_request() -> dict
        Make a GET request to the API.
    delete_request(endpoint: str)
        Make a DELETE request to the API.
    post_request( endpoint: str, data: dict)
        Make a POST request to the API.
    put_request(endpoint: str, data: dict)
        Make a PUT request to the API.

    See Also
    --------
    - Refer to the upstream child class for more information.
    - See https://developers.scisports.app/performance-center for documentation.
    """
    def __init__(self, credentials: ApiCredentials, endpoint: str = ""):
        """Inits PerformanceAPI with credentials."""
        super().__init__(credentials, "api performance", endpoint)

    def set_base_url(self) -> str:
        """Set the base url for the API."""
        return f"https://api-performance.scisports.app/api/"
