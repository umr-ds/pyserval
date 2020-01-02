"""
pyserval.lowlevel.rhizome
~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the means to interact with rhizome, the serval distributed file-store
"""

from pyserval.exceptions import JournalError, InvalidManifestError
from pyserval.lowlevel.connection import RestfulConnection


class Manifest:
    """Representation of a rhizome-bundle's manifest

    Args:
        id (str): Bundle ID - generated from Bundle Secret for new bundles
        version (int): Version of the bundle - a bundle with a higher version will replace
                       its old versions
                       May be specified manually, otherwise will be UNIX-timestamp of update
        filesize (int): Size (in bytes) of payload
        service (str): Name of service to be published under
        date (int): UNIX-Timestamp of bundle creation (is not changed by updates)
        filehash (str): If payload is not empty (filesize != 0), contains sha512 of payload
        tail (int): For journals: offset up to which content has been dropped
                    May be increased by updates to clear space in rhizome-store
        sender (str): SID of the bundle author
                      (optional unless the bundle is a MeshMS, or MeshMB ply)
        recipient (str): SID of the data recipient
                         (optional unless the bundle is a MeshMS, or MeshMB ply)
        name (str): Human-readable bundle name
        crypt (int): 1, if payload is encrypted, 0 otherwise
        bk (str): Bundle Key - Bundle secret encrypted with author's public key
                  Enable by setting 'bundle_author' in Rhizome.insert/append
        kwargs (str): Additional custom metadata
                    (See examples.rhizome for usage)
    """

    def __init__(
        self,
        id=None,
        version=None,
        filesize=None,
        service=None,
        date=None,
        filehash=None,
        tail=None,
        sender=None,
        recipient=None,
        name=None,
        crypt=None,
        BK=None,
        **kwargs
    ):
        self.id = id
        self.version = version
        self.filesize = filesize
        self.service = service
        self.date = date
        self.filehash = filehash
        self.tail = tail
        self.sender = sender
        self.recipient = recipient
        self.name = name
        self.crypt = crypt
        self.BK = BK
        self.__dict__.update(kwargs)

        self._types = {
            "version": int,
            "filesize": int,
            "date": int,
            "tail": int,
            "crypt": int,
        }

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, Manifest):
            return False

        # two manifests are equal, if all their fields (including custom fields) are equal
        for key, value in self.__dict__.items():
            try:
                if not other.__dict__[key] == value:
                    return False
            except KeyError:
                return False

        return True

    def fields(self):
        """Get List of (fieldname, value) tuples of all relevant manifest fields

        Returns:
            List[Tuple[str, Any]]: Fields which are not None
        """
        items = []
        for key, value in self.__dict__.items():
            if value is not None and not key.startswith("_"):
                items.append((key, value))

        return items

    def update(self, response_data):
        """Updates the Manifest with data from a Rhizome HTTP response

        Args:
            response_data (str): Manifest in text+binarysig format
            (https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md#textbinarysig-manifest-format)
        """
        pure_manifest = response_data.split("\0")[0]
        values = {}
        for line in pure_manifest.splitlines():
            key, value = line.split("=")
            value = self.autocast(key, value)
            values[key] = value

        self.__dict__.update(values)

    def update_manual(self, **kwargs):
        """Update the manifest's data

        Args:
            kwargs (Union[str, int]): names & updated values for the manifest
        """
        for key in kwargs:
            # Serval does not allow the '_'-character for custom fields,
            # but I don't know if there are any other restrictions - the documentation doesn't say
            # which is why I chose to restrict it to alphanumerics - to b on the safe side
            assert key.isalnum(), "Custom fields must be alphanumeric"

        self.__dict__.update(kwargs)

    def is_valid(self):
        """Checks whether the manifest is valid

        Raises:
            InvalidManifestError: If the manifest is invalid
        """
        if self.service:
            # apparently service names may only by alphanumeric
            # even though the documentation does not say so...
            if not self.service.isalnum():
                raise InvalidManifestError(
                    key="service",
                    value=str(self.service),
                    reason="Service must be alphanumeric",
                )
        return True

    def autocast(self, field_name, value):
        """Tries to automatically cast a string into another type
        Rhizome HTTP replies for manifests are always strings,
        but the underlying type might be different

        Checks the object's 'types'-dict to determine if the value should be cast to another type
        or left unchanged.

        Args:
            field_name (str): Name of the manifest field
            value (str): String returned by the serval rest-server

        Returns:
            Any: Possibly cast value
        """
        try:
            return self._types[field_name](value)
        except KeyError:
            return value


