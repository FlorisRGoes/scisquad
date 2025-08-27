from typing import Optional
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ApiCredentials:
    """Credentials dataclass with a default representation of API credentials.

    Extra Information:
    -----------------
    All fields are optional, as not every API requires all. If only a token is available, it is suggested to
    set the token under the client_secret field.
    """
    username: Optional[str]
    password: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]


class StatusCode(Enum):
    """HTML Status codes for API responses.

    See Also:
    --------
    https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
    """
    CONTINUE = 100
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    TIME_OUT = 408
    RATE_LIMIT = 429
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    TEMPORARILY_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
