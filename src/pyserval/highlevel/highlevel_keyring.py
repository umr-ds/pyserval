# -*- coding: utf-8 -*-
"""
pyserval.highlevel.gighlevel_keyring
~~~~~~~~~~~~~~~~

High level API for accessing the serval keyring
"""

import sys

from pyserval.exceptions import NoSuchIdentityException
from pyserval.lowlevel.keyring import Keyring
from pyserval.lowlevel.util import unmarshall


# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str


class ServalIdentity:
    """Representation of an identity in the serval keyring

    Args:
        _keyring (HighLevelKeyring): Keyring containing this identity
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
        assert isinstance(_keyring, HighLevelKeyring), "_keyring must be a HighLevelKeyring"
        assert isinstance(sid, basestring), "sid must be a string"
        assert (did is None or isinstance(did, basestring)), "did must be a string"
        assert (name is None or isinstance(name, basestring)), "name must be a string"

        self._keyring = _keyring
        self.sid = sid
        self.did = did
        self.name = name
        self.identity = identity

    def __repr__(self):
        return "ServalIdentity(sid={}, did=\"{}\", name=\"{}\")".format(
            self.sid,
            self.did,
            self.name
        )

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
            did (str): Sets the DID (phone number);
                       must be a string of five or more digits from the set 123456789#0*
            name (str): Sets the name; must be non-empty

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        assert isinstance(did, basestring), "did must be a string"
        assert isinstance(name, basestring), "name must be a string"

        # make sure that we have the current state
        self.refresh()

        # serval will remove already set names when updating did and vice-versa.
        # So the name/did needs to be sent with the change request
        if not did and self.did:
            did = self.did
        if not name and self.name:
            name = self.name

        self._keyring.set(identity=self, did=did, name=name)
        self.did = did
        self.name = name

    def delete(self):
        """Removes this Identity from the Keyring

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        self._keyring.delete(identity=self)

    def lock(self):
        """Locks this identity - can be unlocked again with its pin

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        self._keyring.lock(identity=self)


class HighLevelKeyring:
    def __init__(self, connection):
        self.low_level_keyring = Keyring(connection)

    def add(self, pin="", did="", name=""):
        """Creates a new identity with a random SID

        Endpoint:
            GET /restful/keyring/add

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
            ServalIdentity: Object of the newly created identity
        """
        serval_reply = self.low_level_keyring.add(pin=pin, did=did, name=name)
        reply_json = serval_reply.json()
        return ServalIdentity(self, **reply_json["identity"])

    def get_identities(self):
        """List of all currently unlocked identities

        Endpoint:
            GET /restful/keyring/identities.json

        Returns:
            List[ServalIdentity]: All currently unlocked identities
        """
        serval_response = self.low_level_keyring.get_identities()
        response_json = serval_response.json()

        identities = unmarshall(
            json_table=response_json,
            object_class=ServalIdentity,
            _keyring=self)

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
        assert isinstance(sid, basestring), "sid must be a string"

        serval_response = self.low_level_keyring.get_identity(sid)

        if serval_response.status_code == 404:
            raise NoSuchIdentityException(sid)

        response_json = serval_response.json()

        return ServalIdentity(self, **response_json["identity"])

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

    def default_identity(self):
        """Returns the first unlocked identity (or creates one, if none exist)

        Returns:
            ServalIdentity: First unlocked (or created) identity
        """
        return self.get_or_create(1)[0]

    def delete(self, identity):
        """Removes an existing identity

        Endpoint:
            GET /restful/keyring/SID/remove

        Args:
            identity (ServalIdentity): Identity to be removed

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
            ServalIdentity: Object of the deleted identity if successful
        """
        serval_response = self.low_level_keyring.delete(identity.sid)

        if serval_response.status_code == 404:
            raise NoSuchIdentityException(identity.sid)

        reply_json = serval_response.json()
        return ServalIdentity(self, **reply_json["identity"])

    def set(self, identity, did="", name=""):
        """Sets the DID and/or name of an unlocked identity

        Endpoint:
            GET /restful/keyring/SID/set

        Args:
            identity (ServalIdentity): Identity to be updated (required)
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
        serval_reply = self.low_level_keyring.set(identity.sid, did, name)
        reply_json = serval_reply.json()
        return ServalIdentity(self, **reply_json["identity"])

    def lock(self, identity):
        """Locks an identity - you will need the pin to unlock it again

        NOTE: This endpoint does not work as documented - it does not return the locked identity's details on success

        Endpoint:
            PUT /restful/keyring/SID/lock

        Args:
            identity (ServalIdentity): Identity to be locked

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available
        """
        serval_response = self.low_level_keyring.lock(identity.sid)

        if serval_response.status_code == 404:
            raise NoSuchIdentityException(identity.sid)
