# -*- coding: utf-8 -*-
"""
pyserval.highlevel.gighlevel_keyring
~~~~~~~~~~~~~~~~

High level API for accessing the serval keyring
"""

import sys

from pyserval.lowlevel.keyring import Keyring


# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str


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
             EndpointNotImplementedException: Because it's actually not possible to do this
        """
        self._keyring.lock(self.sid)


class HighLevelKeyring:
    def __init__(self, connection):
        self.low_level_keyring = Keyring(connection)
