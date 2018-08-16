# -*- coding: utf-8 -*-
"""
pyserval.rhizome
~~~~~~~~~~~~~~~~

This module contains the means to interact with rhizome, the serval distributed file-store
"""

import sys

from pyserval.lowlevel.rhizome import LowLevelRhizome, Manifest
from pyserval.lowlevel.util import decode_json_table
from pyserval.exceptions import ManifestNotFoundError, PayloadNotFoundError, UnknownRhizomeStatusError
from pyserval.exceptions import DecryptionError


# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str


class Bundle:
    """Representation of a (non-journal) Rhizome-bundle

    Args:
        rhizome (Rhizome): Interface-object to interact with the Rhizome REST-interface
        manifest (Manifest): Manifest for the bundle (may be partial)
        payload (Any): Payload of the bundle
                       (may be empty if bundle is not a journal)
        bundle_id (str): Bundle ID (same as manifest.id)
        bundle_author (str): SID of a local unlocked identity
                             Setting this enables the 'bk' field in the manifest
        bundle_secret (str): Secret key used for bundle-signing
        from_here (int): Whether the bundle has been authored on this device

    Note:
        If bundle_author is not set, then the bundle will be anonymous. In this case,
        the bundle_secret has to be saved, or else it will be impossible to update the bundle later.
        If bundle_author is set,
        then the bundle_secret will be encrypted by the identity's public key
        and stored in the 'bk' field.
        This allows the secret to be recovered if the identity's private key is accessible.
    """
    def __init__(
        self,
        rhizome,
        manifest,
        payload=None,
        bundle_id="",
        bundle_author="",
        bundle_secret="",
        from_here=0
    ):
        self._rhizome = rhizome
        self.manifest = manifest
        self.payload = payload
        self.bundle_id = bundle_id
        self.bundle_author = bundle_author
        self.bundle_secret = bundle_secret
        self.from_here = from_here

    def __repr__(self):
        return "Bundle({})".format(repr(self.__dict__))

    def update(self):
        """Updates the bundle's content in rhizome"""

        # Remove filesize & hash so that they will be recomputed
        self.manifest.filesize = None
        self.manifest.filehash = None

        # remove version (will be reset with current timestamp)
        # TODO: Different ways to increase version
        self.manifest.version = None

        # TODO: Update payload in rhizome store
        # TODO: Update local state

    def get_payload(self):
        """Get the bundle's payload from the rhizome store

        Returns:
            str: The new payload
        """
        payload = self._rhizome.get_payload(self)
        self.payload = payload
        return payload

    def update_payload(self):
        """Update the bundle's payload"""


class Journal(Bundle):
    """Representation of a Journal

        Args:
            rhizome (Rhizome): Interface-object to interact with the Rhizome REST-interface
            manifest (Manifest): Manifest for the bundle (may be partial)
            payload (Any): Payload of the bundle
                           (may be empty if bundle is not a journal)
            bundle_id (str): Bundle ID (same as manifest.id)
            bundle_author (str): SID of a local unlocked identity
                                 Setting this enables the 'bk' field in the manifest
            bundle_secret (str): Secret key used for bundle-signing
            from_here (int): Whether the bundle has been authored on this device

        Note:
            If bundle_author is not set, then the bundle will be anonymous. In this case,
            the bundle_secret has to be saved, or else it will be impossible to update the bundle later.
            If bundle_author is set,
            then the bundle_secret will be encrypted by the identity's public key
            and stored in the 'bk' field.
            This allows the secret to be recovered if the identity's private key is accessible.
        """
    def __init__(
        self,
        rhizome,
        manifest,
        payload=None,
        bundle_id="",
        bundle_author="",
        bundle_secret="",
        from_here=0
    ):
        Bundle.__init__(
            self,
            rhizome=rhizome,
            manifest=manifest,
            payload=payload,
            bundle_id=bundle_id,
            bundle_author=bundle_author,
            bundle_secret=bundle_secret,
            from_here=from_here
        )

    def __repr__(self):
        return "Journal({})".format(repr(self.__dict__))

    def update(self):
        """Updates the journal's content in the rhizome store"""

        # Remove filesize & hash so that they will be recomputed
        self.manifest.filesize = None
        self.manifest.filehash = None

        # remove version (will be reset with current timestamp)
        # TODO: Different ways to increase version
        self.manifest.version = None

        # TODO: Update payload in rhizome store
        # TODO: Update local state


