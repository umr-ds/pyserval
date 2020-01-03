"""
pyserval.exceptions
~~~~~~~~~~~~~~~~

Collected exceptions
"""

from requests.models import Response


class MalformedRequestError(Exception):
    """General error when serval server response to a malformed request"""


class IdentityNotFoundError(Exception):
    """Error raised when trying to operate on a non-available identity

    This may either mean that the identity does not exists, or that it is not unlocked
    (https://github.com/servalproject/pyserval-dna/blob/development/doc/REST-API-Keyring.md#pin)
    There is no way to distinguish between these cases

    Args:
        sid (str): SID of the identity
    """

    def __init__(self, sid: str) -> None:
        assert isinstance(sid, str)
        self.sid = sid

    def __str__(self) -> str:
        return f"No Identity with SID {self.sid} available"


class JournalError(Exception):
    """Raised if attempting to updated a bundle using the wrong endpoint

    For normal bundles, use 'insert' and for journals use 'append'

    Args:
        is_journal (bool): True, if a journal was passed to the 'insert'-endpoint
                           False, if a normal bundle was passed to the 'append'-endpoint
    """

    def __init__(self, is_journal: bool) -> None:
        assert isinstance(is_journal, bool)
        self.is_journal = is_journal

    def __str__(self) -> str:
        if self.is_journal:
            return "Bundle is a journal; please use 'append'-endpoint"
        else:
            return "Bundle is not a journal; please use 'insert'-endpoint"


class ManifestNotFoundError(Exception):
    """Raised when attempting to get the info for a non-existing bundle

    Args:
        bid (str): Attempted BID
    """

    def __init__(self, bid: str) -> None:
        assert isinstance(bid, str)
        self.bid = bid

    def __str__(self) -> str:
        return f"No Manifest for BID {self.bid} available"


class PayloadNotFoundError(Exception):
    """Raised if attempting to get a bundle's payload when no such payload exists

    Args:
        bid (str): Bundle ID of the bundle
    """

    def __init__(self, bid: str) -> None:
        assert isinstance(bid, str)
        self.bid = bid

    def __str__(self) -> str:
        return f"Bundle {self.bid} appears to have no payload"


class DecryptionError(Exception):
    """Raised if trying to decrypt a bundle's payload without having the necessary key

    Args:
        bid (str): Bundle ID of the bundle
    """

    def __init__(self, bid: str) -> None:
        assert isinstance(bid, str)
        self.bid = bid

    def __str__(self) -> str:
        return f"Can't decrypt bundle payload, BID: {self.bid}"


class RhizomeHTTPStatusError(Exception):
    """Raised for rhizome responses with an unknown HTTP status

    Args:
        serval_response (requests.models.Response): Response returned by the serval-server

    Attributes:
        http_status (int): HTTP status code of the response
    """

    def __init__(self, serval_response: Response) -> None:
        assert isinstance(serval_response, Response)

        self.http_status: int = serval_response.status_code
        self.response: str = serval_response.json()

    def __str__(self) -> str:
        return f"Unknown HTTP status code {self.http_status}, hint: {self.response}"


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

    def __init__(self, serval_response: Response) -> None:
        assert isinstance(serval_response, Response)

        self.http_status: int = serval_response.status_code
        self.bundle_status: int = serval_response.headers.get(
            "Serval-Rhizome-Result-Bundle-Status-Code"
        )
        self.payload_status: int = serval_response.headers.get(
            "Serval-Rhizome-Result-Payload-Status-Code"
        )

    def __str__(self) -> str:
        return f"Unknown status code combination (HTTP: {self.http_status}, Bundle: {self.bundle_status}, Payload: {self.payload_status})"


class DuplicateBundleException(Exception):
    """Rhizome performs 'duplicate detection' during the insert process

    When you try to insert a bundle without providing an ID but with the same payload, service, name,
    sender, recipient as an existing bundle then this is considered a duplicate.
    The same is true if an id is supplied but the version field in the new manifest is not greater
    In this case, serval will return status 200 for your request but will not modify any data for that bundle

    Args:
        bid (str): BID of the bundle which is being duplicated
    """

    def __init__(self, bid: str) -> None:
        assert isinstance(bid, str)
        self.bid = bid

    def __str__(self) -> str:
        return f"Bundle is duplicate of BID {self.bid}"


class RhizomeInsertionError(Exception):
    """Raised if a call to the 'insert' or 'append' endpoint fails

    Args:
        http_status (int): HTTP-status-code of the reply
        bundle_status (int): Status code for the failure
        bundle_message (str): Human readable explanation of the failure
        response_text (str): Text of response returned by the server - since we can't always rely on
                             the first two arguments being provided
    """

    def __init__(
        self,
        http_status: int,
        bundle_status: int,
        bundle_message: str,
        response_text: str,
    ) -> None:
        self.http_status = http_status
        self.status = bundle_status
        self.message = bundle_message
        self.response_text = response_text

    def __str__(self) -> str:
        return f"Insertion failed with: HTTP-code: {self.http_status}, bundle-code {self.status}, bundle-Message: {self.message}, server-response: {self.response_text}"


class InvalidManifestError(Exception):
    """Raised by the manifest's is_valid-method if the manifest is invalid

    Args:
        key (str): invalid key
        value (str): invalid value
        reason (str): Human readable explanation of what is wrong
    """

    def __init__(self, key: str, value: str, reason: str) -> None:
        assert isinstance(key, str)
        assert isinstance(value, str)
        assert isinstance(reason, str)

        self.key = key
        self.value = value
        self.reason = reason

    def __str__(self) -> str:
        return (
            f"Invalid Manifest field: ({self.key}: {self.value}), Reason: {self.reason}"
        )


class InvalidTokenError(Exception):
    """Raised by the rhizome get_bundlelist_newsince method, if the token is invalid

    Args:
        token (str): invalid token
        reason (str): Human readable explanation of what is wrong
    """

    def __init__(self, token: str, reason: str) -> None:
        assert isinstance(reason, str)

        self.token = token
        self.reason = reason

    def __str__(self) -> str:
        return f"Invalid token: {self.token}, Reason: {self.reason}"


class ConversationNotFoundError(Exception):
    """Raised if trying to get a conversation which does not exist

    Args:
        sid (str)
        other_sid (str)
    """

    def __init__(self, sid: str, other_sid: str) -> None:
        assert isinstance(sid, str)
        assert isinstance(other_sid, str)

        self.sid = sid
        self.other_sid = other_sid

    def __str__(self) -> str:
        return f"No conversation between {self.sid} and {self.other_sid}"


class UnauthorizedError(Exception):
    """Raised if username/password is wrong"""

    def __str__(self) -> str:
        return "Server returned unauthorized-error"
