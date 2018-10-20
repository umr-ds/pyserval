# -*- coding: utf-8 -*-
"""
pyserval.rhizome
~~~~~~~~~~~~~~~~

This module contains the means to interact with rhizome, the serval distributed file-store
"""

import sys
import copy
import json

from pyserval.lowlevel.rhizome import LowLevelRhizome, Manifest
from pyserval.lowlevel.util import decode_json_table
from pyserval.exceptions import ManifestNotFoundError, PayloadNotFoundError, UnknownRhizomeStatusError
from pyserval.exceptions import DecryptionError, DuplicateBundleException, RhizomeInsertionError
from pyserval.exceptions import InvalidTokenError, RhizomeHTTPStatusError
from pyserval.keyring import Keyring, ServalIdentity


# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str


BUNDLELIST_HEADER_SIZE = 157


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
        complete (bool): Whether this bundle is complete
                         If gotten via get_bundlelist, the manifest will be incomplete and there will be no payload
                         call 'refresh' before trying to do anything with it

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
        from_here=0,
        complete=False,
        token=None,
    ):
        self._rhizome = rhizome
        self.manifest = manifest
        self.payload = payload
        self.bundle_id = bundle_id
        self.bundle_author = bundle_author
        self.bundle_secret = bundle_secret
        self.from_here = from_here
        self.complete = complete
        self.token = token

    def __repr__(self):
        return "Bundle({})".format(repr(self.__dict__))

    def clone(self, name=None, service=None):
        """Creates a clone of the bundle in rhizome.
        
        Two clones share a payload but have different bundle ids. This is possible by choosing another name or service."""
        manifest_copy = copy.copy(self.manifest)
        
        manifest_copy.id = None
        manifest_copy.BK = None

        if name:
            manifest_copy.name = name
        if service:
            manifest_copy.service = service

        the_clone = self._rhizome.insert(
            manifest=manifest_copy,
            bundle_author=self.bundle_author,
        )

        return the_clone

    def update(self):
        """Updates the bundle's content in rhizome"""
        assert self.complete, "Pleas call 'refresh' before trying to update"

        # Remove filesize & hash so that they will be recomputed
        self.manifest.filesize = None
        self.manifest.filehash = None

        # remove version (will be reset with current timestamp)
        # TODO: Different ways to increase version
        self.manifest.version = None

        new_self = self._rhizome.insert(
            manifest=self.manifest,
            payload=self.payload,
            bundle_id=self.bundle_id,
            bundle_author=self.bundle_author,
            bundle_secret=self.bundle_secret
        )

        self.manifest = new_self.manifest

    def get_payload(self):
        """Get the bundle's payload from the rhizome store

        Returns:
            bytes: The bundle's payload
        """
        payload = self._rhizome.get_payload(self)
        self.payload = payload
        return payload

    def update_payload(self, payload):
        """Update the bundle's payload

        Args:
            payload (Union[str, bytes]): New payload
        """
        self.payload = payload
        self.update()

    def update_manifest(self, **kwargs):
        """Update the bundle's manifest's contents

        Args:
            kwargs (Union[str, int]): names & updated values for the manifest
        """
        self.manifest.__dict__.update(kwargs)
        self.update()

    def refresh(self):
        """Refresh the bundle's metadata & payload to be certain that we have the complete current state"""
        self.manifest = self._rhizome._get_manifest(self.bundle_id)
        self.get_payload()
        self.complete = True


class Journal:
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
            complete (bool): Whether this bundle is complete
                         If gotten via get_bundlelist, the manifest will be incomplete and there will be no payload
                         call 'refresh' before trying to do anything with it

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
        from_here=0,
        complete=False,
        token=None,
    ):
        self._rhizome = rhizome
        self.manifest = manifest
        self.payload = payload
        self.bundle_id = bundle_id
        self.bundle_author = bundle_author
        self.bundle_secret = bundle_secret
        self.from_here = from_here
        self.complete = complete
        self.token = token

    def __repr__(self):
        return "Journal({})".format(repr(self.__dict__))

    def get_payload(self):
        """Get the bundle's payload from the rhizome store

        Returns:
            str: The new payload
        """
        payload = self._rhizome.get_payload(self)
        self.payload = payload
        return payload

    def update(self, payload=None):
        """Updates the journal's content in the rhizome store

        Args:
            payload (Union[None, str, bytes]):

        Note:
            While for a normal bundle, the updated payload will replace the previos payload,
            for journals it will instead be appended
        """
        assert self.complete, "Pleas call 'refresh' before trying to update"

        # Remove filesize & hash as they will always be recomputed automatically
        self.manifest.filesize = None
        self.manifest.filehash = None

        # remove version (will be set to tail + filesize)
        self.manifest.version = None

        new_self = self._rhizome.append(
            manifest=self.manifest,
            bundle_id=self.bundle_id,
            bundle_author=self.bundle_author,
            bundle_secret=self.bundle_secret,
            payload=payload
        )

        self.manifest = new_self.manifest

    def append_payload(self, payload):
        """Append additional payload to the bundle

        Args:
            payload (Union[str, bytes]): Additional payload
        """
        self.update(payload=payload)
        # since payload is appended wen then need to get the new complete payload
        self.get_payload()

    def drop_payload(self, n_bytes):
        """Drop parts of the payload

        Args:
            n_bytes (int): Number of bytes to be dropped
        """
        # FIXME: This does not appear to do anything...
        self.manifest.tail += n_bytes
        self.update(payload="")
        # get new, shrunk payload
        self.get_payload()

    def refresh(self):
        """Refresh the bundle's metadata & payload to be certain that we have the complete current state"""
        self.manifest = self._rhizome._get_manifest(self.bundle_id)
        self.get_payload()
        self.complete = True


