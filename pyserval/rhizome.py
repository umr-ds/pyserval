from pyserval.lowlevel.rhizome import LowLevelRhizome


class Bundle:
    """Representation of a Rhizome-bundle

    Args:
        rhizome (Rhizome): Interface-object to interact with the Rhizome REST-interface
        manifest (Manifest): Manifest for the bundle (may be partial)
        payload (Any): Payload of the bundle
                       (may be empty if bundle is not a journal)
        bundle_id (str): Bundle ID (same as manifest.id)
        bundle_author (str): SID of a local unlocked identity
                             Setting this enables the 'bk' field in the manifest
        bundle_secret (str): Secret key used for bundle-signing

    Note:
        If bundle_author is not set, then the bundle will be anonymous. In this case,
        the bundle_secret has to be saved, or else it will be impossible to update the bundle later.
        If bundle_author is set,
        then the bundle_secret will be encrypted by the identity's public key
        and stored in the 'bk' field.
        This allows the secret to be recovered if the identity's private key is accessible.
    """
    def __init__(self, rhizome,
                 manifest,
                 payload=None,
                 bundle_id="",
                 bundle_author="",
                 bundle_secret=""):
        self._rhizome = rhizome
        self.manifest = manifest
        self.payload = payload
        self.bundle_id = bundle_id
        self.bundle_author = bundle_author
        self.bundle_secret = bundle_secret

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def update(self):
        """Updates the bundle's content in rhizome"""

        # Remove filesize & hash so that they will be recomputed
        self.manifest.filesize = None
        self.manifest.filehash = None

        # remove version (will be reset with current timestamp)
        # TODO: Different ways to increase version
        self.manifest.version = None

        if self.manifest.tail is None:
            updated = self._rhizome.insert(manifest=self.manifest,
                                           payload=self.payload,
                                           bundle_id=self.bundle_id,
                                           bundle_author=self.bundle_author,
                                           bundle_secret=self.bundle_secret)
        else:
            updated = self._rhizome.append(manifest=self.manifest,
                                           payload=self.payload,
                                           bundle_id=self.bundle_id,
                                           bundle_author=self.bundle_author,
                                           bundle_secret=self.bundle_secret)

        self.__dict__.update(updated.__dict__)


class Rhizome:
    def __init__(self, low_level_rhizome):
        assert isinstance(low_level_rhizome, LowLevelRhizome)
        self.low_level_rhizome = low_level_rhizome

    def get_bundlelist(self):
        """"""