class LowLevelRhizome:
    """Interface to access Rhizome-related endpoints of the REST-interface

    Args:
        connection (connection.RestfulConnection): Used for HTTP-communication
    """

    def __init__(self, connection):
        assert isinstance(connection, RestfulConnection)
        self._connection = connection

    def get_manifests(self):
        """Returns list of all bundles stored in rhizome

        Endpoint:
            GET /restful/rhizome/bundlelist.json

        Returns:
            requests.models.Response: Response returned by the serval-server

        Note:
            This endpoint does NOT return the Bundle's payload, this must be queried separately
        """
        return self._connection.get("/restful/rhizome/bundlelist.json")

    def get_manifest_newsince(self, token):
        """Blocking call, returns first manifest after provided token, none on timeout.

        Endpoint:
            GET /restful/rhizome/newsince[/TOKEN]/bundlelist.json

        Returns:
            ...

        """

        return self._connection.get(
            "/restful/rhizome/newsince/{}/bundlelist.json".format(token), stream=True
        )

    def get_manifest(self, bid):
        """Gets the manifest for a specified BID

        Endpoint:
            GET /restful/rhizome/BID.rhm

        Args:
            bid (str): Bundle ID

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get("/restful/rhizome/{}.rhm".format(bid))

    def get_raw(self, bid):
        """Gets the raw payload of a bundle

        Endpoint:
            GET /restful/rhizome/BID/raw.bin

        Args:
            bid (str): Bundle ID

        Returns:
            requests.models.Response: Response returned by the serval-server

        Note:
            If the payload is encrypted, this method will return the ciphertext
        """
        return self._connection.get("/restful/rhizome/{}/raw.bin".format(bid))

    def get_decrypted(self, bid):
        """Gets the decrypted payload of a bundle

        Endpoint:
            GET /restful/rhizome/BID/decrypted.bin

        Args:
            bid (str): Bundle ID

        Returns:
            requests.models.Response: Response returned by the serval-server

        Note:
            If the payload is encrypted and the decryption key is known,
            the plaintext will be returned.

            If the payload is unencrypted, the plaintext will be returned

            If the payload is encrypted and the decryption key is unknown, the call will fail
        """
        return self._connection.get("/restful/rhizome/{}/decrypted.bin".format(bid))

    @staticmethod
    def _format_params(
        manifest, bundle_id="", bundle_author="", bundle_secret="", payload=""
    ):
        """Internal method to build parameters

        Takes bundle data and constructs parameters for POST-request

        Args:
            manifest (Manifest): Manifest of the bundle (may be partial)
            bundle_id (str): Bundle ID (same as manifest.id)
            bundle_author (str): SID of a local unlocked identity
                                 Setting this enables the 'bk' field in the manifest
            bundle_secret (str): Secret key used for bundle-signing
            payload (Any): Bundle payload

        Returns:
            List[Tuple[str, Any]]: Formatted parameters for POST-request
        """
        manifest.is_valid()

        params = []

        # add bundle-id, if present
        # if no id is given, a new will be created by pyserval
        if bundle_id:
            params.append(("bundle-id", bundle_id))

        # set SID bundle-author
        # if an identity is provided, the bundle-secret will be stored as part of the bundle
        # (encrypted by the SID's private key)
        # - note that this parameter mus come BEFORE the manifest
        if bundle_author:
            params.append(("bundle-author", bundle_author))

        if bundle_secret:
            params.append(("bundle-secret", bundle_secret))

        # marshall manifest
        manifest_header = ""

        for (key, value) in manifest.fields():
            # Emptystring or None should be ignored
            # The number 0 should be included
            if value or value == 0:
                manifest_header += "{}={}\n".format(key, value)

        params.append(
            (
                "manifest",
                (
                    "manifest1",
                    manifest_header,
                    'rhizome/manifest;format="text+binarysig"',
                ),
            )
        )

        params.append(("payload", ("file", payload)))

        return params

    def insert(
        self, manifest, bundle_id="", bundle_author="", bundle_secret="", payload=""
    ):
        """Inserts a bundle into rhizome

        See
        https://github.com/servalproject/pyserval-dna/blob/development/doc/REST-API-Rhizome.md#post-restfulrhizomeinsert
        for details

        Endpoint:
            POST /restful/rhizome/insert

        Args:
            manifest (Manifest): Manifest with new values; may be partial
            bundle_id (str): The Bundle ID of an existing bundle to update; 64 hexadecimal digits.
                             If a bundle with this id exists
                             and its secret is known or inferrable (see bundle_author),
                             the bundle will be updated.
            bundle_author (str): SID of a local identity.
                                 Supplying it will store an encrypted version of the bundle-secret
                                 in the 'BK' header
            bundle_secret (str): Secret key to sign the bundle. May be inferred BK is set
                                 and there is a matching, unlocked identity
            payload (Any): Optional new payload for the bundle

        Returns:
            requests.models.Response: Response returned by the serval-server

        Raises:
            JournalException: If the field manifest.tail is present
        """
        if manifest.tail is not None:
            raise JournalError(True)

        params = self._format_params(
            manifest=manifest,
            payload=payload,
            bundle_id=bundle_id,
            bundle_author=bundle_author,
            bundle_secret=bundle_secret,
        )

        return self._connection.post("/restful/rhizome/insert", files=params)

    def append(
        self, manifest, payload, bundle_id="", bundle_author="", bundle_secret=""
    ):
        """Appends data to a journal

        See
        https://github.com/servalproject/pyserval-dna/blob/development/doc/REST-API-Rhizome.md#post-restfulrhizomeappend
        for details

        Endpoint:
            POST /restful/rhizome/append

        Args:
            manifest (Manifest): Manifest with new values; may be partial
            bundle_id (str): The Bundle ID of an existing bundle to update; 64 hexadecimal digits.
                             If a bundle with this id exists and its secret is known or
                             inferrable (see bundle_author), the bundle will be updated.
            bundle_author (str): SID of a local identity.
                                 Supplying it will store an encrypted version of the bundle-secret
                                 in the 'BK' header
            bundle_secret (str): Secret key to sign the bundle. May be inferred BK is set
                                 and there is a matching, unlocked identity
            payload (Any): Optional new payload for the bundle

        Returns:
            requests.models.Response: Response returned by the serval-server

        Raises:
            JournalException: If the field manifest.tail is not present
        """
        if manifest.tail is None:
            raise JournalError(False)

        params = self._format_params(
            manifest=manifest,
            payload=payload,
            bundle_id=bundle_id,
            bundle_author=bundle_author,
            bundle_secret=bundle_secret,
        )

        return self._connection.post("/restful/rhizome/append", files=params)
