from .pushover import Pushover
from .slack import Slack

_VALID_SERVICES = None


def valid_services():
    """Returns the valid and configured services."""
    global _VALID_SERVICES

    if _VALID_SERVICES is None:
        _VALID_SERVICES = []

        if Pushover.verify_credentials():
            _VALID_SERVICES.append(Pushover())

        if Slack.verify_credentials():
            _VALID_SERVICES.append(Slack())

    return _VALID_SERVICES
