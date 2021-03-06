"""
pyserval.keyring
~~~~~~~~~~~~~~~~

High level API for accessing the serval keyring
"""

from pyserval.exceptions import IdentityNotFoundError, MalformedRequestError
from pyserval.lowlevel.keyring import LowLevelKeyring
from pyserval.lowlevel.util import unmarshall
from typing import Any, List


class ServalIdentity:
    """Representation of an identity in the serval keyring

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

    def __init__(
        self, _keyring, sid: str, identity: str = "", did: str = "", name: str = ""
    ) -> None:
        if did is None:
            did = ""
        if name is None:
            name = ""

        assert isinstance(_keyring, Keyring), "_keyring must be a HighLevelKeyring"
        assert isinstance(sid, str), "sid must be a string"
        assert isinstance(did, str), "did must be a string"
        assert isinstance(name, str), "name must be a string"

        self._keyring = _keyring
        self.sid = sid
        self.did = did
        self.name = name
        self.identity = identity

    def __repr__(self) -> str:
        return f'ServalIdentity(sid="{self.sid}", did="{self.did}", name="{self.name}")'

    def __str__(self) -> str:
        if self.name or self.did:
            return f"(Name: {self.name}, DID: {self.did})"
        else:
            return f"{self.sid[:16]}*"

    def __eq__(self, other: Any) -> bool:
        if not type(other) == type(self):
            return False
        return (
            self.sid == other.sid
            and self.did == other.did
            and self.name == other.name
            and self.identity == other.identity
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def refresh(self) -> None:
        """Refreshes Information for the Identity

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        refreshed = self._keyring.get_identity(sid=self.sid)
        self.__dict__.update(refreshed.__dict__)

    def set(self, did: str = "", name: str = "") -> None:
        """Sets the DID and/or name of this identity

        Args:
            did (str): Sets the DID (phone number);
                       must be a string of five or more digits from the set 123456789#0*
            name (str): Sets the name; must be non-empty

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        assert isinstance(did, str), "did must be a string"
        assert isinstance(name, str), "name must be a string"

        # make sure that we have the current state
        self.refresh()

        self._keyring.set(identity=self, did=did, name=name)
        self.did = did
        self.name = name

    def delete(self) -> None:
        """Removes this Identity from the Keyring

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        self._keyring.delete(identity=self)

    def lock(self) -> None:
        """Locks this identity - can be unlocked again with its pin

        Raises:
            NoSuchIdentityException: If this identity is no longer available
        """
        self._keyring.lock(identity=self)


