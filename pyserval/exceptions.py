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


class RhizomeHTTPStatusError(Exception):
    """Raised for rhizome responses with an unknown HTTP status

    Args:
        serval_response (requests.models.Response): Response returned by the serval-server

    Attributes:
        http_status (int): HTTP status code of the response
        headers (dict)
    """

    def __init__(self, serval_response):
        assert isinstance(serval_response, Response)

        self.http_status = serval_response.status_code
        self.response = serval_response.json()

    def __str__(self):
        return "Unknown HTTP status code {}, hint: {}".format(
            self.http_status, self.response
        )


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
        self.bundle_status = serval_response.headers.get(
            "Serval-Rhizome-Result-Bundle-Status-Code"
        )
        self.payload_status = serval_response.headers.get(
            "Serval-Rhizome-Result-Payload-Status-Code"
        )

    def __str__(self):
        return "Unknown status code combination (HTTP: {}, Bundle: {}, Payload: {})".format(
            self.http_status, self.bundle_status, self.payload_status
        )


class DuplicateBundleException(Exception):
    """Rhizome performs 'duplicate detection' during the insert process

    When you try to insert a bundle without providing an ID but with the same payload, service, name,
    sender, recipient as an existing bundle then this is considered a duplicate.
    The same is true if an id is supplied but the version field in the new manifest is not greater
    In this case, serval will return status 200 for your request but will not modify any data for that bundle

    Args:
        bid (str): BID of the bundle which is being duplicated
    """

    def __init__(self, bid):
        assert isinstance(bid, basestring)
        self.bid = bid

    def __str__(self):
        return "Bundle is duplicate of BID {}".format(self.bid)


class RhizomeInsertionError(Exception):
    """Raised if a call to the 'insert' or 'append' endpoint fails

    Args:
        http_status (int): HTTP-status-code of the reply
        bundle_status (int): Status code for the failure
        bundle_message (str): Human readable explanation of the failure
        response_text (str): Text of response returned by the server - since we can't always rely on
                             the first two arguments being provided
    """

    def __init__(self, http_status, bundle_status, bundle_message, response_text):
        self.http_status = http_status
        self.status = bundle_status
        self.message = bundle_message
        self.response_text = response_text

    def __str__(self):
        return "Insertion failed with: HTTP-code: {}, bundle-code {}, bundle-Message: {}, server-response: {}".format(
            self.http_status, self.status, self.message, self.response_text
        )


class InvalidManifestError(Exception):
    """Raised by the manifest's is_valid-method if the manifest is invalid

    Args:
        key (str): invalid key
        value (str): invalid value
        reason (str): Human readable explanation of what is wrong
    """

    def __init__(self, key, value, reason):
        assert isinstance(key, basestring)
        assert isinstance(value, basestring)
        assert isinstance(reason, basestring)

        self.key = key
        self.value = value
        self.reason = reason

    def __str__(self):
        return "Invalid Manifest field: ({}: {}), Reason: {}".format(
            self.key, self.value, self.reason
        )


class InvalidTokenError(Exception):
    """Raised by the rhizome get_bundlelist_newsince method, if the token is invalid

    Args:
        token (str): invalid token
        reason (str): Human readable explanation of what is wrong
    """

    def __init__(self, token, reason):
        assert isinstance(reason, basestring)

        self.token = token
        self.reason = reason

    def __str__(self):
        return "Invalid token: {}, Reason: {}".format(self.token, self.reason)