def _handle_bundle_error(serval_reply):
    """When the insert/append endpoint fails, check what exactly happened

    Args:
        serval_reply (requests.models.Response): Faulty response

    Raises:
        DuplicateBundleException: If the error occured because the bundle is a duplicate
        RhizomeInsertionError: If it's something else
    """
    reply_content = serval_reply.text

    if serval_reply.status_code == 200:
        manifest = Manifest()
        manifest.update(reply_content)
        raise DuplicateBundleException(bid=manifest.id)
    else:
        bundle_status = serval_reply.headers.get("Serval-Rhizome-Result-Bundle-Status-Code")
        bundle_message = serval_reply.headers.get("Serval-Rhizome-Result-Bundle-Status-Message")
        raise RhizomeInsertionError(
            http_status=serval_reply.status_code,
            bundle_status=bundle_status,
            bundle_message=bundle_message,
            response_text=reply_content
        )


class Rhizome:
    """Interface for interacting with the serval rhizome API

    Args:
        low_level_rhizome (LowLevelRhizome): Used to perform low level requests
        keyring (Keyring): Bundles can be associated with identities
    """
    def __init__(self, low_level_rhizome, keyring):
        assert isinstance(low_level_rhizome, LowLevelRhizome)
        assert isinstance(keyring, Keyring)
        self._low_level_rhizome = low_level_rhizome
        self._keyring = keyring

    def _parse_bundlelist(self, reply_json):
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
                    from_here=data['.fromhere'],
                    token=data['.token'],
                )
            else:
                new_bundle = Journal(
                    self,
                    manifest=manifest,
                    bundle_id=data['id'],
                    from_here=data['.fromhere'],
                    token=data['.token'],
                )

            if data['.author'] is not None:
                new_bundle.bundle_author = data['.author']

            bundles.append(new_bundle)

        return bundles

    def get_bundlelist(self):
        """Get list of all bundles in the rhizome store

        Returns:
            List[Union[Bundle, Journal]]
        """
        serval_reply = self._low_level_rhizome.get_manifests()
        reply_json= serval_reply.json()

        return self._parse_bundlelist(reply_json)

    def get_bundlelist_newsince(self, token):
        """Get list of the bundles added after a specific token

        Args:
            token (str): NewSince Token

        Returns:
            List[Union[Bundle, Journal]]

        Raises:
            InvalidTokenError: If the token is not found in serval
            RhizomeHTTPStatusError: If the HTTP status code is unknown 
        """
        with self._low_level_rhizome.get_manifest_newsince(token) as serval_stream:
            if serval_stream.status_code == 404:
                raise InvalidTokenError(token, serval_stream.reason)
            if serval_stream.status_code != 200:
                raise RhizomeHTTPStatusError(serval_stream)

            serval_reply_bytes = []
            lines = 0

            for c in serval_stream.iter_content():
                if c == b'\n': 
                    lines += 1

                serval_reply_bytes.append(c)
                
                if c == b']' and lines == 3 and len(serval_reply_bytes) > BUNDLELIST_HEADER_SIZE:
                    # complete json manually
                    serval_reply_bytes += [b'\n', b']', b'\n', b'}']
                    break
        
        serval_reply = b''.join(serval_reply_bytes)
        reply_json = json.loads(serval_reply)

        return self._parse_bundlelist(reply_json)

    def _get_manifest(self, bid):
        """Get only the manifest for a specific BID

        Args:
            bid (str): Bundle ID

        Returns:
            Manifest: Bundle's manifest

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

        return manifest

    def get_bundle(self, bid):
        """Get the bundle for a specific BID

        Args:
            bid (str): Bundle ID

        Returns:
            Union[Bundle, Journal]: Object containing all relevant data

        Raises:
            NoSuchIdentityException: If no bundle with the specified BID is available
        """
        manifest = self._get_manifest(bid)

        if manifest.tail is None:
            bundle = Bundle(
                self,
                manifest=manifest,
                bundle_id=manifest.id,
                complete=True
            )
        else:
            bundle = Journal(
                self,
                manifest=manifest,
                bundle_id=manifest.id,
                complete=True
            )

        bundle.get_payload()
        return bundle

    def get_payload(self, bundle, decode=False):
        """Get the payload for a bundle

        Args:
            bundle (Union[Bundle, Journal]): Bundle/Journal object
            decode (bool): Set, if payload is utf-8 encoded string (if your original payload was a string and not bytes)
                           If unset, returns raw bytes

        Returns:
            Union[bytes, str]: Payload of the bundle

        Note:
            For documentation on possible status code combinations, see
            https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md#get-restfulrhizomebidrawbin
        """
        assert isinstance(bundle, Bundle) or isinstance(bundle, Journal)

        if bundle.manifest.crypt == 1:
            serval_reply = self._low_level_rhizome.get_decrypted(bundle.bundle_id)

            if serval_reply.status_code == 200:
                if decode:
                    return serval_reply.text
                else:
                    return serval_reply.content

            elif serval_reply.status_code == 404:
                bundle_status = serval_reply.headers.get("Serval-Rhizome-Result-Bundle-Status-Code")
                payload_status = serval_reply.headers.get("Serval-Rhizome-Result-Payload-Status-Code")

                if bundle_status == '0':
                    raise ManifestNotFoundError(bid=bundle.bundle_id)
                elif bundle_status == '1' and payload_status == '1':
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
                if decode:
                    return serval_reply.text
                else:
                    return serval_reply.content

            elif serval_reply.status_code == 404:
                bundle_status = serval_reply.headers.get("Serval-Rhizome-Result-Bundle-Status-Code")
                payload_status = serval_reply.headers.get("Serval-Rhizome-Result-Payload-Status-Code")

                if bundle_status == '0':
                    raise ManifestNotFoundError(bid=bundle.bundle_id)
                elif bundle_status == '1' and payload_status == '1':
                    raise PayloadNotFoundError(bid=bundle.bundle_id)
                else:
                    raise UnknownRhizomeStatusError(
                        serval_response=serval_reply
                    )

        # if we don't recognise the status code combination, raise the appropriate error
        raise UnknownRhizomeStatusError(
            serval_response=serval_reply
        )

    def insert(
        self,
        manifest,
        bundle_id="",
        bundle_author="",
        bundle_secret="",
        payload=""
    ):
        """Creates/Updates a bundle

        Args:
            manifest (Manifest): Valid (partial) bundle manifest
            bundle_id (str): Optional BID - necessary if attempting to modify an existing bundle
            bundle_author (str): Optional SID for a local, unlocked identity
                                 When set, the bundle secret may be reconstructed later on
            bundle_secret (str): Optional Curve25519 private key, used to create an anonymous bundle
                                 Note that this will not be saved anywhere, you need to save it yourself
                                 or lose access to the bundle
            payload (Union[str, bytes]): Optional payload

        Returns:
            Bundle: New Bundle-object which contains the reply's data

        Note:
            Don't use for journals, use ''append'' instead
        """
        assert isinstance(manifest, Manifest)
        assert manifest.tail is None, "For journals, use ''append''"
        assert isinstance(payload, basestring) or isinstance(payload, bytes)

        serval_reply = self._low_level_rhizome.insert(
            manifest=manifest,
            bundle_id=bundle_id,
            bundle_author=bundle_author,
            bundle_secret=bundle_secret,
            payload=payload
        )

        if serval_reply.status_code == 201:
            manifest = Manifest()
            manifest.update(serval_reply.text)
            return Bundle(
                rhizome=self,
                manifest=manifest,
                bundle_id=manifest.id,
                bundle_author=bundle_author,
                bundle_secret=bundle_secret,
                from_here=2
            )
        else:
            _handle_bundle_error(serval_reply)

    def new_bundle(
        self,
        name="",
        payload="",
        identity=None,
        recipient="",
        service="",
        custom_manifest=None
    ):
        """Creates a new bundle

        Args:
            name (str): Human readable name for the bundle
            payload (Union[str, bytes]): Initial payload
            identity (ServalIdentity): If set, then this identity's SID will be set as the bundle author
                                       If unset, the keyring's default identity will be used
            recipient (str): Optional SID of the bundle's recipient
                             If unset, bundle will be public and readable by anyone
                             If set, bundle will be encrypted
            service (str): (Optional) Service this bundle belongs to
            custom_manifest (Union[None, Dictionary[str, str]): A dictionary whose key-value pairs will be added
                                                                as custom fields in the new bundle's manifest

        Returns:
            Bundle: New Bundle-object containing all relevant data
        """
        assert isinstance(name, basestring)
        assert isinstance(payload, basestring) or isinstance(payload, bytes)

        if identity is None:
            identity = self._keyring.default_identity()

        assert isinstance(identity, ServalIdentity)
        assert isinstance(recipient, basestring)
        assert isinstance(service, basestring)
        assert custom_manifest is None or isinstance(custom_manifest, dict)

        if recipient:
            encryption = 1
        else:
            encryption = 0

        manifest = Manifest(
            name=name,
            service=service,
            sender=identity.sid,
            recipient=recipient,
            crypt=encryption
        )

        if custom_manifest:
            manifest.__dict__.update(custom_manifest)

        bundle_author = identity.sid

        new_bundle = self.insert(
            manifest=manifest,
            bundle_author=bundle_author,
            payload=payload,
        )

        new_bundle.payload = payload
        new_bundle.complete = True

        return new_bundle

    def append(
        self,
        manifest,
        bundle_id="",
        bundle_author="",
        bundle_secret="",
        payload=""
    ):
        """Creates/updates a journal

        Args:
            manifest (Manifest): Valid (partial) bundle manifest
            bundle_id (str): Optional BID - necessary if attempting to modify an existing bundle
            bundle_author (str): Optional SID for a local, unlocked identity
                                 When set, the bundle secret may be reconstructed later on
            bundle_secret (str): Optional Curve25519 private key, used to create an anonymous bundle
                                 Note that this will not be saved anywhere, you need to save it yourself
                                 or lose access to the bundle
            payload (Union[str, bytes]): Optional payload

        Note:
            Don't use for plain bundles, use ''insert'' instead
        """
        assert isinstance(manifest, Manifest)
        assert manifest.tail is not None, "For plain bundles, use ''insert''"
        assert isinstance(payload, basestring) or isinstance(payload, bytes)

        serval_reply = self._low_level_rhizome.append(
            manifest=manifest,
            bundle_id=bundle_id,
            bundle_author=bundle_author,
            bundle_secret=bundle_secret,
            payload=payload
        )
        reply_content = serval_reply.text

        if serval_reply.status_code == 201:
            manifest = Manifest()
            manifest.update(reply_content)
            return Journal(
                rhizome=self,
                manifest=manifest,
                bundle_id=manifest.id,
                bundle_author=bundle_author,
                bundle_secret=bundle_secret,
                from_here=2
            )
        else:
            _handle_bundle_error(serval_reply)

    def new_journal(
        self,
        name="",
        payload="",
        identity=None,
        recipient="",
        service="",
        custom_manifest=None
    ):
        """Creates a new journal

        Args:
            payload (Union[str, bytes]): Initial payload - must be non-empty
            name (str): Human readable name for the journal
            identity (ServalIdentity): If set, then this identity's SID will be set as the journal author
                                       If unset, the keyring's default identity will be used
            recipient (str): Optional SID of the bundle's recipient
                             If unset, bundle will be public and readable by anyone
                             If set, bundle will be encrypted
            service (str): (Optional) Service this journal belongs to
            custom_manifest (Union[None, Dictionary[str, str]): A dictionary whose key-value pairs will be added
                                                                as custom fields in the new bundle's manifest

        Returns:
            Journal: New journal object containing all relevant data
        """
        # TODO: this is also very similar to new_bundle - refactor and extract common components
        assert isinstance(name, basestring)
        assert isinstance(payload, basestring) or isinstance(payload, bytes)

        if identity is None:
            identity = self._keyring.default_identity()

        assert isinstance(identity, ServalIdentity)
        assert isinstance(recipient, basestring)
        assert isinstance(service, basestring)
        assert custom_manifest is None or isinstance(custom_manifest, dict)

        if recipient:
            encryption = 1
        else:
            encryption = 0

        manifest = Manifest(
            name=name,
            service=service,
            sender=identity.sid,
            recipient=recipient,
            crypt=encryption,
            tail=0
        )

        if custom_manifest:
            manifest.__dict__.update(custom_manifest)

        bundle_author = identity.sid

        new_journal = self.append(
            manifest=manifest,
            bundle_author=bundle_author,
            payload=payload
        )

        new_journal.payload = payload
        new_journal.complete = True

        return new_journal
