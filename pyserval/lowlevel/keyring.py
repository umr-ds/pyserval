"""
pyserval.lowlevel.keyring
~~~~~~~~~~~~~~~~

This module contains the means to interact with the serval keyring
"""

from pyserval.lowlevel.connection import RestfulConnection
from requests.models import Response
from typing import Any, Dict, Union


class LowLevelKeyring:
    """Interface to access keyring-related endpoints of the REST-interface

    Args:
        connection (connection.RestfulConnection): Used for HTTP-communication
    """

    def __init__(self, connection: RestfulConnection) -> None:
        assert isinstance(
            connection, RestfulConnection
        ), "connection must be a RestfulConnection (from pyserval.lowlevel.connection)"

        self._connection = connection

    def _modify(self, sid: str, operation: str, params: Dict[str, Any]) -> Response:
        """Utility method for the manipulation of identities

        Reduces boilerplate-code for common operations.

        Args:
            sid (str): SID of the identity to be manipulated
            operation (str): Kind of operation to be executed on the identity
            params (Dict[str, Any]): Additional parameters for the operation

        Returns:
             requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, str), "sid must be a string"
        assert isinstance(operation, str), "operation must be a string"
        assert isinstance(params, dict), "params must be a dictionary"

        return self._connection.get(
            f"/restful/keyring/{sid}/{operation}", params=params
        )

    def get_identities(self, pin: str = "") -> Response:
        """List of all currently unlocked identities

        Endpoint:
            GET /restful/keyring/identities.json

        Args:
            pin (str): Passphrase to unlock identity prior to lookup

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(pin, str), "pin must be a string"

        params = {}
        if pin:
            params["pin"] = pin

        return self._connection.get("/restful/keyring/identities.json", params=params)

    def get_identity(self, sid: str, pin: str = "") -> Response:
        """Get the details of a specific identity

        Endpoint:
            GET /restful/keyring/SID

        Args:
            sid (str): SID of the identity
            pin (str): Passphrase to unlock identity prior to lookup

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(pin, str), "pin must be a string"

        params = {}
        if pin:
            params["pin"] = pin

        return self._connection.get(f"/restful/keyring/{sid}", params=params)

    def add(self, pin: str = "", did: str = "", name: str = "") -> Response:
        """Creates a new identity with a random SID

        Endpoint:
            POST /restful/keyring/add

        Args:
            pin (str): If set the new identity will be protected by that passphrase,
                       and the passphrase will be cached by Serval DNA
                       so that the new identity is unlocked

                       May not include non-printable characters
                       NOTE:Even though 'pin' would imply numbers-only, it can be a arbitrary sting
            did (str): sets the DID (phone number)
                       String of 5-31 digits from 0123456789#*
            name (str): sets the name (optional)
                        String of at most 63 utf-8 bytes, may not include non-printable characters
                        may not start or end with a whitespace

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(pin, str), "pin must be a string"
        assert isinstance(did, str), "did must be a string"
        assert isinstance(name, str), "name must be a string"

        assert len(did) > 4 or not len(did), "did should be at least 5 digits"
        assert len(did.encode("utf-8")) < 32, "did may have at most 31 bytes (as UTF-8)"
        assert (
            len(name.encode("utf-8")) < 64
        ), "name may have at most 63 bytes (as UTF-8)"

        params = {}
        if pin:
            params["pin"] = pin
        if name:
            params["name"] = name
        if did:
            params["did"] = did

        return self._connection.post("/restful/keyring/add", params=params)

    def delete(self, sid: str, pin: str = "") -> Response:
        """Deletes an existing identity with a given SID

        Endpoint:
            DELETE /restful/keyring/SID

        Args:
            sid (str): SID of the identity to be deleted
            pin (str): Passphrase to unlock identity prior to deletion

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, str), "sid must be a string"
        assert isinstance(pin, str), "pin must be a string"

        params = {}
        if pin:
            params["pin"] = pin

        return self._connection.delete(f"/restful/keyring/{sid}", params=params)

    def lock(self, sid: str) -> Response:
        """Locks an existing identity with a given SID

        Endpoint:
            PUT /restful/keyring/SID/lock

        Args:
            sid (str): SID of the identity to be locked

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, str), "sid must be a string"
        return self._connection.put(f"/restful/keyring/{sid}/lock")

    def set(
        self,
        sid: str,
        pin: str = "",
        did: Union[str, None] = None,
        name: Union[str, None] = None,
    ) -> Response:
        """Sets the DID and/or name of the unlocked identity that has the given SID

        Endpoint:
            GET /restful/keyring/SID/set

        Args:
            sid (str): SID of the identity to be updated (required)
            pin (str): Passphrase to unlock identity prior to modification
            did (Union[str, None]): sets the DID (phone number)
                       String of 5-31 digits from 0123456789#*
            name (Union[str, None]): sets the name (optional)
                        String of at most 63 utf-8 bytes, may not include non-printable characters
                        may not start or end with a whitespace

        Returns:
             requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, str), "sid must be a string"
        assert isinstance(sid, str), "sid must be a string"
        assert did is None or isinstance(did, str), "did must be a string"
        if did is not None:
            assert len(did) > 4 or not len(did), "did should be at least 5 digits"
            assert (
                len(did.encode("utf-8")) < 32
            ), "did may have at most 31 bytes (as UTF-8)"

        assert name is None or isinstance(name, str), "name must be a string"
        if name is not None:
            assert (
                len(name.encode("utf-8")) < 64
            ), "name may have at most 63 bytes (as UTF-8)"

        params = {}
        if pin:
            params["pin"] = pin
        if did is not None:
            params["did"] = did
        if name is not None:
            params["name"] = name

        return self._connection.patch(f"/restful/keyring/{sid}", params=params)
