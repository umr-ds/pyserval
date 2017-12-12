# -*- coding: utf-8 -*-
"""
pyserval.keyring
~~~~~~~~~~~~~~~~

This module contains the means to interact with the serval keyring
"""

from pyserval.util import unmarshall
from pyserval.connection import RestfulConnection


class ServalIdentity:
    """Representation of an indentity in the serval keyring

    Args:
        _keyring (Keyring): Keyring containing this identity
        sid (str): 'Serval ID' of this identity (required)
        identity(str): 'Serval Signing ID' of this identity (required)
        did (str): 'Dialled Identity' - phone number associated with this identity (optional)
        name (str): Human-readable name for this identity (optional)

    Attributes:
        sid (str): 'Serval ID' of this identity (required)
        identity(str): 'Serval Signing ID' of this identity (required)
        did (str): 'Dialled Identity' - phone number associated with this identity (optional)
        name (str): Human-readable name for this identity (optional)

    Note:
        Both 'sid' and 'identity' are public keys and may be shared
        Both 'did' and 'name' should be set via the 'set'-method
    """
    def __init__(self, _keyring, sid, identity, did=None, name=None):
        assert isinstance(_keyring, Keyring), "_keyring must be a Keyring"
        assert isinstance(sid, str), "sid must be a string"
        assert (did is None or isinstance(did, str)), "did must be a string"
        assert (name is None or isinstance(name, str)), "name must be a string"

        self._keyring = _keyring
        self.sid = sid
        self.did = did
        self.name = name
        self.identity = identity

    def __repr__(self):
        return "ServalIdentity(sid={}, did=\"{}\", name=\"{}\")".format(self.sid, self.did, self.name)

    def __str__(self):
        if self.name:
            return self.name
        if self.did:
            return "did:{}".format(self.did)
        else:
            return "{}*".format(self.sid[:16])

    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        return (self.sid == other.sid and
                self.did == other.did and
                self.name == other.name and
                self.identity == other.identity)

    def __ne__(self, other):
        return not self.__eq__(other)

    def refresh(self):
        """Refreshes Information for the Identity"""
        identities = self._keyring.get_identities()
        for identity in identities:
            if identity.sid == self.sid:
                self.__dict__.update(identity.__dict__)

    def set(self, did="", name=""):
        """Sets the DID and/or name of this identity

        Args:
            did (str): Sets the DID (phone number); must be a string of five or more digits from the set 123456789#0*
            name (str): Sets the name; must be non-empty

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        assert isinstance(did, str), "did must be a string"
        assert isinstance(name, str), "name must be a string"

        # make sure that we have the current state
        self.refresh()

        # serval will remove already set names when updating did and vice-versa.
        # So the name/did needs to be sent with the change request
        if not did and self.did:
            did = self.did
        if not name and self.name:
            name = self.name

        self._keyring.set(sid=self.sid, did=did, name=name)
        self.did = did
        self.name = name

    def remove(self):
        """Removes this Identity from the Keyring

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        self._keyring.remove(self.sid)

    def lock(self):
        """Locks this identity
        
        Raises:
             NoSuchIdentityException: If this identity is no longer available
        """
        self._keyring.lock(self.sid)


class Keyring:
    """Interface to access keyring-related endpoints of the REST-interface

    Args:
        connection (connection.RestfulConnection): Used for HTTP-communication
    """
    def __init__(self, connection):
        assert isinstance(connection, RestfulConnection), "connection must be a RestfulConnection (from pyserval.connection)"

        self._connection = connection

    def _modify(self, sid, operation, params):
        """Utility method for the manipulation of identities

        Reduces boilerplate-code for common operations.

        Args:
            sid (str): SID of the identity to be manipulated
            operation (str): Kind of operation to be executed on the identity
            params (dict[str, Any]): Additional parameters for the operation

        Raises:
             NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
             ServalIdentity: Object of the modified identity
        """
        assert isinstance(sid, str), "sid must be a string"
        assert isinstance(operation, str), "operation must be a string"
        assert isinstance(params, dict), "params must be a dictionary"

        result = self._connection.get("/restful/keyring/{}/{}".format(sid, operation), params=params)
        if result.status_code == 404:
            raise NoSuchIdentityException(sid)

        result_json = result.json()
        return ServalIdentity(self, **result_json["identity"])

    def get_identities(self):
        """List of all currently unlocked identities

        Endpoint:
            GET /restful/keyring/identities.json

        Returns:
            List[ServalIdentity]: All currently unlocked identities
        """
        identities_json = self._connection.get("/restful/keyring/identities.json").json()
        identities = unmarshall(json_table=identities_json, object_class=ServalIdentity, _keyring=self)
        return identities

    def get_identity(self, sid):
        """Gets the identity for a given sid

        Args:
            sid (str): SID of the requested identity

        Returns:
            ServalIdentity: Identity-information associated with the given SID

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available
        """
        assert isinstance(sid, str), "sid must be a string"

        identities = self.get_identities()
        for identity in identities:
            if identity.sid == sid:
                return identity

        raise NoSuchIdentityException(sid)

    def get_or_create(self, n):
        """Returns the first n unlocked identities in the keyring
        If there are fewer than n, new identities will be created

        Args:
            n (int): Number of identities

        Returns:
            List[ServalIdentity]: N first unlocked identities
        """
        assert isinstance(n, int), "n must be an integer"
        assert n >= 0, "n may not be negative"

        identities = self.get_identities()
        if len(identities) < n:
            new_identities = n - len(identities)
            for _ in range(new_identities):
                identities.append(self.add())
        return identities[:n]

    def add(self, pin=""):
        """Creates a new identity with a random SID

        Endpoint:
            GET /restful/keyring/add

        Args:
            pin (str): If set the new identity will be protected by that passphrase,
                       and the passphrase will be cached by Serval DNA so that the new identity is unlocked
                       May not include non-printable characters
                       NOTE:Even though 'pin' would imply numbers-only, it can be a arbitrary sting

        Returns:
            ServalIdentity: Object of the newly created identity
        """
        assert isinstance(pin, str), "pin must be a string"

        params = {}
        if pin:
            params['pin'] = pin

        request_json = self._connection.get("/restful/keyring/add", params=params).json()
        return ServalIdentity(self, **request_json["identity"])

    def remove(self, sid):
        """Removes an existing identity with a given SID

        Endpoint:
            GET /restful/keyring/SID/remove

        Args:
            sid (str): SID of the identity to be deleted

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
            ServalIdentity: Object of the deleted identity if successful
        """
        assert isinstance(sid, str), "sid must be a string"

        return self._modify(sid=sid, operation="remove", params={})

    def lock(self, sid):
        """Locks an existing identity with a given SID

        Endpoint:
            GET /restful/keyring/SID/lock

        Args:
            sid (str): SID of the identity to be locked

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
            ServalIdentity: Object of the locked identity if successful
        """
        assert isinstance(sid, str), "sid must be a string"

        return self._modify(sid=sid, operation="lock", params={})

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
             ServalIdentity: Object of the updated identity if successful
        """
        assert isinstance(sid, str), "sid must be a string"
        assert isinstance(did, str), "did must be a string"
        assert isinstance(name, str), "name must be a string"

        assert (len(did) > 4 or len(did) == 0), "did should be at least 5 digits"
        assert len(bytes(did, "utf-8")) < 32, "did may have at most 31 bytes (as UTF-8)"
        assert len(bytes(name, "utf-8")) < 64, "name may have at most 63 bytes (as UTF-8)"

        params = {}
        if did:
            params['did'] = did
        if name:
            params['name'] = name

        return self._modify(sid=sid, operation="set", params=params)


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
