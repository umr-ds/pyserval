# -*- coding: utf-8 -*-
"""
pyserval.lowlevel.keyring
~~~~~~~~~~~~~~~~

This module contains the means to interact with the serval keyring
"""

import sys

from pyserval.exceptions import EndpointNotImplementedException
from pyserval.lowlevel.connection import RestfulConnection

# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str


class Keyring:
    """Interface to access keyring-related endpoints of the REST-interface

    Args:
        connection (connection.RestfulConnection): Used for HTTP-communication
    """
    def __init__(self, connection):
        assert isinstance(connection, RestfulConnection), \
            "connection must be a RestfulConnection (from pyserval.lowlevel.connection)"

        self._connection = connection

    def _modify(self, sid, operation, params):
        """Utility method for the manipulation of identities

        Reduces boilerplate-code for common operations.

        Args:
            sid (str): SID of the identity to be manipulated
            operation (str): Kind of operation to be executed on the identity
            params (dict[str, Any]): Additional parameters for the operation

        Returns:
             requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, basestring), "sid must be a string"
        assert isinstance(operation, basestring), "operation must be a string"
        assert isinstance(params, dict), "params must be a dictionary"

        return self._connection.get(
            "/restful/keyring/{}/{}".format(sid, operation),
            params=params
        )

    def get_identities(self):
        """List of all currently unlocked identities

        Endpoint:
            GET /restful/keyring/identities.json

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get("/restful/keyring/identities.json")

    def get_identity(self, sid):
        """Get the details of a specific identity

        Endpoint:
            GET /restful/keyring/SID

        Args:
            sid (str): SID of the identity

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get("/restful/keyring/{}".format(sid))

    def add(self, pin="", did="", name=""):
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
        assert isinstance(pin, basestring), "pin must be a string"
        assert isinstance(did, basestring), "did must be a string"
        assert isinstance(name, basestring), "name must be a string"

        assert (len(did) > 4 or not len(did)), "did should be at least 5 digits"
        assert len(did.encode("utf-8")) < 32, "did may have at most 31 bytes (as UTF-8)"
        assert len(name.encode("utf-8")) < 64, "name may have at most 63 bytes (as UTF-8)"

        params = {}
        if pin:
            params['pin'] = pin
        if name:
            params['name'] = name
        if did:
            params['did'] = did

        return self._connection.post("/restful/keyring/add", params=params)

    def delete(self, sid):
        """Deletes an existing identity with a given SID

        Endpoint:
            DELETE /restful/keyring/SID

        Args:
            sid (str): SID of the identity to be deleted

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, basestring), "sid must be a string"

        return self._connection.delete("/restful/keyring/{}".format(sid))

    def lock(self, sid):
        """Locks an existing identity with a given SID

        Endpoint:
            PUT /restful/keyring/SID/lock

        Args:
            sid (str): SID of the identity to be locked

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, basestring), "sid must be a string"
        return self._connection.put("/restful/keyring/{}/lock".format(sid))

    def set(self, sid, did="", name=""):
        """Sets the DID and/or name of the unlocked identity that has the given SID

        Endpoint:
            GET /restful/keyring/SID/set

        Args:
            sid (str): SID of the identity to be updated (required)
            did (str): sets the DID (phone number)
                       String of 5-31 digits from 0123456789#*
            name (str): sets the name (optional)
                        String of at most 63 utf-8 bytes, may not include non-printable characters
                        may not start or end with a whitespace

        Note:
            If did/name is not set, then the field will be reset if currently set in the keyring

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
             requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, basestring), "sid must be a string"
        assert isinstance(did, basestring), "did must be a string"
        assert isinstance(name, basestring), "name must be a string"

        assert (len(did) > 4 or not len(did)), "did should be at least 5 digits"
        assert len(did.encode("utf-8")) < 32, "did may have at most 31 bytes (as UTF-8)"
        assert len(name.encode("utf-8")) < 64, "name may have at most 63 bytes (as UTF-8)"

        params = {}
        if did:
            params['did'] = did
        if name:
            params['name'] = name

        return self._modify(sid=sid, operation="set", params=params)
