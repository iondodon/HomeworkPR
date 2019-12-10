from enum import Enum


class TransportAim(Enum):
    GET_SESSION = 1
    SESSION_PROPOSAL = 2
    APP_REQUEST = 3
    APP_RESPONSE = 4
    CORRUPTED = 5
    OK = 6
    CLOSE = 7


class AppVerb(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
    ERR = 5
    OK = 6
    CLOSE = 7
