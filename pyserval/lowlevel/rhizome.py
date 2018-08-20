# -*- coding: utf-8 -*-
"""
pyserval.lowlevel.rhizome
~~~~~~~~~~~~~~~~

This module contains the means to interact with rhizome, the serval distributed file-store
"""

import sys

from pyserval.exceptions import JournalError
from pyserval.lowlevel.util import autocast


# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str


class Manifest:
    """Representation of a rhizome-bundle's manifest

    Args:
        id (str): Bundle ID - generated from Bundle Secret for new bundles
        version (int): Version of the bundle - a bundle with a higher version will replace
                       its old versions
                       May be specified manually, otherwise will be UNIX-timestamp of update
        filsize (int): Size (in bytes) of payload
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
    def __init__(self,
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
                 **kwargs):
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

    def __repr__(self):
        return str(self.__dict__)

    def __dir__(self):
        """Called by dir()

        Returns:
            List[Tuple[str, Any]]: Fields which are not None
        """
        items = []
        for key, value in self.__dict__.items():
            if value is not None:
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
            value = autocast(value)
            values[key] = value

        self.__dict__.update(values)

    def is_valid(self):
        """Checks whether the manifest is valid

        Returns:
            bool: True if valid, False otherwise
        """
        # TODO: implement


class LowLevelRhizome:
    """Interface to access Rhizome-related endpoints of the REST-interface

    Args:
        connection (connection.RestfulConnection): Used for HTTP-communication
    """
    def __init__(self, connection):
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
    def _format_params(manifest,
                       bundle_id="",
                       bundle_author="",
                       bundle_secret="",
                       payload=""):
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

        for (key, value) in dir(manifest):
            if value:
                manifest_header += "{}={}\n".format(key, value)

        params.append(
            (
                "manifest",
                ("manifest1", manifest_header, "rhizome/manifest;format=\"text+binarysig\"")
            )
        )

        params.append(("payload", ("file1", payload)))

        return params

    def insert(self, manifest,
               bundle_id="",
               bundle_author="",
               bundle_secret="",
               payload=""):
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

        params = self._format_params(manifest=manifest,
                                     payload=payload,
                                     bundle_id=bundle_id,
                                     bundle_author=bundle_author,
                                     bundle_secret=bundle_secret)

        return self._connection.post("/restful/rhizome/insert", files=params)

    def append(self, manifest,
               payload,
               bundle_id="",
               bundle_author="",
               bundle_secret=""):
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

        params = self._format_params(manifest=manifest,
                                     payload=payload,
                                     bundle_id=bundle_id,
                                     bundle_author=bundle_author,
                                     bundle_secret=bundle_secret)

        return self._connection.post("/restful/rhizome/append", files=params)