class Rhizome:
    def __init__(self, low_level_rhizome):
        assert isinstance(low_level_rhizome, LowLevelRhizome)
        self._low_level_rhizome = low_level_rhizome

    def get_bundlelist(self):
        """Get list of all bundles in the rhizome store

        Returns:
            List[Union[Bundle, Journal]]
        """
        serval_reply = self._low_level_rhizome.get_manifests()
        reply_json = serval_reply.json()

        bundle_data = decode_json_table(reply_json)
        bundles = []

        for data in bundle_data:
            manifest = Manifest()
            # take only those values from data which belong into the manifest
            manifest_data = {
                key: value for (key, value) in data.items() if key in manifest.__dict__.keys()
            }

            manifest.__dict__.update(**manifest_data)

            if manifest.tail is None:
                new_bundle = Bundle(
                    self,
                    manifest=manifest,
                    bundle_id=data['id'],
                    from_here=data['.fromhere']
                )
            else:
                new_bundle = Journal(
                    self,
                    manifest=manifest,
                    bundle_id=data['id'],
                    from_here=data['.fromhere']
                )

            if data['.author'] is not None:
                new_bundle.bundle_author = data['.author']

            bundles.append(new_bundle)

        return bundles

    def get_bundle(self, bid):
        """Get the bundle for a specific BID

        Args:
            bid (str): Bundle ID

        Returns:
            Union[Bundle, Journal]):

        Raises:
            NoSuchIdentityException: If no bundle with the specified BID is available
        """
        assert isinstance(bid, basestring)

        serval_reply = self._low_level_rhizome.get_manifest(bid=bid)

        if serval_reply.status_code == 404:
            raise ManifestNotFoundError(bid)

        reply_text = serval_reply.text

        manifest = Manifest()
        manifest.update(reply_text)

        if manifest.tail is None:
            return Bundle(
                self,
                manifest=manifest
            )
        else:
            return Journal(
                self,
                manifest=manifest
            )

    def get_payload(self, bundle):
        """Get the payload for a bundle

        Args:
            bundle (Union[Bundle, Journal]): Bundle/Journal object

        Returns:
            str: Payload of the bundle

        Note:
            For documentation on possible status code combinations, see
            https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md#get-restfulrhizomebidrawbin
        """
        assert isinstance(bundle, Bundle)

        if bundle.manifest.crypt == 1:
            serval_reply = self._low_level_rhizome.get_decrypted(bundle.bundle_id)

            if serval_reply.status_code == 200:
                return serval_reply.text

            elif serval_reply.status_code == 404:
                bundle_status = serval_reply.headers.get("Serval-Rhizome-Result-Bundle-Status-Code")
                payload_status = serval_reply.headers.get("Serval-Rhizome-Result-Payload-Status-Code")

                if bundle_status == 0:
                    raise ManifestNotFoundError(bid=bundle.bundle_id)

                elif bundle_status == 1 and payload_status == 1:
                    raise PayloadNotFoundError(bid=bundle.bundle_id)

                else:
                    raise UnknownRhizomeStatusError(
                        serval_response=serval_reply
                    )

            elif serval_reply.status_code == 419:
                raise DecryptionError(bid=bundle.bundle_id)

        else:
            serval_reply = self._low_level_rhizome.get_raw(bundle.bundle_id)

            if serval_reply.status_code == 200:
                return serval_reply.text

            elif serval_reply.status_code == 404:
                bundle_status = serval_reply.headers.get("Serval-Rhizome-Result-Bundle-Status-Code")
                payload_status = serval_reply.headers.get("Serval-Rhizome-Result-Payload-Status-Code")
                if bundle_status == 0:
                    raise ManifestNotFoundError(bid=bundle.bundle_id)
                elif bundle_status == 1 and payload_status == 1:
                    raise PayloadNotFoundError(bid=bundle.bundle_id)
                else:
                    raise UnknownRhizomeStatusError(
                        serval_response=serval_reply
                    )

        # if we don't recognise the status code combination, raise the appropriate error
        raise UnknownRhizomeStatusError(
            serval_response=serval_reply
        )