class Keyring:
    """High-level interface to interact with the serval keyring

    Args:
        low_level_keyring (LowLevelKeyring): Instance of the LowLevelKeyring used to perform the basic requests
    """

    def __init__(self, low_level_keyring: LowLevelKeyring) -> None:
        assert isinstance(low_level_keyring, LowLevelKeyring)
        self.low_level_keyring = low_level_keyring

    def add(self, pin: str = "", did: str = "", name: str = "") -> ServalIdentity:
        """Creates a new identity with a random SID

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

        Raises:
            MalformedRequestError: If arguments are invalid values
        """
        serval_reply = self.low_level_keyring.add(pin=pin, did=did, name=name)

        if serval_reply.status_code == 400:
            raise MalformedRequestError()

        reply_json = serval_reply.json()
        return ServalIdentity(self, **reply_json["identity"])

    def get_identities(self, pin: str = "") -> List[ServalIdentity]:
        """List of all currently unlocked identities

        Args:
            pin (str): Passphrase to unlock identity prior to lookup

        Returns:
            List[ServalIdentity]: All currently unlocked identities
        """
        serval_response = self.low_level_keyring.get_identities(pin=pin)
        response_json = serval_response.json()

        identities = unmarshall(
            json_table=response_json, object_class=ServalIdentity, _keyring=self
        )

        return identities

    def get_identity(self, sid: str, pin: str = "") -> ServalIdentity:
        """Gets the identity for a given sid

        Args:
            sid (str): SID of the requested identity
            pin (str): Passphrase to unlock identity prior to lookup

        Returns:
            ServalIdentity: Identity-information associated with the given SID

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available
        """
        assert isinstance(sid, str), "sid must be a string"

        serval_response = self.low_level_keyring.get_identity(sid=sid, pin=pin)

        if serval_response.status_code == 404:
            raise IdentityNotFoundError(sid)

        response_json = serval_response.json()

        return ServalIdentity(self, **response_json["identity"])

    def get_or_create(self, n: int) -> List[ServalIdentity]:
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

    def default_identity(self) -> ServalIdentity:
        """Returns the first unlocked identity (or creates one, if none exist)

        Returns:
            ServalIdentity: First unlocked (or created) identity
        """
        return self.get_or_create(1)[0]

    def delete(self, identity: ServalIdentity, pin: str = "") -> ServalIdentity:
        """Removes an existing identity

        Args:
            identity (ServalIdentity): Identity to be removed
            pin (str): Passphrase to unlock identity prior to deletion

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
            ServalIdentity: Object of the deleted identity if successful
        """
        serval_response = self.low_level_keyring.delete(sid=identity.sid, pin=pin)

        if serval_response.status_code == 404:
            raise IdentityNotFoundError(identity.sid)

        reply_json = serval_response.json()
        return ServalIdentity(self, **reply_json["identity"])

    def set(
        self, identity: ServalIdentity, pin: str = "", did: str = "", name: str = ""
    ) -> ServalIdentity:
        """Sets the DID and/or name of an unlocked identity

        Args:
            identity (ServalIdentity): Identity to be updated (required)
            pin (str): Passphrase to unlock identity prior to modification
            did (str): sets the DID (phone number)
                       String of 5-31 digits from 0123456789#*
            name (str): sets the name (optional)
                        String of at most 63 utf-8 bytes, may not include non-printable characters
                        may not start or end with a whitespace

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
             ServalIdentity: Object of the updated identity if successful
        """
        assert isinstance(identity, ServalIdentity), "identity must be a ServalIdentity"
        assert isinstance(pin, str), "PIN must be a string"
        assert isinstance(did, str), "did must be a string"
        assert isinstance(name, str), "name must be a string"

        # If you want to reset did and/or name, use the reset-method
        if not len(did):
            did = None
        if not len(name):
            name = None

        serval_response = self.low_level_keyring.set(
            sid=identity.sid, pin=pin, did=did, name=name
        )

        if serval_response.status_code == 404:
            raise IdentityNotFoundError(identity.sid)

        response_json = serval_response.json()

        return ServalIdentity(self, **response_json["identity"])

    def reset(
        self,
        identity: ServalIdentity,
        pin: str = "",
        did: bool = False,
        name: bool = False,
    ) -> ServalIdentity:
        """Reset Name and/or DID of an identity

        Args:
            identity (ServalIdentity): Identity to be updated (required)
            pin (str): Passphrase to unlock identity prior to modification
            did (bool): Whether the DID should be reset
            name (bool): Whether the Name should be reset

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available

        Returns:
             ServalIdentity: Object of the updated identity if successful
        """
        assert isinstance(identity, ServalIdentity), "identity must be a ServalIdentity"
        assert isinstance(pin, str), "PIN must be a string"
        assert isinstance(did, bool), "did must be a boolean"
        assert isinstance(name, bool), "name must be a boolean"

        if did:
            did = ""
        else:
            did = None

        if name:
            name = ""
        else:
            name = None

        serval_response = self.low_level_keyring.set(
            sid=identity.sid, pin=pin, did=did, name=name
        )

        if serval_response.status_code == 404:
            raise IdentityNotFoundError(identity.sid)

        response_json = serval_response.json()

        return ServalIdentity(self, **response_json["identity"])

    def lock(self, identity: ServalIdentity) -> ServalIdentity:
        """Locks an identity - you will need the pin to unlock it again

        Args:
            identity (ServalIdentity): Identity to be locked

        Raises:
            NoSuchIdentityException: If no identity with the specified SID is available
        """
        serval_response = self.low_level_keyring.lock(identity.sid)

        if serval_response.status_code == 404:
            raise IdentityNotFoundError(identity.sid)

        response_json = serval_response.json()

        return ServalIdentity(self, **response_json["identity"])
