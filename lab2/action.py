from enum import Enum


class TransportAim(Enum):
    GET_SESSION = 1
    SESSION_PROPOSAL = 2
    APP_REQUEST = 3


class AppVerb(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
