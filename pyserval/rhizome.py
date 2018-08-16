# -*- coding: utf-8 -*-
"""
pyserval.rhizome
~~~~~~~~~~~~~~~~

This module contains the means to interact with rhizome, the serval distributed file-store
"""

from pyserval.lowlevel.rhizome import LowLevelRhizome, Manifest
from pyserval.lowlevel.util import decode_json_table


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
        """Get the bundle's payload from the rhizome store"""

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
        self.low_level_rhizome = low_level_rhizome

    def get_bundlelist(self):
        """Get list of all bundles in the rhizome store

        Returns:
            List[Union[Bundle, Journal]]
        """
        serval_reply = self.low_level_rhizome.get_manifests()
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
