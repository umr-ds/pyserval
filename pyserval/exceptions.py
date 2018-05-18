# -*- coding: utf-8 -*-
"""
pyserval.exceptions
~~~~~~~~~~~~~~~~

Collected exceptions
"""


class NoSuchIdentityException(Exception):
    """Exception raised when trying to operate on a non-available identity

    This may either mean that the identity does not exists, or that it is not unlocked
    (https://github.com/servalproject/pyserval-dna/blob/development/doc/REST-API-Keyring.md#pin)
    There is no way to distinguish between these cases

    Args:
        sid (str): SID of the identity

    Attributes:
        sid (str): SID of the identity
    """

    def __init__(self, sid):
        self.sid = sid

    def __str__(self):
        return "No Identity with SID {} available".format(self.sid)


class EndpointNotImplementedException(Exception):
    """Exception raised when trying to use an endpoint which has not actually been implemented on the server side

    While in a perfect world there *SHOULD* be no need for this exception,
    serval does have documented endpoint which do not actually exist.
    We find this just ab baffling as you probably do...

    Args:
        endpoint (str): Name of the 'fictional' endpoint

    Attributes:
        endpoint (str): Name of the 'fictional' endpoint
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def __str__(self):
        return "The endpoint '{}' has not been implemented by the serval project."
