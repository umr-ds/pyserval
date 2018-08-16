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
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def __str__(self):
        return "The endpoint '{}' has not been implemented by the serval project."


class JournalException(Exception):
    """Raised if attempting to updated a bundle using the wrong endpoint

    For normal bundles, use 'insert' and for journals use 'append'

    Args:
        is_journal (bool): True, if a journal was passed to the 'insert'-endpoint
                           False, if a normal bundle was passed to the 'append'-endpoint
    """
    def __init__(self, is_journal):
        self.is_journal = is_journal

    def __str__(self):
        if self.is_journal:
            return "Bundle is a journal; please use 'append'-endpoint"
        else:
            return "Bundle is not a journal; please use 'insert'-endpoint"


class EmptyPayloadException(Exception):
    """Raised if a journal with empty payload is passed to the 'append'-endpoint"""
    def __str__(self):
        return "Journals require a payload"


class NoSuchBundleException(Exception):
    """Raised when attempting to get the info for a non-existing bundle

    Args:
        bid (str): Attempted BID
    """
    def __init__(self, bid):
        self.bid = bid

    def __str__(self):
        return "No Bundle with BID {} available".format(self.bid)
