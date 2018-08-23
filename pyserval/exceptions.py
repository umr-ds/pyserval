# -*- coding: utf-8 -*-
"""
pyserval.exceptions
~~~~~~~~~~~~~~~~

Collected exceptions
"""

import sys

from requests.models import Response

# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str


class IdentityNotFoundError(Exception):
    """Error raised when trying to operate on a non-available identity

    This may either mean that the identity does not exists, or that it is not unlocked
    (https://github.com/servalproject/pyserval-dna/blob/development/doc/REST-API-Keyring.md#pin)
    There is no way to distinguish between these cases

    Args:
        sid (str): SID of the identity
    """

    def __init__(self, sid):
        assert isinstance(sid, basestring)
        self.sid = sid

    def __str__(self):
        return "No Identity with SID {} available".format(self.sid)


class JournalError(Exception):
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


class ManifestNotFoundError(Exception):
    """Raised when attempting to get the info for a non-existing bundle

    Args:
        bid (str): Attempted BID
    """
    def __init__(self, bid):
        assert isinstance(bid, basestring)
        self.bid = bid

    def __str__(self):
        return "No Manifest for BID {} available".format(self.bid)


class PayloadNotFoundError(Exception):
    """Raised if attempting to get a bundle's payload when no such payload exists

    Args:
        bid (str): Bundle ID of the bundle
    """
    def __init__(self, bid):
        assert isinstance(bid, basestring)
        self.bid = bid

    def __str__(self):
        return "Bundle {} appears to have no payload".format(self.bid)


class DecryptionError(Exception):
    """Raised if trying to decrypt a bundle's payload without having the necessary key

    Args:
        bid (str): Bundle ID of the bundle
    """
    def __init__(self, bid):
        assert isinstance(bid, basestring)
        self.bid = bid

    def __str__(self):
        return "Can't decrypt bundle payload, BID: {}".format(self.bid)


class UnknownRhizomeStatusError(Exception):
    """Raised for rhizome responses with an unknown combination of HTTP/Bundle/Payload status

    Args:
        serval_response (requests.models.Response): Response returned by the serval-server

    Attributes:
        http_status (int): HTTP status code of the response
        bundle_status (int): bundle status code of the response
        payload_status (int): payload status of the response

    Note:
        For documentation on the rhizome specific status codes, see
        https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md#bundle-status-code
        https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md#payload-status-code
    """
    def __init__(self, serval_response):
        assert isinstance(serval_response, Response)

        self.http_status = serval_response.status_code
        self.bundle_status = serval_response.headers.get("Serval-Rhizome-Result-Bundle-Status-Code")
        self.payload_status = serval_response.headers.get("Serval-Rhizome-Result-Payload-Status-Code")

    def __str__(self):
        return "Unknown status code combination (HTTP: {}, Bundle: {}, Payload: {})".format(
            self.http_status,
            self.bundle_status,
            self.payload_status
        )


class DuplicateBundleException(Exception):
    """Rhizome performs 'duplicate detection' during the insert process

    When you try to insert a bundle without providing an ID but with the same payload, service, name,
    sender, recipient as an existing bundle then this is considered a duplicate.
    In this case, serval will return status 200 for your request but will not modify any data for that bundle

    Args:
        bid (str): BID of the bundle which is being duplicated
    """
    def __init__(self, bid):
        assert isinstance(bid, basestring)
        self.bid = bid

    def __str__(self):
        return "Bundle is duplicate of BID {}".format(self.bid)
